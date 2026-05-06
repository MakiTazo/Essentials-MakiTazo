from endstone.command import CommandSender
from endstone import Player, ColorFormat
from endstone.level import Location
from pathlib import Path
import yaml

# Diccionario para almacenar peticiones activas: {target_player_id: (sender_player, task)}
tpa_requests = {}

def is_moving(player: Player, start_loc: Location, tolerance: float = 0.1) -> bool:
    loc = player.location
    return (
            abs(loc.x - start_loc.x) > tolerance or
            abs(loc.y - start_loc.y) > tolerance or
            abs(loc.z - start_loc.z) > tolerance
    )


def tpa(sender: CommandSender, args: list[str], plugin) -> bool:
    """
    Crear petición de teleport a usuario.
    1. Enviar al target un Form para que acepte o cancele
    2. Si se acepta hacer lo siguiente:
       - Crear un Task de movimiento, si el sender se mueve en un timeout de 200 ticks (10 secs) se cancela la tarea.
       - si el sender o target se desconectan, se cancela la tarea
       -
    """
    return True

def tpa_accept(sender: CommandSender, args: list[str], plugin) -> bool:
    """Aceptar petición de teleport"""
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    if sender.id not in tpa_requests:
        sender.send_message(f"{ColorFormat.RED}No tienes peticiones pendientes")
        return False

    requester, task = tpa_requests[sender.id]
    task.cancel()
    del tpa_requests[sender.id]

    # Validar que requester sigue online
    if requester not in plugin.server.online_players:
        sender.send_message(f"{ColorFormat.RED}El jugador se desconectó")
        return False

    try:
        requester.teleport(sender.location)
        sender.send_message(f"{ColorFormat.GREEN}¡Aceptaste la petición de {requester.name}!")
        requester.send_message(f"{ColorFormat.GREEN}¡{sender.name} aceptó tu petición!")
        return True
    except Exception as e:
        sender.send_message(f"{ColorFormat.RED}Error al aceptar petición: {str(e)}")
        plugin.logger.error(f"Error en tpa_accept: {str(e)}")
        return False


def tpa_deny(sender: CommandSender, args: list[str], plugin) -> bool:
    """Negar petición de teleport"""
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    if sender.id not in tpa_requests:
        sender.send_message(f"{ColorFormat.RED}No tienes peticiones pendientes")
        return False

    requester, task = tpa_requests[sender.id]
    task.cancel()
    del tpa_requests[sender.id]

    # Validar que requester sigue online
    if requester in plugin.server.online_players:
        requester.send_message(f"{ColorFormat.RED}¡{sender.name} rechazó tu petición!")

    sender.send_message(f"{ColorFormat.RED}¡Rechazaste la petición de {requester.name}!")

    return True

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
        sender.send_message(f"{ColorFormat.RED}Error al transportarse al home: {str(e)}")
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
        sender.send_message(f"{ColorFormat.GREEN}¡Te has transportado al spawn!")

    except Exception as e:
        sender.send_message(f"{ColorFormat.RED}Error al transportarse al spawn: {str(e)}")
        plugin.logger.error(f"Error en spawn_command: {str(e)}")
        return False

    return True