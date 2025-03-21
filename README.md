# Envidia

![Unit Tests](https://github.com/fkcptlst/envidia/actions/workflows/unit-test-matrix.yml/badge.svg)
![Python Versions](https://img.shields.io/pypi/pyversions/envidia)
![PyPI](https://img.shields.io/pypi/v/envidia)

Envidia is a command-line interface (CLI) tool for loading project-level environment variables and simplifying the
setting of long environment variables with aliases.

## Table of Contents

- [Envidia](#envidia)
    - [Table of Contents](#table-of-contents)
    - [Install](#install)
    - [Features](#features)
        - [1. Loading `.env` from a directory](#1-loading-env-from-a-directory)
        - [2. Set Environment Variables via Alias](#2-set-environment-variables-via-alias)
        - [3. Integration with Cookiecutter](#3-integration-with-cookiecutter)
        - [4. Pre-load and Post-load Hooks](#4-pre-load-and-post-load-hooks)
    - [License](#license)

## Install

To install Envidia, use pip:

```bash
pip install envidia
```

## Features

### 1. Loading `.env` from a directory

Envidia allows you to load environment variables from a directory, replacing long and verbose declarations with simple
commands.

![load-demo](assets/load.gif)

### 2. Set Environment Variables via Alias

Setting environment variables manually can be cumbersome. Envidia provides a convenient way to set them via alias.

❌: `export CUDA_VISIBLE_DEVICES="0"`

✅: `source <(e --cuda 0)` or simply `es --cuda 0` if you have `eval $(envidia install)` in your `.bashrc` or `.zshrc`.

Put the following line in your `.bashrc` or `.zshrc`:

```bash
eval "$(envidia install --alias es)"
```

Specify which option is related to which environment variable in `env.d/bootstrap.py`:

```python
from envidia import register_option

register_option("cuda", "CUDA_VISIBLE_DEVICES", default="0")
```

Use `es` to set environment variables specified in `env.d`. ( es is short for "env set").

![alias-demo](assets/alias.gif)

### 3. Integration with [Cookiecutter](https://github.com/cookiecutter/cookiecutter)

Pack your project environment variables as a cookiecutter template to reuse them across different projects.

![cookiecutter-demo](assets/cookiecutter.gif)

### 4. Pre-load and Post-load Hooks

Use hooks to verify path variables or add extra variables into the environment.

```python
# env.d/bootstrap.py
from pathlib import Path

from envidia import Loader, register_option

register_option("cuda", "CUDA_VISIBLE_DEVICES", default="0")
register_option("foo", "FOO_PATH", default=".")


def pre_load(loader: Loader):
    # add extra variable into the environment
    # if hf_transfer is installed, set HF_TRANSFER=1
    if is_package_installed("hf_transfer"):
        loader.env_registry["HF_TRANSFER"] = "1"
    else:
        loader.env_registry["HF_TRANSFER"] = "0"


def post_load(loader: Loader):
    # validate a path must exist
    if not Path(loader.env_registry.get("FOO_PATH", "")).exists():
        raise RuntimeError("FOO_PATH must exist")
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
