from pathlib import Path
import yaml
from endstone import Player, ColorFormat
from endstone.level import Location
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault
from .spawn import handler as spawn_handler

command = {
    "home": {
        "description": "Vas a tu hogar",
        "usages": ["/home <name: string>"],
        "permissions": [
            "endstone_essmakitazo.command.teleport.home"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.teleport.home": {
        "description": "Usar el comando /home",
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
            sender.send_message(
                f"{ColorFormat.GREEN}"
                "Como no tenías un home "
                "¡Has sido transportado al spawn!"
            )
            return spawn_handler(plugin,sender,args)

        with open(user_file,"r",encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        home_name = args[0] if len(args) > 0 else "default"
        user_home = config.get("home", {}).get(home_name)
        if not user_home:
            sender.send_message(
                f"{ColorFormat.GREEN}"
                "Como no tenías un home "
                "¡Has sido transportado al spawn!"
            )
            return spawn_handler(plugin,sender,args)
        x = user_home.get("x")
        y = user_home.get("y")
        z = user_home.get("z")
        dimension_id = user_home.get("dimension","minecraft:overworld")
        level = plugin.server.level
        dimension = level.get_dimension(dimension_id)
        home_location = Location(dimension,x,y,z)
        sender.teleport(home_location)
        sender.send_message(
            f"{ColorFormat.GREEN}"
            "¡Has sido transportado a tu home!"
        )
        return True

    except Exception as error:
        sender.send_message(
            f"{ColorFormat.RED}"
            f"Error al transportarse al home: "
            f"{error}"
        )
        plugin.logger.error(
            f"Error en home_command: {error}"
        )

        return False