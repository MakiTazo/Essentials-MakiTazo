from endstone.command import CommandSender
from endstone import Player, ColorFormat
from pathlib import Path
import yaml


def execute(sender: CommandSender, args: list[str], plugin) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    try:
        config_path = Path(plugin.data_folder) / "config.yml"
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        host = config["servers"]["lobby"]["host"]
        port = config["servers"]["lobby"]["port"]

        plugin.logger.info(f"Transfiriendo a {host}:{port}")

        sender.send_message(f"{ColorFormat.YELLOW}Conectando al lobby...")
        sender.transfer(host, port)

    except Exception as e:
        sender.send_message(f"{ColorFormat.RED}Error al conectar al lobby: {str(e)}")
        plugin.logger.error(f"Error en lobby_command: {str(e)}")
        return False

    return True