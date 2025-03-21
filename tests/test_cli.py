import os
import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest
from click.testing import CliRunner

from envidia.core.cli import CLI
from envidia.core.loader import Loader


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def mock_loader(mocker):
    loader = mocker.MagicMock(spec=Loader)
    loader.call_log = []
    loader.registered_options = {}
    loader.env_registry = {}
    return loader


def test_init_command(runner, tmp_path, mock_loader):
    """Test template initialization with cookiecutter"""
    with runner.isolated_filesystem() as td:
        test_template = Path(td) / "template"
        test_template.mkdir()

        with patch("envidia.core.cli.cookiecutter") as mock_cookiecutter:
            result = runner.invoke(
                CLI(mock_loader).create_main_command(),
                ["init", str(test_template)],
                obj={"loader": mock_loader},
            )

            mock_cookiecutter.assert_called_once_with(str(test_template))
            assert result.exit_code == 0


def test_install_alias(runner, tmp_path, mock_loader):
    """Test shell alias installation"""
    shell_rc = tmp_path / ".testrc"
    shell_rc.touch()

    with patch.object(sys, "argv", ["envidia"]):
        result = runner.invoke(
            CLI(mock_loader).create_main_command(),
            ["install", "--alias", "es", str(shell_rc)],
            obj={"loader": mock_loader},
        )


def test_show_execution_order(runner, mock_loader):
    """Test execution order logging"""
    mock_loader.call_log = ["load env file: test.env", "process cli option: gpu"]

    result = runner.invoke(
        CLI(mock_loader).create_main_command(), ["show"], obj={"loader": mock_loader}
    )


def test_dynamic_options(runner, mock_loader):
    """Test registration and usage of dynamic options"""
    mock_loader.registered_options = {
        "cuda": {"help": "CUDA devices", "env_var": "CUDA_VISIBLE_DEVICES"}
    }

    # Test help output
    result = runner.invoke(
        CLI(mock_loader).create_main_command(),  # Fixed
        ["--help"],
        obj={"loader": mock_loader},
    )

    # Test option parsing
    result = runner.invoke(
        CLI(mock_loader).create_main_command(),  # Fixed
        ["--cuda", "0,1", "show"],
        obj={"loader": mock_loader},
    )


def test_error_handling(runner, mock_loader):
    """Test error conditions"""
    # Invalid init path
    result = runner.invoke(
        CLI(mock_loader).create_main_command(),  # Fixed
        ["init", "/invalid/path"],
        obj={"loader": mock_loader},
    )

    # Missing subcommand
    result = runner.invoke(
        CLI(mock_loader).create_main_command(), obj={"loader": mock_loader}  # Fixed
    )


def test_core_functionality(runner, tmp_path, mock_loader):  # Use fixture runner
    """Test environment variable generation"""
    # Setup test environment
    env_file = tmp_path / "test.env"
    env_file.write_text("FOO=bar\nBAZ=qux")

    mock_loader.get_env_file_paths.return_value = [env_file]
    mock_loader.generate_shell_commands.return_value = "export FOO=bar\nexport BAZ=qux"

    result = runner.invoke(
        CLI(mock_loader).create_main_command(), obj={"loader": mock_loader}  # Fixed
    )
