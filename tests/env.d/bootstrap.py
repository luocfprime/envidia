from pathlib import Path

from envidia import Loader, register_option

register_option("gpu", "CUDA_VISIBLE_DEVICES", default="0")
register_option("foo", "FOO_PATH", default=".")


def is_package_installed(package_name):
    try:
        __import__(package_name)
        return True
    except ImportError:
        return False


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
