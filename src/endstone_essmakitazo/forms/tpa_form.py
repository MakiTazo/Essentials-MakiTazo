from endstone import Player, ColorFormat
from endstone.form import ActionForm

def open_tpa_form(sender: Player) -> None:
    online_players = [p for p in sender.server.online_players if p.unique_id != sender.unique_id]
    if not online_players:
        sender.send_message(f"{ColorFormat.RED}No hay jugadores disponibles para enviar solicitud")
        return
    form = ActionForm(
        title="Solicitud de Teletransporte",
        content="Selecciona un jugador para enviar solicitud de TPA:"
    )
    for player in online_players:
        def create_callback(target=player):
            def on_click(clicker: Player) -> None:
                send_tpa_request(clicker, target)
            return on_click
        form.add_button(text=player.name, on_click=create_callback())
    form.add_button(text=f"{ColorFormat.RED}Cerrar")
    sender.send_form(form)

def send_tpa_request(sender: Player, target: Player) -> None:
    target.send_message(
        f"{ColorFormat.YELLOW}{sender.name} {ColorFormat.WHITE}"
        f"quiere teletransportarse a ti. Usa {ColorFormat.GREEN}/tpaccept "
        f"{ColorFormat.WHITE}para aceptar"
    )
    sender.send_message(
        f"{ColorFormat.GREEN}Solicitud enviada a {ColorFormat.WHITE}"
        f"{target.name}"
    )