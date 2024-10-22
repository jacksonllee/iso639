import datetime
from importlib.metadata import version

from .language import Language, LanguageNotFoundError, _get_all_languages


# __version__ is based on calendar versioning (https://calver.org/).
# __version__ and DATA_LAST_UPDATED are intentionally kept separate.
# While DATA_LAST_UPDATED is strictly the date for the ISO 639-3 data release,
# __version__ can be bumped for changes other than data updates.
__version__ = version("python-iso639")
DATA_LAST_UPDATED = datetime.date(2024, 4, 15)


def __getattr__(name):
    if name == "ALL_LANGUAGES":
        return _get_all_languages()
    else:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = [
    "__version__",
    "ALL_LANGUAGES",
    "DATA_LAST_UPDATED",
    "Language",
    "LanguageNotFoundError",
]
