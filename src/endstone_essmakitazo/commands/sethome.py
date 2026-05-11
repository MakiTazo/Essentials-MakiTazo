from pathlib import Path
import yaml

from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault

command = {
    "sethome": {
        "description": "Establece tu hogar",
        "usages": ["/sethome"],
        "permissions": [
            "endstone_essmakitazo.command.teleport.sethome"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.teleport.sethome": {
        "description": "Usar el comando /sethome",
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
        user_path = (Path(plugin.data_folder) / "userdata")
        user_path.mkdir(parents=True,exist_ok=True)
        user_file = (user_path / f"{sender.unique_id}.yml")
        if user_file.exists():
            with open(user_file,"r",encoding="utf-8") as file:
                config = yaml.safe_load(file) or {}
        else:
            config = {}
        config["home"] = {
            "location": {
                "x": round(sender.location.x, 2),
                "y": round(sender.location.y, 2),
                "z": round(sender.location.z, 2),
                "dimension": str(
                    sender.location.dimension.name
                )
            }
        }
        with open(user_file,"w",encoding="utf-8") as file:
            yaml.dump(
                config,
                file,
                allow_unicode=True,
                default_flow_style=False
            )
        sender.send_message(
            f"{ColorFormat.GREEN}"
            "✓ Hogar establecido"
        )
        plugin.logger.info(
            f"{sender.name} estableció su hogar"
        )
        return True

    except Exception as error:
        sender.send_message(
            f"{ColorFormat.RED}"
            f"Error al guardar home: {error}"
        )
        plugin.logger.error(
            f"Error en sethome: {error}"
        )
        return False