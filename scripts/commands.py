import asyncio
import importlib
import importlib.util
import inspect
import pkgutil
from dataclasses import dataclass
from time import perf_counter
from typing import Set

import typer
from injector import Injector
from rich import print

from container.factory import create_command_injector
from core.bootstrap import bootstrap_runtime, bootstrap_shutdown
from core.logger.factory import create_app_logger

COMMANDS_MODULE = "commands"


@dataclass
class RunCommandOptions:
    injector: Injector


app = typer.Typer(help="Run available commands.")
logger = create_app_logger()


@app.command(
    name="run",
    help="Run a specific command by name.",
    context_settings={"allow_extra_args": True, "ignore_unknown_options": True},
)
def run(ctx: typer.Context, name: str):
    _check_command_exists(name)
    from core.bootstrap import bootstrap_runtime

    bootstrap_runtime()
    asyncio.run(_run_command(name, extra_args=ctx.args))


@app.callback()
def callback():
    """
    Setup callback function for removing group command when running the script directly.
    """

    pass


def _run_pre_command_hook():
    bootstrap_runtime()
    injector = create_command_injector()
    return RunCommandOptions(injector=injector)


async def _run_post_command_hook(options: RunCommandOptions):
    await bootstrap_shutdown(injector=options.injector)


def _get_available_commands() -> Set[str]:
    spec = importlib.util.find_spec(COMMANDS_MODULE)
    if not spec or not spec.submodule_search_locations:
        return set()

    return {
        module.name
        for module in pkgutil.iter_modules(spec.submodule_search_locations)
        if not module.name.startswith("_")
    }


def _check_command_exists(name: str) -> None:
    available_commands = _get_available_commands()
    if not available_commands:
        print("[bold yellow]No available commands found.[/bold yellow]")
        raise typer.Exit(1)

    if name not in available_commands:
        formated_available_commands = "\n".join(
            f"> {command}" for command in available_commands
        )
        print(
            f"[bold red]Command named '{name}' not found.[/bold red]\n"
            "Available commands:\n"
            f"{formated_available_commands}"
        )
        raise typer.Exit(1)


async def _run_command(name: str, extra_args: list[str] | None = None) -> None:
    command_module = importlib.import_module(f"{COMMANDS_MODULE}.{name}")
    if hasattr(command_module, "execute") and callable(command_module.execute):
        options = _run_pre_command_hook()

        logger.info(f"Running command: {name}")
        start_time = perf_counter()

        sig = inspect.signature(command_module.execute)
        kwargs = {"injector": options.injector}
        if "args" in sig.parameters:
            kwargs["args"] = extra_args or []
        elif "extra_args" in sig.parameters:
            kwargs["extra_args"] = extra_args or []

        if inspect.iscoroutinefunction(command_module.execute):
            await command_module.execute(**kwargs)
        else:
            command_module.execute(**kwargs)

        elapsed_time = perf_counter() - start_time
        logger.info(f"Command '{name}' finished in {elapsed_time:.2f} seconds.")

        await _run_post_command_hook(options)
        raise typer.Exit(0)

    print(
        f"[bold red]Command '{name}' does not have a callable 'execute' function.[/bold red]"
    )
    raise typer.Exit(1)


def main():
    app()


if __name__ == "__main__":
    main()
