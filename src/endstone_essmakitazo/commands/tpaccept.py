from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault
from endstone_essmakitazo.forms.tpa_form import get_pending_request, remove_request
from pathlib import Path
import yaml
from endstone.level import Location

command = {
    "tpaccept": {
        "description": "Acepta una solicitud de teletransporte",
        "usages": ["/tpaccept"],
        "permissions": [
            "endstone_essmakitazo.command.teleport.tpaccept"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.teleport.tpaccept": {
        "description": "Usar el comando /tpaccept",
        "default": PermissionDefault.TRUE,
    }
}

def handler(plugin, sender: CommandSender, args) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return True
    request = get_pending_request(sender.unique_id)
    if request is None:
        sender.send_message(f"{ColorFormat.RED}No tienes solicitudes de teletransporte pendientes")
        return True
    sender_player = plugin.server.get_player(request["sender_uuid"])
    if sender_player is None:
        sender.send_message(f"{ColorFormat.RED}El jugador que te envió la solicitud ya no está conectado")
        remove_request(sender.unique_id)
        return True
    user_path = Path(plugin.data_folder) / "userdata"
    user_path.mkdir(parents=True, exist_ok=True)
    user_file = user_path / f"{sender_player.unique_id}.yml"
    if user_file.exists():
        with open(user_file, "r", encoding="utf-8") as file:
            user_config = yaml.safe_load(file) or {}
    else:
        user_config = {}
    user_config["last_position"] = {
        "location": {
            "x": round(sender_player.location.x, 2),
            "y": round(sender_player.location.y, 2),
            "z": round(sender_player.location.z, 2),
            "dimension": str(sender_player.location.dimension.name)
        }
    }
    target_location = Location(
        sender.location.dimension,
        sender.location.x,
        sender.location.y,
        sender.location.z
    )
    sender_player.teleport(target_location)
    with open(user_file, "w", encoding="utf-8") as file:
        yaml.dump(user_config, file, allow_unicode=True, default_flow_style=False)
    remove_request(sender.unique_id)
    sender.send_message(f"{ColorFormat.GREEN}Has aceptado la solicitud de {request['sender_name']}")
    sender_player.send_message(f"{ColorFormat.GREEN}{sender.name} ha aceptado tu solicitud de teletransporte")
    return True