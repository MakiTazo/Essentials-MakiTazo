from endstone.command import CommandSender
from endstone import Player, ColorFormat
from endstone.form import ModalForm, Label, Slider, StepSlider, TextInput, Toggle, Divider, Header
from endstone.level import Location
# Endstone cuenta con su propio asyncio pero no hay documentación existente creo
# Te enviaré el __init__.py de ese asyncio para que veas qué se puede usar
from endstone import asyncio
from pathlib import Path
from typing import Dict, Tuple
import yaml
import time

# Almacenamiento de solicitudes {solicitante: (destino, timestamp)}
tpa_requests: Dict[Player, Tuple[Player, float]] = {}
TPA_TIMEOUT = 10  # segundos


def is_moving(player: Player, start_loc: Location, tolerance: float = 0.1) -> bool:
    """Verifica si el jugador se ha movido desde la posición inicial"""
    loc = player.location
    return (
            abs(loc.x - start_loc.x) > tolerance or
            abs(loc.y - start_loc.y) > tolerance or
            abs(loc.z - start_loc.z) > tolerance
    )


def tpa(sender: CommandSender, args: list[str], plugin) -> bool:
    """Envía solicitud de teletransporte usando ModalForm"""
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    if len(args) < 1:
        sender.send_message(f"{ColorFormat.RED}Uso correcto: /tpa <jugador>")
        return False

    target = plugin.server.get_player(args[0])
    if target is None:
        sender.send_message(f"{ColorFormat.RED}Jugador no encontrado")
        return False

    if target == sender:
        sender.send_message(f"{ColorFormat.RED}No puedes enviarte TPA a ti mismo")
        return False

    # Verificar movimiento antes de enviar
    start_location = sender.location
    if is_moving(sender, start_location):
        sender.send_message(f"{ColorFormat.RED}Te has movido, acción cancelada!")
        return False

    # Verificar si ya hay solicitud pendiente
    if sender in tpa_requests:
        sender.send_message(f"{ColorFormat.RED}Ya tienes una solicitud TPA pendiente")
        return False

    # Guardar solicitud con timestamp actual
    tpa_requests[sender] = (target, time.time())

    # Confirmación al solicitante
    sender.send_message(f"{ColorFormat.GREEN}Solicitud TPA enviada a {target.name}")

    # Crear formulario para el destino
    form = ModalForm(
        title=f"📡 Solicitud de teletransporte",
        controls=[
            Label(
                f"✨ {sender.name} quiere teletransportarse a ti.\n\n⏰ Expira en {TPA_TIMEOUT} segundos.\n\n📍 Desde: {sender.location.x:.1f}, {sender.location.y:.1f}, {sender.location.z:.1f}")
        ],
        submit_button="✅ Aceptar",
        on_submit=lambda player, data: on_tpa_accept(sender, target, plugin),
        on_close=lambda player: on_tpa_reject(sender, target, plugin)
    )

    # Enviar formulario
    target.send_form(form)

    # Programar limpieza automática usando el asyncio de Endstone
    async def auto_cleanup():
        try:
            # Usar asyncio.sleep estándar con get_loop de Endstone
            loop = asyncio.get_loop()
            future = asyncio.run_coroutine_threadsafe(asyncio.sleep(TPA_TIMEOUT), loop)
            future.result(timeout=TPA_TIMEOUT + 1)
        except Exception:
            pass  # Timeout normal

        # Verificar y limpiar si la solicitud sigue existiendo
        if sender in tpa_requests:
            current_target, timestamp = tpa_requests[sender]
            if current_target == target and time.time() - timestamp >= TPA_TIMEOUT:
                del tpa_requests[sender]
                # Notificar expiración solo si ambos siguen válidos
                if sender.is_valid:
                    sender.send_message(f"{ColorFormat.RED}Tu solicitud TPA para {target.name} expiró")
                if target.is_valid:
                    target.send_message(f"{ColorFormat.RED}La solicitud TPA de {sender.name} expiró")

    # Ejecutar la limpieza con submit
    asyncio.submit(auto_cleanup())

    return True


