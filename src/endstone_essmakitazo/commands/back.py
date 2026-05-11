from pathlib import Path
import yaml
from endstone import Player, ColorFormat
from endstone.level import Location
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault

command = {
    "back": {
        "description": "Regresas a tu posición anterior",
        "usages": ["/back"],
        "permissions": [
            "endstone_essmakitazo.command.teleport.back"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.teleport.back": {
        "description": "Usar el comando /back",
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
        if not user_file.exists():
            sender.send_message(f"{ColorFormat.GREEN}No hay posiciones guardadas!")
            return False
        with open(user_file,"r",encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
        user_last_pos = (config.get("last_position", {}).get("location"))
        x = user_last_pos.get("x")
        y = user_last_pos.get("y")
        z = user_last_pos.get("z")
        dimension_id = user_last_pos.get("dimension","minecraft:overworld")
        level = plugin.server.level
        dimension = level.get_dimension(dimension_id)
        back_location = Location(dimension,x,y,z)
        sender.teleport(back_location)
        sender.send_message(
            f"{ColorFormat.GREEN}"
            "¡Has sido transportado a tu última posición registrada!"
        )
        return True

    except Exception as error:
        sender.send_message(
            f"{ColorFormat.RED}"
            f"Error al transportarse: "
            f"{error}"
        )
        plugin.logger.error(
            f"Error en back_command: {error}"
        )

        return False