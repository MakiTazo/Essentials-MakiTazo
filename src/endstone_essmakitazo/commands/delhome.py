from pathlib import Path
import yaml

from endstone import Player, ColorFormat
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault

command = {
    "delhome": {
        "description": "Elimina un hogar guardado",
        "usages": ["/delhome <name: string>"],
        "permissions": [
            "endstone_essmakitazo.command.teleport.delhome"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.teleport.delhome": {
        "description": "Usar el comando /delhome",
        "default": PermissionDefault.TRUE,
    }
}


def handler(plugin, sender: CommandSender, args) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(
            f"{ColorFormat.RED}Solo los jugadores pueden usar este comando"
        )
        return False

    try:
        if len(args) == 0:
            sender.send_message(
                f"{ColorFormat.RED}Debes especificar un home"
            )
            return False

        home_name = args[0]
        user_path = Path(plugin.data_folder) / "userdata"
        user_path.mkdir(parents=True, exist_ok=True)
        user_file = user_path / f"{sender.unique_id}.yml"

        if not user_file.exists():
            sender.send_message(f"{ColorFormat.RED}No tienes homes guardados")
            return False

        with open(user_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}

        homes = config.get("home", {})
        if home_name not in homes:
            sender.send_message(f"{ColorFormat.RED}Ese home no existe")
            return False

        del homes[home_name]
        config["home"] = homes
        with open(user_file, "w", encoding="utf-8") as file:
            yaml.dump(config, file, allow_unicode=True, default_flow_style=False)
        sender.send_message(f"{ColorFormat.GREEN}✓ Home '{home_name}' eliminado")
        plugin.logger.info(f"{sender.name} eliminó el home {home_name}")
        return True

    except Exception as error:
        sender.send_message(
            f"{ColorFormat.RED}Error al eliminar home: {error}"
        )
        plugin.logger.error(
            f"Error en delhome: {error}"
        )
        return False