def on_tpa_accept(sender: Player, target: Player, plugin) -> None:
    """Callback cuando se acepta la solicitud TPA"""
    # Verificar que la solicitud existe
    if sender not in tpa_requests:
        target.send_message(f"{ColorFormat.RED}La solicitud TPA ya no está vigente")
        return

    # Verificar que sigue siendo el mismo destino
    stored_target, timestamp = tpa_requests[sender]
    if stored_target != target:
        target.send_message(f"{ColorFormat.RED}La solicitud TPA ha sido modificada")
        if sender in tpa_requests:
            del tpa_requests[sender]
        return

    # Verificar expiración por tiempo
    if time.time() - timestamp >= TPA_TIMEOUT:
        target.send_message(f"{ColorFormat.RED}La solicitud TPA ha expirado")
        if sender in tpa_requests:
            del tpa_requests[sender]
        return

    # Verificar que el sender sigue siendo un Player válido y online
    if not isinstance(sender, Player) or not sender.is_valid:
        target.send_message(f"{ColorFormat.RED}El jugador que solicitó la TPA ya no está disponible")
        if sender in tpa_requests:
            del tpa_requests[sender]
        return

    # Verificar que el target sigue válido
    if not target.is_valid:
        target.send_message(f"{ColorFormat.RED}No se pudo completar el teletransporte")
        if sender in tpa_requests:
            del tpa_requests[sender]
        return

    try:
        # Realizar teletransporte
        sender.teleport(target.location)
        sender.send_message(f"{ColorFormat.GREEN}¡Teletransporte exitoso a {target.name}!")
        target.send_message(f"{ColorFormat.GREEN}Has aceptado la solicitud TPA de {sender.name}")
    except Exception as e:
        plugin.logger.error(f"Error en teletransporte TPA: {e}")
        if sender.is_valid:
            sender.send_message(f"{ColorFormat.RED}Error al teletransportar")
        if target.is_valid:
            target.send_message(f"{ColorFormat.RED}Error al procesar la solicitud TPA")
    finally:
        # Limpiar solicitud siempre
        if sender in tpa_requests:
            del tpa_requests[sender]


def on_tpa_reject(sender: Player, target: Player, plugin) -> None:
    if sender not in tpa_requests:
        return

    stored_target, timestamp = tpa_requests[sender]
    if stored_target != target:
        if sender in tpa_requests:
            del tpa_requests[sender]
        return

    if time.time() - timestamp >= TPA_TIMEOUT:
        # Ya expiró, no enviar mensajes duplicados
        if sender in tpa_requests:
            del tpa_requests[sender]
        return

    if target.is_valid:
        target.send_message(f"{ColorFormat.YELLOW}Rechazaste la solicitud TPA de {sender.name}")
    if isinstance(sender, Player) and sender.is_valid:
        sender.send_message(f"{ColorFormat.YELLOW}{target.name} rechazó tu solicitud TPA")
    if sender in tpa_requests:
        del tpa_requests[sender]

def home(sender: CommandSender, args: list[str], plugin) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    try:
        user_path = Path(plugin.data_folder) / "userdata"
        user_path.mkdir(parents=True, exist_ok=True)
        user_file = user_path / f"{sender.id}.yml"

        if not user_file.exists():
            sender.send_message(f"{ColorFormat.GREEN}Como no tenías un home ¡Has sido transportado al spawn!")
            spawn(sender, args, plugin)
            return True

        with open(user_file, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        user_home = config.get("home", {}).get("location")
        if not user_home:
            sender.send_message(f"{ColorFormat.GREEN}Como no tenías un home ¡Has sido transportado al spawn!")
            spawn(sender, args, plugin)
            return True

        x = user_home.get("x")
        y = user_home.get("y")
        z = user_home.get("z")
        dimension_id = user_home.get("dimension", "minecraft:overworld")
        level = plugin.server.level
        dimension = level.get_dimension(dimension_id)
        home_location = Location(dimension, x, y, z)
        sender.teleport(home_location)
        sender.send_message(f"{ColorFormat.GREEN}¡Has sido transportado a tu home!")

    except Exception as e:
        sender.send_message(f"{ColorFormat.RED}Error al teleportarse al home: {str(e)}")
        plugin.logger.error(f"Error en home_command: {str(e)}")
        return False

    return True

def spawn(sender: CommandSender, args: list[str], plugin) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    try:
        config_path = Path(plugin.data_folder) / "config.yml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f)

        spawn_data = config.get("spawn", {}).get("location")

        if not spawn_data:
            sender.send_message(f"{ColorFormat.RED}El spawn no ha sido establecido")
            return False

        x = spawn_data.get("x")
        y = spawn_data.get("y")
        z = spawn_data.get("z")
        dimension_id = spawn_data.get("dimension", "minecraft:overworld")

        level = plugin.server.level
        dimension = level.get_dimension(dimension_id)
        spawn_location = Location(dimension, x, y, z)

        sender.teleport(spawn_location)
        sender.send_message(f"{ColorFormat.GREEN}¡Te has teletransportado al spawn!")

    except Exception as e:
        sender.send_message(f"{ColorFormat.RED}Error al teleportarse al spawn: {str(e)}")
        plugin.logger.error(f"Error en spawn_command: {str(e)}")
        return False

    return True