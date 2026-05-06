from endstone.command import CommandSender
from endstone import Player, ColorFormat
from endstone_essmakitazo.forms.tpa_form import send_tpa_form, tpa_requests
from endstone.level import Location
from pathlib import Path
import yaml

def is_moving(player: Player, start_loc: Location, tolerance: float = 0.1) -> bool:
    loc = player.location
    return (
            abs(loc.x - start_loc.x) > tolerance or
            abs(loc.y - start_loc.y) > tolerance or
            abs(loc.z - start_loc.z) > tolerance
    )

def tpa(sender: CommandSender, args: list[str], plugin) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message("Solo jugadores pueden usar /tpa")
        return True

    if not args:
        sender.send_error_message("Uso: /tpa <jugador>")
        return False

    target = plugin.server.get_player(args[0])
    if target is None:
        sender.send_error_message(f"Jugador '{args[0]}' no encontrado")
        return True

    if target.name == sender.name:
        sender.send_error_message("No puedes enviarte una petición a ti mismo")
        return True

    if target.name in tpa_requests:
        sender.send_error_message(f"{target.name} ya tiene una petición pendiente")
        return True

    send_tpa_form(plugin, sender, target)
    sender.send_message(f"{ColorFormat.YELLOW}Petición enviada a {target.name}...")
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