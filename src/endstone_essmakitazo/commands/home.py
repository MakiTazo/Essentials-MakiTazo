from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault
from endstone_essmakitazo.forms.home_form import open_home_form

command = {
    "home": {
        "description": "Vas a tu hogar",
        "usages": ["/home"],
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
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return True
    open_home_form(plugin, sender)
    return True