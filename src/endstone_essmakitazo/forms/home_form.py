from pathlib import Path
import yaml
from endstone import Player, ColorFormat
from endstone.level import Location
from endstone.form import ActionForm

def open_home_form(plugin, sender: Player) -> None:
    user_path = Path(plugin.data_folder) / "userdata"
    user_file = user_path / f"{sender.unique_id}.yml"
    if not user_file.exists():
        sender.send_message(f"{ColorFormat.GREEN}No tienes homes guardados, usa /sethome primero")
        return
    with open(user_file, "r", encoding="utf-8") as file:
        config = yaml.safe_load(file) or {}
    homes = config.get("home", {})
    if not homes:
        sender.send_message(f"{ColorFormat.GREEN}No tienes homes guardados, usa /sethome primero")
        return
    form = ActionForm(
        title="Tus Homes",
        content="Selecciona un home para teletransportarte:"
    )
    for home_names in homes:
        form.add_button(text=f"{ColorFormat.GREEN}{home_names}")
    form.add_button(text=f"{ColorFormat.RED}Cerrar")
    def on_submit(player: Player, selection: int) -> None:
        if selection >= len(homes):
            return
        home_name = list(homes.keys())[selection]
        user_home = homes[home_name]
        x = user_home.get("x")
        y = user_home.get("y")
        z = user_home.get("z")
        dimension_id = user_home.get("dimension", "minecraft:overworld")
        dimension = plugin.server.level.get_dimension(dimension_id)
        config["last_position"] = {
            "location": {
                "x": round(player.location.x, 2),
                "y": round(player.location.y, 2),
                "z": round(player.location.z, 2),
                "dimension": str(player.location.dimension.name)
            }
        }
        with open(user_file, "w", encoding="utf-8") as fl:
            yaml.dump(config, fl, allow_unicode=True, default_flow_style=False)
        home_location = Location(dimension, x, y, z)
        player.teleport(home_location)
        player.send_message(f"{ColorFormat.GREEN}¡Has sido transportado a tu home {home_name}!")

    form.on_submit = on_submit
    sender.send_form(form)