from pathlib import Path
import yaml
from endstone import Player, ColorFormat
from endstone.level import Location
from endstone.command import CommandSender
from endstone.permissions import PermissionDefault

command = {
    "back": {
        "description": "Regresas a tu posición anterior",
        "usages": ["/back"],
        "permissions": [
            "endstone_essmakitazo.command.teleport.back"
        ],
    }
}

permissions = {
    "endstone_essmakitazo.command.teleport.back": {
        "description": "Usar el comando /back",
        "default": PermissionDefault.TRUE,
    }
}

def handler(plugin, sender: CommandSender, args) -> bool:
    if not isinstance(sender, Player):
        sender.send_message(f"{ColorFormat.RED}Solo los jugadores pueden usar este comando")
        return False
    try:
        user_path = Path(plugin.data_folder) / "userdata"
        user_path.mkdir(parents=True, exist_ok=True)
        user_file = user_path / f"{sender.unique_id}.yml"
        if not user_file.exists():
            sender.send_message(f"{ColorFormat.GREEN}No hay posiciones guardadas!")
            return False
        with open(user_file, "r", encoding="utf-8") as file:
            config = yaml.safe_load(file) or {}
        user_last_pos = config.get("last_position", {}).get("location")
        if not user_last_pos:
            sender.send_message(f"{ColorFormat.GREEN}No hay posiciones guardadas!")
            return False
        config["last_position"] = {
            "location": {
                "x": round(sender.location.x, 2),
                "y": round(sender.location.y, 2),
                "z": round(sender.location.z, 2),
                "dimension": str(sender.location.dimension.name)
            }
        }
        x = user_last_pos.get("x")
        y = user_last_pos.get("y")
        z = user_last_pos.get("z")
        dimension_id = user_last_pos.get("dimension", "minecraft:overworld")
        level = plugin.server.level
        dimension = level.get_dimension(dimension_id)
        back_location = Location(dimension, x, y, z)
        sender.teleport(back_location)
        with open(user_file, "w", encoding="utf-8") as file:
            yaml.dump(config, file, allow_unicode=True, default_flow_style=False)
        sender.send_message(f"{ColorFormat.GREEN}¡Has sido transportado a tu última posición registrada!")
        return True
    except Exception as error:
        sender.send_message(f"{ColorFormat.RED}Error al transportarse: {error}")
        plugin.logger.error(f"Error en back_command: {error}")
        return False