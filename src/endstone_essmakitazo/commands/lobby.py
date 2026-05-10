from pathlib import Path
import yaml
from endstone import Player, ColorFormat
from endstone.command import CommandSender

command = {
    "lobby": {
        "description": "Ir al lobby",
        "usages": ["/lobby"],
        "permissions": [
            "endstone_essmakitazo.command.lobby"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.lobby": {
        "description": "Usar el comando /lobby",
        "default": True,
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
        with open(config_path, "r") as file:
            config = yaml.safe_load(file)
        lobby_data = config["servers"]["lobby"]
        host = lobby_data["host"]
        port = lobby_data["port"]
        plugin.logger.info(
            f"Transfiriendo a {host}:{port}"
        )
        sender.send_message(
            f"{ColorFormat.YELLOW}"
            "Conectando al lobby..."
        )
        sender.transfer(host, port)
        return True

    except Exception as error:
        sender.send_message(
            f"{ColorFormat.RED}"
            f"Error al conectar al lobby: {error}"
        )
        plugin.logger.error(
            f"Error en lobby_command: {error}"
        )
        return False