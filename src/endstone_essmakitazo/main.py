import asyncio
from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from .commands import preloaded_commands, preloaded_handlers, preloaded_permissions
from .config import config_loader
from .utils import scoreboards, fallback_server
from .events import preloaded_events

class Main(Plugin):
    api_version = "0.11"
    commands = preloaded_commands
    permissions = preloaded_permissions
    for event_name, event_handler in preloaded_events.items():
        locals()[event_name] = event_handler
    def on_load(self) -> None:
        config_loader.load_or_create_config(str(self.data_folder))
        scoreboards.load_or_create_scoreboard_config(str(self.data_folder))
        self.logger.info("✓ Configuración cargada")

    def on_enable(self) -> None:
        self.register_events(self)
        economy_plugin = self.server.plugin_manager.get_plugin("jweconomy")
        if economy_plugin:
            self.economy_api = economy_plugin.get_api()
            self.logger.info("✓ API de JWEconomy integrada")
        else:
            self.economy_api = None
            self.logger.warning("JWEconomy no encontrado, placeholders de economía deshabilitados")
        self.server.scheduler.run_task(
            self,
            self.update_placeholders_task,
            delay=0,
            period=1
        )
        self.logger.info("✓ Essentials Maki habilitado")

    def on_disable(self) -> None:
        fallback_server.transferall_fallback_server(self)
        self.server.scheduler.cancel_tasks(self)
        self.logger.info("✗ Essentials Maki deshabilitado")

    def on_command(self,sender: CommandSender,command: Command,args: list[str]) -> bool:
        handler = preloaded_handlers.get(command.name)
        if handler:
            return handler(self, sender, args)
        return False

    def update_placeholders_task(self) -> None:
        try:
            for player in self.server.online_players:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(scoreboards.show_scoreboard_for_player(player, self))
                loop.close()
        except Exception as e:
            self.logger.error(f"Error actualizando scoreboards: {e}")