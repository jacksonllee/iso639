try:
    from importlib.metadata import version
except ModuleNotFoundError:
    # For Python 3.7
    from importlib_metadata import version

import datetime

from .language import Language, _get_all_languages


__version__ = version("python-iso639")
__all__ = ["__version__", "Language", "ALL_LANGUAGES", "DATA_LAST_UPDATED"]

DATA_LAST_UPDATED = datetime.date(2022, 3, 11)


def __getattr__(name):
    if name == "ALL_LANGUAGES":
        return _get_all_languages()
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
