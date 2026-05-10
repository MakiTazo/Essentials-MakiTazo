from pathlib import Path
import yaml
from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault

command = {
    "setspawn": {
        "description": "Establece el spawn",
        "usages": ["/setspawn"],
        "permissions": [
            "endstone_essmakitazo.command.setspawn"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.setspawn": {
        "description": "Usar el comando /setspawn",
        "default": PermissionDefault.OP,
    }
}


def handler(plugin, sender: CommandSender, args) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(
            f"{ColorFormat.RED}"
            "Solo los jugadores pueden usar este comando"
        )
        return False

    try:
        location = sender.location
        spawn_location = {
            "x": round(location.x, 2),
            "y": round(location.y, 2),
            "z": round(location.z, 2),
            "dimension": str(location.dimension.name)
        }
        config_path = (
            Path(plugin.data_folder) / "config.yml"
        )
        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:
            config = yaml.safe_load(file) or {}
        config["spawn"] = {
            "location": spawn_location
        }
        with open(
            config_path,
            "w",
            encoding="utf-8"
        ) as file:
            yaml.dump(
                config,
                file,
                allow_unicode=True,
                default_flow_style=False
            )
        sender.send_message(
            f"{ColorFormat.GREEN}"
            f"✓ Spawn establecido en "
            f"{spawn_location}"
        )
        plugin.logger.info(
            f"Spawn establecido por "
            f"{sender.name} en {spawn_location}"
        )
        return True
    except Exception as error:
        sender.send_message(
            f"{ColorFormat.RED}"
            f"Error al establecer spawn: {error}"
        )
        plugin.logger.error(
            f"Error en setspawn: {error}"
        )
        return False