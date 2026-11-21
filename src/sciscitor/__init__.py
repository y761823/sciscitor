"""Sciscitor - a desktop chat client for OpenAI-compatible models."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sciscitor")
except PackageNotFoundError:  # a source tree that was never installed
    __version__ = "0.0.0"
