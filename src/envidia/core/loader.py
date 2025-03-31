import importlib.util
from itertools import chain
from pathlib import Path
from shlex import quote
from typing import Any, Callable, Dict, List, Optional, Union

import natsort
from dotenv import dotenv_values


class Loader:
    def __init__(self):
        self.load_sequence_fn: Callable[[List[Path]], List[Path]] = natsort.natsorted
        self.env_dir = None
        self.registered_options = {}
        self.env_registry = {}
        self.bootstrap = None
        self.call_log = []
        self._bootstrap_loaded = False

    def set_env_dir(self, env_dir: Union[str, Path]):
        self.env_dir = Path(env_dir)

    def load_bootstrap(self):
        if self._bootstrap_loaded:
            return

        if not self.env_dir.exists():
            raise FileNotFoundError(
                f"Environment directory {self.env_dir} does not exist"
            )

        if (self.env_dir / "bootstrap.py").exists():
            spec = importlib.util.spec_from_file_location(
                "bootstrap", self.env_dir / "bootstrap.py"
            )
            bootstrap = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(bootstrap)

            self.bootstrap = bootstrap

            # Run pre_load hooks
            if hasattr(self.bootstrap, "pre_load"):
                self._log_called("run pre_load hooks")
                self.bootstrap.pre_load(self)

        self._bootstrap_loaded = True

    def get_env_file_paths(self):
        env_files = chain(
            self.env_dir.glob("*.env"),
            self.env_dir.glob(".env.*"),
        )
        sorted_files = self.load_sequence_fn([p for p in env_files if p.exists()])
        return sorted_files

    def get_script_paths(self):
        script_files = chain(
            self.env_dir.glob("*.sh"),
            self.env_dir.glob("*.bash"),
            self.env_dir.glob(".bashrc"),
            self.env_dir.glob(".zshrc"),
            self.env_dir.glob("*.zsh"),
            self.env_dir.glob(".profile"),
            self.env_dir.glob(".bash_profile"),
            self.env_dir.glob(".zprofile"),
            self.env_dir.glob(".profile.d/*.sh"),
        )
        sorted_files = self.load_sequence_fn([p for p in script_files if p.exists()])
        return sorted_files

    def _load_env_files_to_registry(self) -> None:
        """Load environment variables into registry"""
        sorted_files = self.get_env_file_paths()
        for env_file in sorted_files:
            self._log_called(f"load env file: {env_file}")
            self.env_registry.update(dotenv_values(env_file))

    def generate_shell_commands(self, options: Dict[str, Any]) -> str:
        """
        Steps:
            1. Load from cli options
            2. Load env
            3. Load scripts
            4. Run post_load hooks
        Args:
            options:

        Returns:

        """
        commands = []

        # 1. Load from cli options
        self._process_cli_options(options)

        # 3. Load env
        self._load_env_files_to_registry()
        commands.extend(
            [
                f"export {env_var}={quote(value)}"
                for env_var, value in self.env_registry.items()
                if value is not None
            ]
        )

        # 4. Load scripts
        for script_path in self.get_script_paths():
            with open(script_path, "r") as f:
                self._log_called(f"load script: {script_path}")
                commands.append(f.read().strip("\n"))

        # 5. Run post_load hooks
        if self.bootstrap and hasattr(self.bootstrap, "post_load"):
            self._log_called("run post_load hooks")
            self.bootstrap.post_load(self)

        return "\n".join(commands)

    def _process_cli_options(self, options: Dict[str, Any]):
        for opt, value in options.items():
            if opt in self.registered_options:
                self._log_called(f"process cli option: {opt}")
                if value is None:
                    self._log_called(f"ignoring cli option as it is None: {opt}")
                    self.env_registry[self.registered_options[opt]["env_var"]] = None
                    continue
                self.env_registry[self.registered_options[opt]["env_var"]] = (
                    self._transform_value(opt, value)
                )

    def _transform_value(self, opt: str, value: Any) -> str:
        transformer = self.registered_options[opt].get("transform")
        return str(transformer(value)) if transformer else str(value)

    def _log_called(self, text: str):
        self.call_log.append(text)

    def register_option(
        self,
        name: str,
        env_var: str,
        default: Optional[str] = None,
        transform: Callable = lambda x: x,
        help: str = "Sets {env_var} environment variable.",
    ) -> None:
        """Register a CLI option to environment variable mapping.

        Args:
            name: CLI option name (without --)
            env_var: Target environment variable
            default: Default value of the environment variable. If None, this environment variable will not be set.
            transform: Function to transform option value
            help: help message to display when `envidia -h`

        """
        self.registered_options[name] = {
            "env_var": env_var,
            "transform": transform,
            "default": default,
            "help": help.format(env_var=env_var),
        }

    def set_load_sequence_fn(
        self, load_sequence_fn: Callable[[List[Path]], List[Path]]
    ):
        self.load_sequence_fn = load_sequence_fn


loader = Loader()
