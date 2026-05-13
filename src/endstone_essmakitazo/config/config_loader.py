import yaml
from pathlib import Path

DEFAULT_CONFIG = {
    "plugin": {
        "name": "endstone-essmakitazo",
        "version": "0.1.0"
    },
    "servers": {
        "lobby": {
            "host": "localhost",
            "port": 19132
        }
    },
    "spawn": {
        "location": {
            "dimension": "Overworld",
            "x": 0,
            "y": 64,
            "z": 0
        }
    }
}


def get_config_path(plugin_data_folder: str) -> Path:
    return Path(plugin_data_folder) / "config.yml"


def load_or_create_config(plugin_data_folder: str) -> dict:
    config_path = get_config_path(plugin_data_folder)

    if not config_path.exists():
        config_path.parent.mkdir(parents=True, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)
        return DEFAULT_CONFIG

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)
    except UnicodeDecodeError:
        config_path.unlink()
        with open(config_path, "w", encoding="utf-8") as f:
            yaml.dump(DEFAULT_CONFIG, f, default_flow_style=False, allow_unicode=True)
        return DEFAULT_CONFIG