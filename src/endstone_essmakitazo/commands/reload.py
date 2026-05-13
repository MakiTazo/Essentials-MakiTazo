from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault
from endstone_essmakitazo.config.config_loader import load_or_create_config
from endstone_essmakitazo.utils.scoreboards import (
    load_or_create_scoreboard_config,
    update_scoreboard_for_player
)

command = {
    "essreload": {
        "description": "Recargar la configuración",
        "usages": ["/essreload"],
        "permissions": [
            "endstone_essmakitazo.command.essreload"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.essreload": {
        "description": "Usar el comando /essreload",
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
        load_or_create_config(str(plugin.data_folder))
        load_or_create_scoreboard_config(str(plugin.data_folder))
        for player in plugin.server.online_players:
            update_scoreboard_for_player(player, plugin)
        sender.send_message(
            f"{ColorFormat.GREEN}"
            "✓ Configuración recargada"
        )
        plugin.logger.info(f"{sender.name} recargó la configuración")
        return True

    except Exception as error:
        sender.send_message(
            f"{ColorFormat.RED}"
            f"Error al recargar: {error}"
        )
        plugin.logger.error(f"Error en reload_command: {error}")
        return False