from endstone import Player
from endstone.scoreboard import DisplaySlot, Criteria
from pathlib import Path
import yaml

DEFAULT_SCOREBOARD_CONFIG = {
    "scoreboard": {
        "enabled": True,
        "is_hidden": False,
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

SCOREBOARD_CACHE = {}

def load_or_create_scoreboard_config(plugin_data_folder: str) -> dict:
    global SCOREBOARD_CACHE
    config_path = Path(plugin_data_folder) / "scoreboard.yml"
    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                DEFAULT_SCOREBOARD_CONFIG,
                f,
                default_flow_style=False,
                allow_unicode=True
            )
        SCOREBOARD_CACHE = DEFAULT_SCOREBOARD_CONFIG
        return SCOREBOARD_CACHE
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            SCOREBOARD_CACHE = yaml.safe_load(f)
    except UnicodeDecodeError:
        config_path.unlink()
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(
                DEFAULT_SCOREBOARD_CONFIG,
                f,
                default_flow_style=False,
                allow_unicode=True
            )
        SCOREBOARD_CACHE = DEFAULT_SCOREBOARD_CONFIG
    return SCOREBOARD_CACHE

def replace_placeholders(line: str,player: Player,plugin) -> str:
    online_players = len(plugin.server.online_players)
    tps = round(plugin.server.current_tps)
    line = line.replace("%online%", str(online_players))
    line = line.replace("%ping%", str(player.ping))
    line = line.replace("%tps%", str(tps))
    return line

def get_active_scoreboard_name(config: dict) -> str:
    scoreboards = (config.get("scoreboard", {}).get("scoreboards", {}))
    return (
        next(iter(scoreboards.keys()))
        if scoreboards
        else "default"
    )

def create_scoreboard_for_player(player: Player,plugin):
    config = SCOREBOARD_CACHE
    if not config.get("scoreboard",{}).get("enabled", False):
        return
    board = player.scoreboard
    scoreboard_name = f"sb_{player.name}"
    default_score = get_active_scoreboard_name(config)
    scoreboard_config = (config.get("scoreboard", {}).get("scoreboards", {}).get(default_score, {}))
    existing_obj = board.get_objective(scoreboard_name)
    if existing_obj:
        return
    title = scoreboard_config.get("title","Essmakitazo")
    lines = scoreboard_config.get("lines", [])
    obj = board.add_objective(scoreboard_name,Criteria.DUMMY,title)
    obj.set_display(DisplaySlot.SIDE_BAR)
    for idx, line in enumerate(lines):
        display_text = (
            replace_placeholders(
                line,
                player,
                plugin
            )
            if line
            else " " * (idx + 1)
        )
        score = obj.get_score(display_text)
        score.value = idx + 1

def update_scoreboard_for_player(player: Player, plugin):
    config = SCOREBOARD_CACHE
    if not config.get("scoreboard", {}).get("enabled", False):
        return
    board = player.scoreboard
    scoreboard_name = f"sb_{player.name}"
    default_score = get_active_scoreboard_name(config)
    scoreboard_config = (
        config.get("scoreboard", {})
        .get("scoreboards", {})
        .get(default_score, {})
    )
    obj = board.get_objective(scoreboard_name)
    if obj:
        obj.unregister()
    create_scoreboard_for_player(player, plugin)