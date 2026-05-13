import asyncio
from pathlib import Path
import yaml

from endstone.event import PlayerKickEvent, PlayerJoinEvent, event_handler, PlayerDeathEvent
from endstone_essmakitazo.utils import fallback_server, scoreboards
from endstone import ColorFormat

@event_handler
def on_player_join(self, event: PlayerJoinEvent):
    try:
        loop = asyncio.new_event_loop()
        loop.run_until_complete(
            scoreboards.create_scoreboard_for_player(event.player, self)
        )
        loop.close()
    except Exception as e:
        self.logger.error(f"Error al crear scoreboard para {event.player.name}: {e}")

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