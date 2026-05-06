from endstone import Player, ColorFormat
from endstone.form import MessageForm
from endstone.level import Location
from endstone.scheduler import Task
from dataclasses import dataclass

TPA_TIMEOUT_TICKS = 100  # 5 segundos

@dataclass
class TpaRequest:
    sender: Player
    task: Task

tpa_requests: dict[str, TpaRequest] = {}


def is_moving(player: Player, start_loc: Location, tolerance: float = 0.1) -> bool:
    loc = player.location
    return (
        abs(loc.x - start_loc.x) > tolerance or
        abs(loc.y - start_loc.y) > tolerance or
        abs(loc.z - start_loc.z) > tolerance
    )


def _start_movement_task(plugin, requester: Player, target: Player):
    start_loc = requester.location
    ticks_elapsed = [0]

    def tick():
        ticks_elapsed[0] += 1

        if plugin.server.get_player(requester.name) is None:
            target.send_message(f"{ColorFormat.RED}{requester.name} se desconectó")
            task_ref[0].cancel()
            return

        if plugin.server.get_player(target.name) is None:
            task_ref[0].cancel()
            return

        if is_moving(requester, start_loc):
            requester.send_message(f"{ColorFormat.RED}Te moviste, teleporte cancelado")
            target.send_message(f"{ColorFormat.RED}Teleporte de {requester.name} cancelado (se movió)")
            task_ref[0].cancel()
            return

        if ticks_elapsed[0] >= TPA_TIMEOUT_TICKS:
            requester.teleport(target.location)
            requester.send_message(f"{ColorFormat.GREEN}¡Teletransportado a {target.name}!")
            target.send_message(f"{ColorFormat.GREEN}{requester.name} fue teletransportado a ti")
            task_ref[0].cancel()

    task_ref: list[Task] = [plugin.server.scheduler.run_task(plugin, tick, delay=0, period=1)]


def _on_form_response(plugin, requester: Player, target: Player, btn: int | None):
    request = tpa_requests.pop(target.name, None)
    if request is None:
        return

    if not request.task.is_cancelled:
        request.task.cancel()

    if btn != 0:
        requester.send_message(f"{ColorFormat.RED}{target.name} rechazó tu petición")
        target.send_message(f"{ColorFormat.RED}Rechazaste la petición de {requester.name}")
        return

    requester.send_message(f"{ColorFormat.GREEN}{target.name} aceptó. No te muevas por 10 segundos...")
    target.send_message(f"{ColorFormat.GREEN}Aceptaste. {requester.name} llegará en 10 segundos")
    _start_movement_task(plugin, requester, target)


def send_tpa_form(plugin, sender: Player, target: Player):
    def expire():
        if target.name in tpa_requests:
            tpa_requests.pop(target.name)
            sender.send_message(f"{ColorFormat.RED}Tu petición a {target.name} expiró")
            target.send_message(f"{ColorFormat.RED}La petición de {sender.name} expiró")
        expire_ref[0].cancel()

    expire_ref: list[Task] = [plugin.server.scheduler.run_task(plugin, expire, delay=TPA_TIMEOUT_TICKS)]
    tpa_requests[target.name] = TpaRequest(sender=sender, task=expire_ref[0])

    form = MessageForm(
        title="Petición de teleporte",
        content=f"{ColorFormat.YELLOW}{sender.name}{ColorFormat.WHITE} quiere teletransportarse a ti",
        button1=f"{ColorFormat.GREEN}Aceptar",
        button2=f"{ColorFormat.RED}Rechazar",
    )
    form.on_submit = lambda p, btn: _on_form_response(plugin, sender, p, btn)
    form.on_close = lambda p: _on_form_response(plugin, sender, p, None)

    target.send_form(form)