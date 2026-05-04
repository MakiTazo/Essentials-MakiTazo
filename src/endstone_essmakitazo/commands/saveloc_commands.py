from endstone.command import CommandSender
from endstone import Player, ColorFormat
from pathlib import Path
import yaml

def set_spawn(sender: CommandSender, args: list[str], plugin) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    try:
        location = sender.location
        spawn_location = {
            "x": round(location.x, 2),
            "y": round(location.y, 2),
            "z": round(location.z, 2),
            "dimension": str(location.dimension.name)
        }

        config_path = Path(plugin.data_folder) / "config.yml"
        with open(config_path, "r", encoding="utf-8") as f:
            config = yaml.safe_load(f) or {}

        if "spawn" not in config:
            config["spawn"] = {}

        config["spawn"]["location"] = spawn_location

        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(config, f, default_flow_style=False, allow_unicode=True)

        sender.send_message(f"{ColorFormat.GREEN}✓ Spawn establecido en {spawn_location}")
        plugin.logger.info(f"Spawn establecido por {sender.name} en {spawn_location}")

    except Exception as e:
        sender.send_message(f"{ColorFormat.RED}Error al establecer spawn: {str(e)}")
        plugin.logger.error(f"Error en setspawn_command: {str(e)}")
        return False

    return True

def set_home(sender: CommandSender, args: list[str], plugin) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    try:
        user_path = Path(plugin.data_folder) / "userdata"
        user_path.mkdir(parents=True, exist_ok=True)
        user_file = user_path / f"{sender.id}.yml"

        if user_file.exists():
            with open(user_file, "r", encoding="utf-8") as f:
                config = yaml.safe_load(f) or {}
        else:
            config = {}

        if "home" not in config:
            config["home"] = {}

        config["home"]["location"] = {
            "x": sender.location.x,
            "y": sender.location.y,
            "z": sender.location.z,
            "dimension": str(sender.location.dimension.name)
        }

        with open(user_file, "w", encoding="utf-8") as f:
            yaml.dump(config, f, allow_unicode=True, default_flow_style=False)

    except Exception as e:
        plugin.logger.error(f"Error al guardar home: {e}")

    return True