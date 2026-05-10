import importlib
import pkgutil
import os

preloaded_commands = {}
preloaded_handlers = {}
preloaded_permissions = {}

def preload_commands():
    commands_path = os.path.dirname(__file__)

    for _, module_name, _ in pkgutil.iter_modules([commands_path]):
        if module_name == "__init__":
            continue

        module = importlib.import_module(
            f"endstone_essmakitazo.commands.{module_name}"
        )

        if hasattr(module, "permissions"):
            preloaded_permissions.update(module.permissions)
        if hasattr(module, "command") and hasattr(module, "handler"):
            for cmd, data in module.command.items():
                preloaded_commands[cmd] = data
                preloaded_handlers[cmd] = module.handler

preload_commands()