from endstone import Player, ColorFormat
from pathlib import Path
import yaml

def transfer_fallback_server(plugin, player):
    try:
        config_path = Path(plugin.data_folder) / "config.yml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        host = config["servers"]["lobby"]["host"]
        port = config["servers"]["lobby"]["port"]
        player.transfer(host, port)

    except Exception as e:
        plugin.logger.error(f"Error en lobby_command: {str(e)}")

def transferall_fallback_server(plugin):
    try:
        players = list(plugin.server.online_players)

        if not players:
            return

        config_path = Path(plugin.data_folder) / "config.yml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f) or {}

        host = config["servers"]["lobby"]["host"]
        port = config["servers"]["lobby"]["port"]

        for player in players:
            try:
                player.transfer(host, port)
            except Exception as e:
                plugin.logger.error(f"Error en lobby_command: {str(e)}")

    except Exception as e:
        plugin.logger.error(f"Error en transferall_fallback_server: {e}")