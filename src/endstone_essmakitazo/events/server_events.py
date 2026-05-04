from endstone.event import PlayerKickEvent, PlayerJoinEvent, PlayerQuitEvent, event_handler
from endstone_essmakitazo.utils import fallback_server, scoreboards


@event_handler
def on_player_join(self, event: PlayerJoinEvent):
    scoreboards.create_scoreboard_for_player(event.player, self)
    return True

@event_handler
def on_player_quit(self, event: PlayerQuitEvent):
    return True

@event_handler
def on_player_kick(self, event: PlayerKickEvent):
    player = event.player
    fallback_server.transfer_fallback_server(self, player)
    return True