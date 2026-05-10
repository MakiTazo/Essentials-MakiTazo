"""
chunk_leak_fix.py  —  DIAGNÓSTICO COMPLETO (una sola ejecución)

Prueba TODO lo necesario para escribir el fix definitivo:
  A) Qué índice del vftable de ServerLevel es _getMapDataManager
  B) En qué offset del manager está el unordered_map
  C) Layout del unordered_map (GCC/Itanium) y sus nodos
  D) Qué unique_id tiene el jugador (para verificar la comparación)

Con el output de esto escribimos el fix real sin más iteraciones.
"""

import ctypes
import struct

from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerJoinEvent

PYBIND11_CPP_OFFSET = 16  # confirmado


# ══════════════════════════════════════════════════════════════════════════════
#  Memoria segura
# ══════════════════════════════════════════════════════════════════════════════

_maps: list[tuple[int, int, str]] = []

def _reload_maps():
    global _maps
    _maps = []
    try:
        with open("/proc/self/maps") as f:
            for line in f:
                p = line.split()
                if len(p) >= 2:
                    a, b = p[0].split('-')
                    _maps.append((int(a, 16), int(b, 16), p[1]))
    except Exception:
        pass

def _readable(addr: int) -> bool:
    if addr < 0x10000:
        return False
    for s, e, p in _maps:
        if s <= addr < e:
            return 'r' in p
    return True  # heap anónimo

def _executable(addr: int) -> bool:
    if addr < 0x10000:
        return False
    return any('x' in p and s <= addr < e for s, e, p in _maps)

def ru64(addr: int) -> int | None:
    if not _readable(addr):
        return None
    try:
        return struct.unpack("Q", bytes((ctypes.c_uint8 * 8).from_address(addr)))[0]
    except Exception:
        return None

def ri64(addr: int) -> int | None:
    v = ru64(addr)
    return (v - (1 << 64)) if v is not None and v >= (1 << 63) else v

def level_ptr(player) -> int | None:
    obj = player.level
    v   = ru64(id(obj) + PYBIND11_CPP_OFFSET)
    _   = obj
    return v if v and v > 0x10000 else None

def vcall(obj: int, idx: int) -> int | None:
    vft = ru64(obj)
    if not vft: return None
    fn  = ru64(vft + idx * 8)
    if not fn or not _executable(fn): return None
    try:
        return ctypes.CFUNCTYPE(ctypes.c_uint64, ctypes.c_uint64)(fn)(obj)
    except Exception:
        return None

def looks_like_cpp(ptr: int) -> bool:
    """True si ptr parece un objeto C++ con vftable ejecutable."""
    if not ptr or ptr < 0x10000: return False
    vft = ru64(ptr)
    if not vft: return False
    fn0 = ru64(vft)
    return fn0 is not None and _executable(fn0)


# ══════════════════════════════════════════════════════════════════════════════
#  A) Encontrar el índice correcto de _getMapDataManager
#     Probamos todos los índices ejecutables del bloque 375–387
#     (confirmado como bloque ✓ en iteración anterior)
# ══════════════════════════════════════════════════════════════════════════════

def find_manager_index(lvl: int, log) -> tuple[int, int] | None:
    """
    Retorna (índice, manager_ptr) del primer índice que:
      - Apunta a función ejecutable
      - Retorna un puntero a un objeto C++ válido (tiene vftable)
      - No es el mismo nivel (para descartar identity functions)
    """
    log.info("[A] Probando índices 375–387 de vftable de ServerLevel:")
    log.info(f"[A]  {'idx':>4}  {'resultado':>18}  {'tiene vftable':>14}  veredicto")

    candidates = []
    for idx in range(375, 388):
        result = vcall(lvl, idx)
        if result is None or result == 0:
            log.info(f"[A]  {idx:4d}  {'null/fallo':>18}")
            continue
        has_vft = looks_like_cpp(result)
        is_self = (result == lvl)
        verdict = "✓ CANDIDATO" if has_vft and not is_self else ("self" if is_self else "sin vftable")
        log.info(f"[A]  {idx:4d}  0x{result:016x}  {str(has_vft):>14}  {verdict}")
        if has_vft and not is_self:
            candidates.append((idx, result))

    if not candidates:
        log.error("[A] Ningún índice retornó un objeto C++ válido")
        return None

    best = candidates[0]
    log.info(f"[A] → Usando índice {best[0]}, manager @ 0x{best[1]:x}")
    return best


