from endstone.command import CommandSender
from endstone import Player, ColorFormat
from endstone.form import ModalForm, Label, Slider, StepSlider, TextInput, Toggle, Divider, Header
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
    """Crear lógica de petición de teleport to user usar 200 gameticks para  (10s de la vida real)"""
    return True


def tpa_accept(sender: CommandSender, target: Player, plugin) -> bool:
    """Crear lógica de aceptar petición de otro usuario """
    return True

def tpa_deny(sender: CommandSender, target: Player, plugin) -> bool:
    """Crear lógica de negar petición de otro usuario"""
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