"""
chunk_leak_fix.py  —  FASE 1: DIAGNÓSTICO PURO

No modifica NADA en memoria.
Usa PlayerJoinEvent (objeto completamente inicializado, sin destrucción)
para inspeccionar de forma segura:

  1. El offset del C++ ptr dentro del wrapper pybind11 de player.level
  2. Las entradas del vftable de ServerLevel (para encontrar _getMapDataManager)
  3. La cadena de punteros: level → manager → mapa

Cuando los valores en consola sean correctos, activamos la lógica real.
"""

import ctypes
import os
import struct

from endstone.plugin import Plugin
from endstone.event import event_handler, PlayerJoinEvent


# ══════════════════════════════════════════════════════════════════════════════
#  Utilidades de memoria (solo lectura)
# ══════════════════════════════════════════════════════════════════════════════

def _safe_read_u64(addr: int) -> int | None:
    try:
        return struct.unpack("Q", bytes((ctypes.c_uint8 * 8).from_address(addr)))[0]
    except Exception:
        return None


def _get_exec_ranges() -> list[tuple[int, int]]:
    """Lee /proc/self/maps y retorna rangos de memoria ejecutable."""
    ranges = []
    try:
        with open("/proc/self/maps") as f:
            for line in f:
                parts = line.split()
                if len(parts) >= 2 and 'x' in parts[1]:
                    a, b = parts[0].split('-')
                    ranges.append((int(a, 16), int(b, 16)))
    except Exception:
        pass
    return ranges


def _is_exec(addr: int, ranges: list) -> bool:
    return any(s <= addr < e for s, e in ranges)


def _get_bds_base() -> int | None:
    """Dirección base del módulo bedrock_server en memoria."""
    try:
        with open("/proc/self/maps") as f:
            for line in f:
                if "bedrock_server" in line and "r-xp" in line:
                    return int(line.split('-')[0], 16)
    except Exception:
        pass
    return None


# ══════════════════════════════════════════════════════════════════════════════
#  PASO 1 — Encontrar el C++ ptr dentro del objeto pybind11
# ══════════════════════════════════════════════════════════════════════════════

def find_cpp_ptr(py_obj, label: str, exec_ranges: list, logger) -> int | None:
    """
    Escanea los primeros 128 bytes del objeto pybind11 buscando un puntero
    cuyo primer qword (vftable) apunte a memoria ejecutable.

    Imprime TODOS los offsets para que podamos ver el layout real.
    Marca con ★ el primero que parece un C++ ptr válido.
    """
    base = id(py_obj)
    logger.info(f"[Diag] Layout pybind11 de {label}  (PyObject* = 0x{base:x})")
    logger.info(f"[Diag]  {'offset':>6}  {'valor':>18}  {'vftable[0]':>18}  nota")

    best = None
    for off in range(0, 128, 8):
        val = _safe_read_u64(base + off)
        if val is None:
            logger.info(f"[Diag]  {off:6d}  {'<no legible>':>18}")
            continue

        # ¿Este valor apunta a algo con vftable ejecutable?
        vft0 = _safe_read_u64(val) if val > 0x10000 else None
        in_exec = vft0 is not None and _is_exec(vft0, exec_ranges)

        marker = "  ★ C++ ptr" if in_exec else ""
        vft_str = f"0x{vft0:016x}" if vft0 is not None else "             N/A"
        logger.info(f"[Diag]  {off:6d}  0x{val:016x}  {vft_str}{marker}")

        if in_exec and best is None:
            best = (off, val)

    if best:
        logger.info(f"[Diag] → C++ ptr encontrado en offset +{best[0]}: 0x{best[1]:x}")
    else:
        logger.info("[Diag] → No se encontró C++ ptr. Revisar layout manualmente.")

    return best[1] if best else None


# ══════════════════════════════════════════════════════════════════════════════
#  PASO 2 — Escanear el vftable de ServerLevel
#  Buscamos _getMapDataManager: una función que retorne un puntero no nulo
# ══════════════════════════════════════════════════════════════════════════════

def scan_vftable(level_ptr: int, exec_ranges: list, logger,
                 scan_from: int = 350, scan_to: int = 420) -> None:
    """
    Lista las entradas del vftable de ServerLevel entre scan_from y scan_to.
    Todas deben apuntar a memoria ejecutable (✓).
    Las que no apunten (✗) marcan el fin del vftable o un índice inválido.

    Con esto ajustamos VTABLE_MAP_DATA_MANAGER (actualmente asumido en 381).
    """
    vftable = _safe_read_u64(level_ptr)
    if vftable is None:
        logger.warning("[Diag] No se pudo leer vftable de level_ptr")
        return

    logger.info(f"[Diag] vftable de ServerLevel @ 0x{vftable:x}")
    logger.info(f"[Diag]  {'índice':>6}  {'fn addr':>18}  estado")

    for idx in range(scan_from, scan_to + 1):
        fn = _safe_read_u64(vftable + idx * 8)
        if fn is None:
            logger.info(f"[Diag]  {idx:6d}  {'<no legible>':>18}")
            continue
        ok = _is_exec(fn, exec_ranges)
        mark = "✓" if ok else "✗ FUERA DE EXEC"
        logger.info(f"[Diag]  {idx:6d}  0x{fn:016x}  {mark}")


