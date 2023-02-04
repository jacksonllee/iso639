import datetime
from importlib.metadata import version

from .language import Language, LanguageNotFoundError, _get_all_languages


__version__ = version("python-iso639")
__all__ = [
    "__version__",
    "ALL_LANGUAGES",
    "DATA_LAST_UPDATED",
    "Language",
    "LanguageNotFoundError",
]

DATA_LAST_UPDATED = datetime.date(2023, 1, 23)


def __getattr__(name):
    if name == "ALL_LANGUAGES":
        return _get_all_languages()
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
