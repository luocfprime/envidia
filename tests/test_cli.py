import os
from pathlib import Path
from shutil import copytree, rmtree

import pytest
from click.testing import CliRunner

from envidia.core.cli import CLI
from envidia.core.loader import loader


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def test_envd_path(tmpdir):
    template = Path(__file__).parent / "env.d"
    dst = tmpdir / "env.d"
    copytree(template, dst)

    cwd = os.getcwd()
    os.chdir(tmpdir)

    loader.set_env_dir(template)

    yield dst

    os.chdir(cwd)
    rmtree(dst)


def test_env_loading(runner, test_envd_path):
    """Test end-to-end environment variable loading"""
    result = runner.invoke(CLI(loader=loader).create_main_command())

    assert "export CUDA_VISIBLE_DEVICES=0" in result.output  # Updated
    assert "export FOO=baz" in result.output  # Added
    assert "export NAME=proj" in result.output  # Added
    assert "export DOCKER_IMAGE=proj-api" in result.output  # Added
    assert "export IMAGE_URL=proj-api:latest" in result.output  # Added
    assert "alias n='notify'" in result.output  # Added


def test_bootstrap_pre_hook(runner, test_envd_path):
    result = runner.invoke(CLI(loader=loader).create_main_command())
    assert "export HF_TRANSFER=0" in result.output


def test_bootstrap_post_hook(runner, test_envd_path):
    result = runner.invoke(
        CLI(loader=loader).create_main_command(),
        args=["--foo", "/a/none/existent/path"],
    )
    assert result.exit_code != 0
    assert "FOO_PATH must exist" in str(result)
