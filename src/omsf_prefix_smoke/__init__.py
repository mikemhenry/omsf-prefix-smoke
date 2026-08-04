"""OMSF prefix.dev publishing smoke test."""

from __future__ import annotations

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("omsf-prefix-smoke")
except PackageNotFoundError:  # pragma: no cover - only used from an uninstalled checkout
    __version__ = "0+unknown"

__all__ = ["__version__"]