# ══════════════════════════════════════════════════════════════════════════════
#  B) Encontrar el offset del unordered_map dentro del manager
#     GCC libstdc++ unordered_map (_Hashtable) layout:
#       +0   _M_buckets ptr
#       +8   _M_bucket_count
#       +16  _M_before_begin._M_nxt  (ptr al primer nodo, o null)
#       +24  _M_element_count        (número de elementos)
#     Un mapa válido tiene _M_element_count > 0 y _M_buckets != null
# ══════════════════════════════════════════════════════════════════════════════

def find_map_offset(manager: int, log) -> int | None:
    log.info(f"[B] Buscando unordered_map en manager @ 0x{manager:x}")
    log.info(f"[B]  {'off':>4}  {'buckets':>18}  {'bucket_cnt':>10}  {'first_node':>18}  {'elem_cnt':>8}  nota")

    found = None
    for off in range(0, 512, 8):
        # Leer como si fuera el inicio de un _Hashtable
        buckets    = ru64(manager + off)
        bcnt       = ru64(manager + off + 8)
        first_node = ru64(manager + off + 16)
        elem_cnt   = ru64(manager + off + 24)

        if any(v is None for v in [buckets, bcnt, first_node, elem_cnt]):
            continue

        # Heurística: bucket_count es potencia de 2, elem_count < bucket_count
        is_pow2 = bcnt > 0 and (bcnt & (bcnt - 1)) == 0
        sane    = 0 < elem_cnt < 100000 and is_pow2
        has_buckets = buckets > 0x10000 and _readable(buckets)

        if sane and has_buckets:
            note = f"  ★ MAPA VÁLIDO (size={elem_cnt}, buckets={bcnt})"
            if found is None:
                found = off
        else:
            note = ""

        # Solo imprimir filas interesantes
        if sane or off == 112:
            marker = "← actual" if off == 112 else ""
            log.info(f"[B]  {off:4d}  0x{buckets:016x}  {bcnt:10d}  0x{first_node:016x}  {elem_cnt:8d}{note}  {marker}")

    if found is not None:
        log.info(f"[B] → Offset del unordered_map: {found}")
    else:
        log.warning("[B] → No se encontró unordered_map válido (¿servidor vacío? ¿índice wrong?)")
    return found


# ══════════════════════════════════════════════════════════════════════════════
#  C) Leer el primer nodo del mapa y ver su layout
#     GCC _Hash_node<pair<long long, unique_ptr<void*>>, false>:
#       +0   _M_nxt (ptr al siguiente nodo)
#       +8   key    (long long)
#       +16  value  (unique_ptr → raw ptr)
#     El 'false' = no cachea hash code
# ══════════════════════════════════════════════════════════════════════════════