# ══════════════════════════════════════════════════════════════════════════════
#  PASO 3 — Signature scan de funciones clave en bedrock_server
#  Encuentra getOrCreateUniqueID y _getMapDataManager por bytes
# ══════════════════════════════════════════════════════════════════════════════

# Firmas Linux x64 (System V ABI) — pueden diferir de Windows.
# Si no hacen match, las cambiamos usando los resultados del vftable scan.
_SIGNATURES = {
    "Actor::getOrCreateUniqueID": "40 53 48 83 EC ?? 4C 8B 51 ?? BB ?? ?? ?? ?? 8B 51",
    # Añadir más firmas aquí cuando las encontremos
}

def scan_signatures(logger) -> dict[str, int]:
    """
    Escanea el módulo bedrock_server buscando las firmas conocidas.
    Retorna {nombre: dirección} para las que encuentre.
    """
    bds_base = _get_bds_base()
    if bds_base is None:
        logger.warning("[Diag] No se encontró bedrock_server en /proc/self/maps")
        return {}

    SCAN_SIZE = 96 * 1024 * 1024  # 96 MB
    logger.info(f"[Diag] Escaneando bedrock_server @ base=0x{bds_base:x}  tamaño={SCAN_SIZE // 1024 // 1024}MB")

    try:
        mem = (ctypes.c_uint8 * SCAN_SIZE).from_address(bds_base)
    except Exception as e:
        logger.error(f"[Diag] No se pudo mapear memoria BDS: {e}")
        return {}

    found = {}
    for name, pattern in _SIGNATURES.items():
        parts = pattern.split()
        pat   = [None if b == "??" else int(b, 16) for b in parts]
        n     = len(pat)
        addr  = 0
        for i in range(SCAN_SIZE - n):
            if all(pat[j] is None or mem[i + j] == pat[j] for j in range(n)):
                addr = bds_base + i
                break
        if addr:
            logger.info(f"[Diag] ✓ {name:40s} @ 0x{addr:x}")
        else:
            logger.warning(f"[Diag] ✗ {name:40s}  — no encontrada (firma puede ser diferente en Linux)")
        found[name] = addr

    return found


# ══════════════════════════════════════════════════════════════════════════════
#  Listener — TODO el diagnóstico corre en PlayerJoinEvent (seguro)
# ══════════════════════════════════════════════════════════════════════════════

class ChunkLeakFixListener:
    """
    Registrar con: plugin.register_events(ChunkLeakFixListener(self))

    Al primer jugador que entre se ejecuta el diagnóstico completo y se
    imprime en consola. Después no hace nada más (flag _done).
    """

    def __init__(self, plugin: Plugin):
        self._plugin = plugin
        self._done   = False  # solo diagnosticar una vez

    @event_handler
    def on_player_join(self, event: PlayerJoinEvent) -> None:
        if self._done:
            return
        self._done = True

        logger = self._plugin.logger
        player = event.player

        logger.info("=" * 60)
        logger.info("[ChunkLeakFix] INICIO DE DIAGNÓSTICO")
        logger.info(f"[ChunkLeakFix] Jugador de prueba: {player.name}")
        logger.info("=" * 60)

        exec_ranges = _get_exec_ranges()
        logger.info(f"[Diag] Regiones ejecutables encontradas: {len(exec_ranges)}")

        # ── Paso 1: layout de player.level ──────────────────────────────────
        logger.info("[Diag] ── PASO 1: pybind11 layout de player.level ──────────")
        level_ptr = find_cpp_ptr(player.level, "player.level", exec_ranges, logger)

        # ── Paso 2: vftable scan ─────────────────────────────────────────────
        if level_ptr:
            logger.info("[Diag] ── PASO 2: vftable scan (índices 350–420) ──────────")
            scan_vftable(level_ptr, exec_ranges, logger, scan_from=350, scan_to=420)
        else:
            logger.warning("[Diag] Saltando paso 2 (no se obtuvo level_ptr)")

        # ── Paso 3: signature scan ───────────────────────────────────────────
        logger.info("[Diag] ── PASO 3: signature scan en bedrock_server ──────────")
        scan_signatures(logger)

        logger.info("=" * 60)
        logger.info("[ChunkLeakFix] FIN DE DIAGNÓSTICO — revisa los logs arriba")
        logger.info("=" * 60)