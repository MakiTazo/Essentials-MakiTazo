from pathlib import Path
import yaml

from endstone import Player, ColorFormat
from endstone.level import Location
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault

command = {
    "spawn": {
        "description": "Ir al spawn",
        "usages": ["/spawn"],
        "permissions": [
            "endstone_essmakitazo.command.spawn"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.spawn": {
        "description": "Usar el comando /spawn",
        "default": PermissionDefault.TRUE,
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
        config_path = (
            Path(plugin.data_folder) / "config.yml"
        )

        with open(
            config_path,
            "r",
            encoding="utf-8"
        ) as file:
            config = yaml.safe_load(file)
        spawn_data = (
            config.get("spawn", {})
            .get("location")
        )
        if not spawn_data:
            sender.send_message(
                f"{ColorFormat.RED}"
                "El spawn no ha sido establecido"
            )
            return False
        x = spawn_data.get("x")
        y = spawn_data.get("y")
        z = spawn_data.get("z")
        dimension_id = spawn_data.get(
            "dimension",
            "minecraft:overworld"
        )
        level = plugin.server.level
        dimension = level.get_dimension(
            dimension_id
        )
        spawn_location = Location(
            dimension,
            x,
            y,
            z
        )
        sender.teleport(spawn_location)
        sender.send_message(
            f"{ColorFormat.GREEN}"
            "¡Te has transportado al spawn!"
        )
        return True

    except Exception as error:
        sender.send_message(
            f"{ColorFormat.RED}"
            f"Error al transportarse al spawn: "
            f"{error}"
        )
        plugin.logger.error(
            f"Error en spawn_command: {error}"
        )

        return False