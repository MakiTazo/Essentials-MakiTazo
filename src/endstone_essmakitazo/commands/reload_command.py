from endstone.command import CommandSender
from endstone import Player, ColorFormat
from endstone_essmakitazo.config.config_loader import load_or_create_config
from endstone_essmakitazo.utils.scoreboards import load_or_create_scoreboard_config

def execute(sender: CommandSender, args: list[str], plugin) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False

    try:
        load_or_create_config(str(plugin.data_folder))
        load_or_create_scoreboard_config(str(plugin.data_folder))
        sender.send_message(f"{ColorFormat.GREEN}✓ Configuración recargada")
        plugin.logger.info(f"{sender.name} recargó la configuración")
    except Exception as e:
        sender.send_message(f"{ColorFormat.RED}Error al recargar: {str(e)}")
        plugin.logger.error(f"Error en reload_command: {str(e)}")
        return False

    return True