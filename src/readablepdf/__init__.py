"""readablepdf package."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("readablepdf")
except PackageNotFoundError:  # pragma: no cover - only in non-installed source usage
    __version__ = "0.0.0"

__all__ = ["__version__"]
