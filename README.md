# Envidia

Envidia is a command-line interface (CLI) tool for loading project level environment variables, and making alias for long environment variable names.

## Install

```bash
pip install envidia
```

## Features

### 1. Loading `.env` from a directory

You can simply put equivalent `source <(e)` in your experiment wrapper script to replace long and verbose environment variable declarations.

![load-demo](assets/load.gif)

### 2. Set Environment Variables via Alias

Manually setting environment variables is cumbersome. Envidia provides a convenient way to set environment variables via alias.

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

And you can use `es` to set environment variables specified in `env.d`. (`es` is short for "env set").

![alias-demo](assets/alias.gif)

### 3. Integration with [Cookiecutter](https://github.com/cookiecutter/cookiecutter)

You can pack your project environment variables as a cookiecutter template. This saves you from manually setting environment variables.

![cookiecutter-demo](assets/cookiecutter.gif)

### 4. Pre-load and Post-load Hooks

Suppose you have specified some path variables, and you want to verify the path variables actually exist.

You can use `pre_load` and `post_load` hooks to do that. Below is an example:

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
