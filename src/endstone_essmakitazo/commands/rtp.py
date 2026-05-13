import random
import math
from pathlib import Path
import yaml
from endstone import Player, ColorFormat
from endstone.level import Location
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault

command = {
    "rtp": {
        "description": "Te transporta a un lugar aleatorio del mundo",
        "usages": ["/rtp"],
        "permissions": [
            "endstone_essmakitazo.command.teleport.rtp"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.teleport.rtp": {
        "description": "Usar el comando /rtp para transportarte a un lugar aleatorio del mundo",
        "default": PermissionDefault.TRUE,
    }
}


def handler(plugin, sender: CommandSender, args) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    if str(sender.dimension.name) != "Overworld":
        sender.send_message(f"{ColorFormat.RED}Este comando solo se puede usar en el Overworld")
        return False

    try:
        config_path = Path(plugin.data_folder) / "config.yml"
        with open(config_path, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        spawn_location = config.get("spawn", {}).get("location")
        if not spawn_location:
            sender.send_message(f"{ColorFormat.RED}No hay un spawn establecido, usa /setspawn primero")
            return False

        center_x = spawn_location.get("x")
        center_z = spawn_location.get("z")
        dimension_id = spawn_location.get("dimension", "minecraft:overworld")
        rtp_config = config.get("rtp", {})
        min_radius = rtp_config.get("min_radius", 1000)
        max_radius = rtp_config.get("max_radius", 5000)
        dimension = plugin.server.level.get_dimension(dimension_id)
        angle = random.uniform(0, 360)
        distance = random.uniform(min_radius, max_radius)
        random_x = round(center_x + distance * math.cos(math.radians(angle)))
        random_z = round(center_z + distance * math.sin(math.radians(angle)))
        user_path = Path(plugin.data_folder) / "userdata"
        user_path.mkdir(parents=True, exist_ok=True)
        user_file = user_path / f"{sender.unique_id}.yml"

        if user_file.exists():
            with open(user_file, "r", encoding="utf-8") as file:
                user_config = yaml.safe_load(file) or {}
        else:
            user_config = {}

        user_config["last_position"] = {
            "location": {
                "x": round(sender.location.x, 2),
                "y": round(sender.location.y, 2),
                "z": round(sender.location.z, 2),
                "dimension": str(sender.location.dimension.name)
            }
        }
        rtp_location = Location(dimension, random_x, 319, random_z)
        sender.teleport(rtp_location)

        with open(user_file, "w", encoding="utf-8") as file:
            yaml.dump(user_config, file, allow_unicode=True, default_flow_style=False)

        sender.send_message(f"{ColorFormat.GREEN}¡Has sido transportado a X:{random_x} Z:{random_z}!")
        return True

    except Exception as error:
        sender.send_message(f"{ColorFormat.RED}Error al transportarse: {error}")
        plugin.logger.error(f"Error: {error}")
        return False