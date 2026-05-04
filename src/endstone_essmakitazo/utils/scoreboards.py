from endstone import Player
from endstone.scoreboard import DisplaySlot, Criteria
from pathlib import Path
import yaml

DEFAULT_SCOREBOARD_CONFIG = {
    "scoreboard": {
        "enabled": True,
        "remember-toggle-choice": False,
        "hidden-by-default": False,
        "delay-on-join-milliseconds": 0,
        "scoreboards": {
            "default": {
                "title": "Essmakitazo",
                "lines": [
                    "",
                    "⟡ ᴏɴʟɪɴᴇ: %online%",
                    "⟡ ᴘɪɴɢ: %ping%ms",
                    "⟡ ᴛᴘs: %tps%",
                    "",
                    ">____________<",
                    "⟡ domain.name"
                ]
            }
        }
    }
}


def load_or_create_scoreboard_config(plugin_data_folder: str) -> dict:
    config_path = Path(plugin_data_folder) / "scoreboard.yml"

    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_SCOREBOARD_CONFIG, f, default_flow_style=False, allow_unicode=True)
        return DEFAULT_SCOREBOARD_CONFIG

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except UnicodeDecodeError:
        config_path.unlink()
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_SCOREBOARD_CONFIG, f, default_flow_style=False, allow_unicode=True)
        return DEFAULT_SCOREBOARD_CONFIG


def replace_placeholders(line: str, player: Player, plugin) -> str:
    online_players = len(plugin.server.online_players)
    tps = round(plugin.server.current_tps)

    line = line.replace("%online%", str(online_players))
    line = line.replace("%ping%", str(player.ping))
    line = line.replace("%tps%", str(tps))

    return line


def get_active_scoreboard_name(config: dict) -> str:
    scoreboards = config.get("scoreboard", {}).get("scoreboards", {})
    return next(iter(scoreboards.keys())) if scoreboards else "default"


def create_scoreboard_for_player(player: Player, plugin):
    config = load_or_create_scoreboard_config(str(plugin.data_folder))

    if not config.get("scoreboard", {}).get("enabled", False):
        return

    board = player.scoreboard
    scoreboard_name = get_active_scoreboard_name(config)
    scoreboard_config = config.get("scoreboard", {}).get("scoreboards", {}).get(scoreboard_name, {})

    existing_obj = board.get_objective(scoreboard_name)
    if existing_obj:
        existing_obj.unregister()

    title = scoreboard_config.get("title", "Essmakitazo")
    lines = scoreboard_config.get("lines", [])

    obj = board.add_objective(scoreboard_name, Criteria.DUMMY, title)
    obj.set_display(DisplaySlot.SIDE_BAR)

    for idx, line in enumerate(lines):
        display_text = replace_placeholders(line, player, plugin) if line else " " * (idx + 1)
        score = obj.get_score(display_text)
        score.value = idx + 1


def update_scoreboard_for_player(player: Player, plugin):
    config = load_or_create_scoreboard_config(str(plugin.data_folder))

    if not config.get("scoreboard", {}).get("enabled", False):
        return

    board = player.scoreboard
    scoreboard_name = get_active_scoreboard_name(config)
    scoreboard_config = config.get("scoreboard", {}).get("scoreboards", {}).get(scoreboard_name, {})

    existing_obj = board.get_objective(scoreboard_name)
    if existing_obj:
        existing_obj.unregister()

    title = scoreboard_config.get("title", "Essmakitazo")
    lines = scoreboard_config.get("lines", [])

    obj = board.add_objective(scoreboard_name, Criteria.DUMMY, title)
    obj.set_display(DisplaySlot.SIDE_BAR)

    for idx, line in enumerate(lines):
        display_text = replace_placeholders(line, player, plugin) if line else " " * (idx + 1)
        score = obj.get_score(display_text)
        score.value = idx + 1