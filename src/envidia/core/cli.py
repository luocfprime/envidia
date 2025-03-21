import sys
from shlex import quote
from typing import Callable

import click
from cookiecutter.main import cookiecutter

from envidia.core.loader import Loader


class CLI:
    def __init__(
        self,
        loader: Loader,
    ):
        self.loader = loader
        try:
            self.loader.load_bootstrap()
        except FileNotFoundError:  # env.d is not initialized yet
            pass

    def create_main_command(self) -> click.Command:

        @click.group(
            context_settings={"help_option_names": ["-h", "--help"]},
            invoke_without_command=True,
        )
        @click.pass_context
        @self._add_dynamic_options
        def cli(ctx, **kwargs):
            """Load from env.d and generate shell script. Run `source <(envidia)` or simply `source <(e)` to load environment context."""
            if ctx.invoked_subcommand is None:
                self.loader.load_bootstrap()
                commands = self.loader.generate_shell_commands(ctx.params)
                click.echo(commands)

        @cli.command()
        @click.argument("path", type=click.Path(exists=True))
        def init(path):
            """Initialize new environment template using cookiecutter"""
            cookiecutter(path)
            click.echo(f"Successfully initialized template from {path}")

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
        def show(ctx):
            """Show execution order"""
            # Generate commands first to populate call log
            self.loader.load_bootstrap()
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
                help=config["help"],
            )(f)
        return f
