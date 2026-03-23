"""Simple logger replacing Rich console for GUI-only build."""

import logging
import sys

_logger = logging.getLogger('ale_switcher')

if not _logger.handlers:
    _handler = logging.StreamHandler(sys.stderr)
    _handler.setFormatter(logging.Formatter('[AleSwitcher] %(message)s'))
    _logger.addHandler(_handler)
    _logger.setLevel(logging.INFO)


def _strip_rich_markup(text: str) -> str:
    """Remove Rich markup tags like [yellow]...[/yellow]."""
    import re
    return re.sub(r'\[/?[a-z_ ]*\]', '', text)


def info(msg: str):
    _logger.info(_strip_rich_markup(msg))


def warn(msg: str):
    _logger.warning(_strip_rich_markup(msg))


def error(msg: str):
    _logger.error(_strip_rich_markup(msg))


def print(msg: str):
    """Drop-in replacement for console.print()."""
    info(msg)
