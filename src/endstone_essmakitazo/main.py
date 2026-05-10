from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from .commands import preloaded_commands, preloaded_handlers, preloaded_permissions
from .config import config_loader
from .utils import scoreboards, fallback_server
from .events import server_events

class Main(Plugin):
    api_version = "0.11"
    commands = preloaded_commands
    permissions = preloaded_permissions
    on_player_join = server_events.on_player_join
    on_player_quit = server_events.on_player_quit
    on_player_kick = server_events.on_player_kick

    def on_load(self) -> None:
        config_loader.load_or_create_config(str(self.data_folder))
        scoreboards.load_or_create_scoreboard_config(str(self.data_folder))
        self.logger.info("✓ Configuración cargada")

    def on_enable(self) -> None:
        self.register_events(self)
        self.server.scheduler.run_task(
            self,
            self.update_placeholders_task,
            delay=0,
            period=20
        )
        # TODO: Agregar un ChunkLeakFixer
        # self.register_events(ChunkLeakFixListener(self))
        self.logger.info("✓ Essentials Maki habilitado")

    def on_disable(self) -> None:
        try:
            fallback_server.transferall_fallback_server(self)
        except Exception as e:
            self.logger.error(
                f"Error en fallback al deshabilitar: {e}"
            )
        self.server.scheduler.cancel_tasks(self)
        self.logger.info("✗ Essentials Maki deshabilitado")

    def on_command(
        self,
        sender: CommandSender,
        command: Command,
        args: list[str]
    ) -> bool:
        handler = preloaded_handlers.get(command.name)
        if handler:
            return handler(self, sender, args)

        return False

    def update_placeholders_task(self) -> None:
        try:
            for player in self.server.online_players:
                scoreboards.update_scoreboard_for_player(
                    player,
                    self
                )
        except Exception as e:
            self.logger.error(
                f"Error actualizando scoreboards: {e}"
            )