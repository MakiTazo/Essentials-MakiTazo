from endstone import Player
from pathlib import Path
import yaml

DEFAULT_SCOREBOARD_CONFIG = {
    "scoreboard": {
        "enabled": True,
        "border": False,
        "scoreboards": {
            "default": {
                "title": "Essmakitazo",
                "lines": [
                    "",
                    "⟡ ᴏɴʟɪɴᴇ: %online%",
                    "⟡ ᴘɪɴɢ: %ping%ms",
                    "⟡ ᴛᴘs: %tps%",
                    "⟡ ʙᴀʟᴀɴᴄᴇ: %balance%",
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

async def replace_placeholders(line: str, player: Player, plugin) -> str:
    online_players = len(plugin.server.online_players)
    tps = round(plugin.server.current_tps)
    line = line.replace("%online%", str(online_players))
    line = line.replace("%ping%", str(player.ping))
    line = line.replace("%tps%", str(tps))
    if plugin.economy_api is not None:
        try:
            balance = await plugin.economy_api.get_balance(str(player.unique_id))
            symbol = plugin.economy_api.currency_symbol
            line = line.replace("%balance%", f"{symbol}{balance:.2f}")
        except Exception as e:
            line = line.replace("%balance%", "N/A")
            plugin.logger.info(f"{e}")
    return line

def get_active_scoreboard_name(config: dict) -> str:
    scoreboards = config.get("scoreboard", {}).get("scoreboards", {})
    return next(iter(scoreboards.keys())) if scoreboards else "default"


def build_scoreboard_text(title: str,lines: list[str],use_border: bool = True,show_logo: bool = True) -> str:
    header = "§s§c§o§r§e§b§o§a§r§d§r"
    border = (
        "§w§b§p§a§o§r"
        if use_border
        else "§n§b§p§a§o§r"
    )
    logo = "§l§o§g§o§r" if show_logo else ""
    content = [header, border, logo, title]
    for line in lines:
        content.append(line if line else " ")
    return "\n".join(content)

async def show_scoreboard_for_player(player: Player, plugin):
    config = SCOREBOARD_CACHE
    if not config.get("scoreboard", {}).get("enabled", False):
        return
    default_score = get_active_scoreboard_name(config)
    scoreboard_config = config.get("scoreboard", {}).get("scoreboards", {}).get(default_score, {})
    lines_config = scoreboard_config.get("lines", [])
    title = scoreboard_config.get("title", "Essmakitazo")
    use_border = config.get("scoreboard", {}).get("border", True)
    formatted_lines = []
    for line in lines_config:
        if line:
            display_text = await replace_placeholders(line, player, plugin)
            formatted_lines.append(display_text)
        else:
            formatted_lines.append(" ")
    scoreboard_text = build_scoreboard_text(title, formatted_lines, use_border=use_border, show_logo=True)
    player.send_title(scoreboard_text, "", fade_in=0, stay=999999, fade_out=0)

def remove_scoreboard_for_player(player: Player):
    player.reset_title()