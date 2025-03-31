__version__ = "0.1.2"

from envidia.core.loader import Loader, loader

set_load_sequence_fn = loader.set_load_sequence_fn
register_option = loader.register_option

__all__ = [
    "Loader",
    "register_option",
    "set_load_sequence_fn",
]
