from endstone.plugin import Plugin
from endstone.command import Command, CommandSender
from endstone.permissions import PermissionDefault

from endstone_essmakitazo.commands import lobby_command, reload_command, saveloc_commands, teleport_commands
from endstone_essmakitazo.config import config_loader
from endstone_essmakitazo.utils import scoreboards, fallback_server
from endstone_essmakitazo.events import server_events
from endstone_essmakitazo.utils.chunk_leak_fix import ChunkLeakFixListener

class Main(Plugin):
    api_version = "0.11"

    commands = {
        "lobby": {
            "description": "Ir al lobby",
            "usages": ["/lobby"],
            "permissions": ["endstone_essmakitazo.command.lobby"],
        },
        "essreload": {
            "description": "Recargar la configuración",
            "usages": ["/essreload"],
            "permissions": ["endstone_essmakitazo.command.essreload"],
        },
        "spawn": {
            "description": "Ir al spawn",
            "usages": ["/spawn"],
            "permissions": ["endstone_essmakitazo.command.spawn"],
        },
        "setspawn": {
            "description": "Establece el spawn",
            "usages": ["/setspawn"],
            "permissions": ["endstone_essmakitazo.command.setspawn"],
        },
        "tpa": {
            "description": "Te transporta a otro jugador",
            "usages": ["/tpa <jugador>"],
            "permissions": ["endstone_essmakitazo.command.teleport.tpa"],
        },
        "tpaccept": {
            "description": "Aceptas una petición de teletransporte de otro jugador",
            "usages": ["/tpaccept"],
            "permissions": ["endstone_essmakitazo.command.teleport.tpaccept"],
        },
        "tpdeny": {
            "description": "Denegas una petición de teletransporte de otro jugador",
            "usages": ["/tpdeny"],
            "permissions": ["endstone_essmakitazo.command.teleport.tpdeny"],
        },
        "sethome": {
            "description": "Establece tu hogar",
            "usages": ["/sethome"],
            "permissions": ["endstone_essmakitazo.command.teleport.sethome"],
        },
        "home": {
            "description": "Vas a tu hogar",
            "usages": ["/home"],
            "permissions": ["endstone_essmakitazo.command.teleport.home"],
        }
    }

    permissions = {
        "endstone_essmakitazo.command.spawn": {
            "description": "Usar el comando /spawn",
            "default": PermissionDefault.TRUE,
        },
        "endstone_essmakitazo.command.lobby": {
            "description": "Usar el comando /lobby",
            "default": PermissionDefault.TRUE,
        },
        "endstone_essmakitazo.command.teleport.tpa": {
            "description": "Usar el comando /tpa",
            "default": PermissionDefault.TRUE,
        },
        "endstone_essmakitazo.command.teleport.sethome": {
            "description": "Usar el comando /sethome",
            "default": PermissionDefault.TRUE,
        },
        "endstone_essmakitazo.command.teleport.home": {
            "description": "Usar el comando /home",
            "default": PermissionDefault.TRUE,
        },
        "endstone_essmakitazo.command.essreload": {
            "description": "Usar el comando /essreload",
            "default": PermissionDefault.OP,
        },
        "endstone_essmakitazo.command.setspawn": {
            "description": "Usar el comando /setspawn",
            "default": PermissionDefault.OP,
        }
    }

    def on_load(self) -> None:
        config_loader.load_or_create_config(str(self.data_folder))
        scoreboards.load_or_create_scoreboard_config(str(self.data_folder))
        self.logger.info("✓ Configuración cargada")

    def on_enable(self) -> None:
        self.register_events(self)
        self.server.scheduler.run_task(
            self,
            self.update_placeholders_task,
            0,
            20
        )
        self.register_events(ChunkLeakFixListener(self))
        self.logger.info("✓ Essentials Maki habilitado")

    def on_disable(self) -> None:
        try:
            fallback_server.transferall_fallback_server(self)
        except Exception as e:
            self.logger.error(f"Error en fallback al deshabilitar: {e}")

        self.server.scheduler.cancel_tasks(self)
        self.logger.info("✗ Essentials Maki deshabilitado")

    _command_map = {
        "lobby": lobby_command.execute,
        "essreload": reload_command.execute,
        "setspawn": saveloc_commands.set_spawn,
        "spawn": teleport_commands.spawn,
        "tpa": teleport_commands.tpa,
        "home": teleport_commands.home,
        # "sethome" : teleport_commands.sethome  creando lógica
    }

    def on_command(self, sender: CommandSender, command: Command, args: list[str]) -> bool:
        handler = self._command_map.get(command.name)
        if handler:
            return handler(sender, args, self)
        return True

    on_player_join = server_events.on_player_join
    on_player_quit = server_events.on_player_quit
    on_player_kick = server_events.on_player_kick

    def update_placeholders_task(self) -> None:
        try:
            for player in self.server.online_players:
                scoreboards.update_scoreboard_for_player(player, self)
        except Exception as e:
            self.logger.error(f"Error actualizando scoreboards: {e}")