import time
from endstone import Player, ColorFormat
from endstone.form import ActionForm

TPA_REQUESTS = {}

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
        form.add_button(text=player.name, icon="textures/ui/Friend1", on_click=create_callback())
    form.add_button(text=f"{ColorFormat.RED}Cerrar")
    sender.send_form(form)

def send_tpa_request(sender: Player, target: Player) -> None:
    TPA_REQUESTS[target.unique_id] = {
        "sender_uuid": sender.unique_id,
        "sender_name": sender.name,
        "timestamp": time.time()
    }
    target.send_message(
        f"{ColorFormat.YELLOW}{sender.name} {ColorFormat.WHITE}"
        f"quiere teletransportarse a ti. Usa {ColorFormat.GREEN}/tpaccept "
        f"{ColorFormat.WHITE}para aceptar ({ColorFormat.RED}expira en 30s{ColorFormat.WHITE})"
    )
    sender.send_message(
        f"{ColorFormat.GREEN}Solicitud enviada a {ColorFormat.WHITE}"
        f"{target.name}"
    )

def get_pending_request(player_uuid):
    request = TPA_REQUESTS.get(player_uuid)
    if request is None:
        return None
    if time.time() - request["timestamp"] > 30:
        del TPA_REQUESTS[player_uuid]
        return None
    return request

def remove_request(player_uuid):
    TPA_REQUESTS.pop(player_uuid, None)