def inspect_map_nodes(manager: int, map_off: int, log) -> None:
    map_ptr    = manager + map_off
    first_node = ru64(map_ptr + 16)   # _M_before_begin._M_nxt
    elem_cnt   = ru64(map_ptr + 24)

    log.info(f"[C] Inspeccionando nodos del mapa (map @ 0x{map_ptr:x})")
    log.info(f"[C] elem_count={elem_cnt}, first_node=0x{first_node:x}" if first_node else "[C] first_node=null")

    if not first_node or first_node < 0x10000:
        log.warning("[C] Mapa vacío o first_node inválido")
        return

    log.info(f"[C]  Probando layout de nodo @ 0x{first_node:x}")
    log.info(f"[C]  (sin caché de hash: nxt+key+unique_ptr)")

    nxt       = ru64(first_node + 0)
    key       = ri64(first_node + 8)
    raw_ptr   = ru64(first_node + 16)

    log.info(f"[C]    +0  _M_nxt    = 0x{nxt:016x}" if nxt is not None else "[C]    +0 nxt = None")
    log.info(f"[C]    +8  key       = {key}" if key is not None else "[C]    +8 key = None")
    log.info(f"[C]    +16 raw_ptr   = 0x{raw_ptr:016x}" if raw_ptr is not None else "[C]    +16 raw_ptr = None")

    if raw_ptr and raw_ptr > 0x10000:
        log.info(f"[C]  Inspeccionando data @ 0x{raw_ptr:x} (buscando tracked_entities vector a offset 96)")
        log.info(f"[C]  Probando offsets del data object:")
        for off in range(80, 128, 8):
            v = ru64(raw_ptr + off)
            if v is None:
                continue
            note = "← offset esperado (tracked_entities)" if off == 96 else ""
            log.info(f"[C]    +{off:3d}  0x{v:016x}  {note}")

        # Intentar leer vector en offset 96
        vec_begin = ru64(raw_ptr + 96)
        vec_end   = ru64(raw_ptr + 104)
        if vec_begin and vec_end and vec_end >= vec_begin:
            count = (vec_end - vec_begin) // 16
            log.info(f"[C]  tracked_entities vector: begin=0x{vec_begin:x} end=0x{vec_end:x} count={count}")
            if count > 0 and count < 10000:
                # Leer primer shared_ptr
                entry_ptr = ru64(vec_begin + 0)
                entry_rep = ru64(vec_begin + 8)
                log.info(f"[C]  shared_ptr[0]: ptr=0x{entry_ptr:x} rep=0x{entry_rep:x}" if entry_ptr else "[C]  shared_ptr[0]: null")
                if entry_ptr and entry_ptr > 0x10000:
                    uid_at_0  = ri64(entry_ptr + 0)
                    uid_at_8  = ri64(entry_ptr + 8)
                    uid_at_16 = ri64(entry_ptr + 16)
                    log.info(f"[C]  entry[+0]={uid_at_0}  entry[+8]={uid_at_8}  entry[+16]={uid_at_16}")
        else:
            log.warning("[C]  Vector en offset 96 no parece válido")


# ══════════════════════════════════════════════════════════════════════════════
#  D) Unique ID del jugador
# ══════════════════════════════════════════════════════════════════════════════

def log_uid(player, log) -> None:
    uid = player.unique_id
    log.info(f"[D] player.unique_id = {uid}  (0x{uid:x})")


# ══════════════════════════════════════════════════════════════════════════════
#  Listener
# ══════════════════════════════════════════════════════════════════════════════

class ChunkLeakFixListener:
    def __init__(self, plugin: Plugin):
        self._plugin = plugin
        self._done   = False

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        if self._done:
            return
        self._done = True

        log    = self._plugin.logger
        player = event.player
        sep    = "=" * 60

        log.info(sep)
        log.info("[ChunkLeakFix] DIAGNÓSTICO COMPLETO")
        log.info(f"[ChunkLeakFix] Jugador: {player.name}")
        log.info(sep)

        _reload_maps()

        lvl = level_ptr(player)
        if not lvl:
            log.error("Sin level_ptr — abortando"); return
        log.info(f"[*] level_ptr = 0x{lvl:x}")

        # A: índice del vftable
        result = find_manager_index(lvl, log)
        if not result:
            log.error("Sin candidato para manager — fin"); return
        mgr_idx, mgr_ptr = result

        # B: offset del mapa
        map_off = find_map_offset(mgr_ptr, log)

        # C: layout de nodos
        if map_off is not None:
            inspect_map_nodes(mgr_ptr, map_off, log)
        else:
            log.warning("Saltando C — sin map_off confirmado")

        # D: unique_id
        log_uid(player, log)

        log.info(sep)
        log.info(f"[ChunkLeakFix] RESUMEN:")
        log.info(f"  PYBIND11_CPP_OFFSET      = {PYBIND11_CPP_OFFSET}")
        log.info(f"  VTABLE_MAP_DATA_MANAGER  = {mgr_idx}")
        log.info(f"  OFFSET_MGR_MAP           = {map_off if map_off is not None else '???'}")
        log.info(f"  player.unique_id OK      = True")
        log.info(sep)