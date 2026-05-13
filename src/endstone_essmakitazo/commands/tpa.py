from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault
from endstone_essmakitazo.forms.tpa_form import open_tpa_form

command = {
    "tpa": {
        "description": "Te transporta a otro jugador",
        "usages": ["/tpa"],
        "permissions": [
            "endstone_essmakitazo.command.teleport.tpa"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.teleport.tpa": {
        "description": "Usar el comando /tpa",
        "default": PermissionDefault.TRUE,
    }
}

def handler(plugin, sender: CommandSender, args) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message("Solo jugadores pueden usar /tpa")
        return True
    open_tpa_form(sender)
    return True