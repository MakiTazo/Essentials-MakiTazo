from pathlib import Path
import yaml

from endstone.event import PlayerKickEvent, event_handler, PlayerDeathEvent, PlayerTeleportEvent, PlayerChatEvent
from endstone_essmakitazo.utils import fallback_server
from endstone import ColorFormat

@event_handler
def on_player_kick(self, event: PlayerKickEvent):
    player = event.player
    fallback_server.transfer_fallback_server(self, player)

@event_handler
def on_player_death(self, event: PlayerDeathEvent):
    try:
        player = event.player
        user_path = (Path(self.data_folder) / "userdata")
        user_path.mkdir(parents=True,exist_ok=True)
        user_file = (user_path / f"{player.unique_id}.yml")
        if user_file.exists():
            with open(user_file,"r",encoding="utf-8") as file:
                config = yaml.safe_load(file) or {}
        else:
            config = {}
        config["last_position"] = {
            "location": {
                "x": round(player.location.x, 2),
                "y": round(player.location.y, 2),
                "z": round(player.location.z, 2),
                "dimension": str(player.location.dimension.name)
            }
        }
        with open(user_file,"w",encoding="utf-8") as file:
            yaml.dump(config,file,allow_unicode=True,default_flow_style=False)
        player.send_message(
            f"{ColorFormat.RED}"
            "✓ Has muerto, puedes volver con /back"
        )
    except Exception as e:
        self.logger.error(e)

@event_handler
def on_player_teleport(self, event: PlayerTeleportEvent):
    try:
        player = event.player
        self.server.dispatch_command(
            self.server.command_sender,
            f"effect {player.name} resistance 10 5 true"
        )
    except Exception as e:
        self.logger.error(e)

@event_handler
def on_player_chat(self, event: PlayerChatEvent):
    event.cancel()
    msg = event.message
    sender = event.player
    for player in self.server.online_players:
        player.send_message(f"{sender.name}: {msg}")