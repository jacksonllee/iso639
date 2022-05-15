try:
    from importlib.metadata import version
except ModuleNotFoundError:
    # For Python 3.7
    from importlib_metadata import version

from .language import Language


__version__ = version("python-iso639")
__all__ = ["__version__", "Language"]
