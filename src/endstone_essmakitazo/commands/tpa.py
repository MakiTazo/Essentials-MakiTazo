from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault
from endstone.level import Location
from endstone_essmakitazo.forms.tpa_form import send_tpa_form, tpa_requests

command = {
    "tpa": {
        "description": "Te transporta a otro jugador",
        "usages": ["/tpa <jugador>"],
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


def is_moving(
    player: Player,
    start_loc: Location,
    tolerance: float = 0.1
) -> bool:
    loc = player.location
    return (
        abs(loc.x - start_loc.x) > tolerance or
        abs(loc.y - start_loc.y) > tolerance or
        abs(loc.z - start_loc.z) > tolerance
    )

def handler(plugin, sender: CommandSender, args) -> bool:
    if not isinstance(sender, Player):
        sender.send_error_message(
            "Solo jugadores pueden usar /tpa"
        )
        return True
    if not args:
        sender.send_error_message(
            "Uso: /tpa <jugador>"
        )
        return False
    target = plugin.server.get_player(args[0])
    if target is None:
        sender.send_error_message(
            f"Jugador '{args[0]}' no encontrado"
        )
        return True
    if target.name == sender.name:
        sender.send_error_message(
            "No puedes enviarte una petición a ti mismo"
        )
        return True
    if target.name in tpa_requests:
        sender.send_error_message(
            f"{target.name} ya tiene "
            f"una petición pendiente"
        )
        return True
    send_tpa_form(
        plugin,
        sender,
        target
    )
    sender.send_message(
        f"{ColorFormat.YELLOW}"
        f"Petición enviada a {target.name}..."
    )
    return True