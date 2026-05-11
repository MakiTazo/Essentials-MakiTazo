from . import server_events

preloaded_events = {
    "on_player_join": server_events.on_player_join,
    "on_player_kick": server_events.on_player_kick,
    "on_player_death": server_events.on_player_death,
}