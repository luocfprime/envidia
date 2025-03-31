import sys
from pathlib import Path
from shlex import quote
from typing import Callable

import click
from cookiecutter.main import cookiecutter

from envidia import __version__
from envidia.core.loader import Loader


class CLI:
    def __init__(self, loader: Loader):
        self.loader = loader
        self._bootstrap_loaded = False

    def create_main_command(self) -> click.Command:
        try:
            self.loader.set_env_dir(Path.cwd() / "env.d")
            self.loader.load_bootstrap()
            self._bootstrap_loaded = True
        except FileNotFoundError:  # env.d is not initialized yet.
            pass

        @click.group(
            context_settings={"help_option_names": ["-h", "--help"]},
            invoke_without_command=True,
        )
        @click.pass_context
        @self._add_dynamic_options
        @click.version_option(__version__)
        def cli(ctx, **kwargs):
            """Load from env.d and generate shell script. Run `source <(envidia)` or simply `source <(e)` to load environment context."""
            if not self._bootstrap_loaded and ctx.invoked_subcommand not in [
                "init",
                "install",
            ]:
                click.echo(
                    "env.d is not initialized yet. Run `envidia init` to initialize."
                )
                raise click.exceptions.Exit()
            if ctx.invoked_subcommand is None:
                commands = self.loader.generate_shell_commands(ctx.params)
                click.echo(commands)

        @cli.command()
        @click.argument("template", type=click.Path(exists=True))
        def init(template):
            """Initialize new environment template using cookiecutter"""
            cookiecutter(template)
            click.echo(f"Successfully initialized template from {template}")

        @cli.command()
        @click.option(
            "--alias",
            default="es",
            help="Alias to use for shell to load env.d files",
        )
        def install(alias):
            """Output shell code to create sourcing alias. Put `eval "$(envidia install)"` inside your .bashrc or .profile"""

            cli_path = quote(sys.argv[0])
            click.echo(
                f"alias {alias}='function _source_envidia() {{ source <({cli_path} \"$@\"); }}; _source_envidia'"
            )

        @cli.command()
        @click.pass_context
        @self._add_dynamic_options
        def show(ctx, **kwargs):
            """Show execution order"""
            # Generate commands first to populate call log
            self.loader.generate_shell_commands(ctx.params)
            for i, entry in enumerate(self.loader.call_log):
                click.echo(f"[{i}] {entry}")

        return cli

    def _add_dynamic_options(self, f: Callable) -> Callable:
        """Dynamically add registered options as Click parameters."""
        for name, config in self.loader.registered_options.items():
            f = click.option(
                f"--{name}",
                type=str,
                default=config["default"],
                help=config["help"],
            )(f)
        return f
