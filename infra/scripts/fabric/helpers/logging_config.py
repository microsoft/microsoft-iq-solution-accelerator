"""
One-time logging configuration for Fabric deployment entry-point scripts.

Call ``setup_logging()`` once at the top of each entry-point script
(install_fabric_solution.py, remove_fabric_solution.py) **before** any work is
performed.  Library modules (fabric_api, graph_api, helpers.*) must never call
this function; they should only acquire loggers via
``logging.getLogger(__name__)``.

The log level is controlled by the ``LOG_LEVEL`` environment variable
(default: ``INFO``).  Set ``LOG_LEVEL=DEBUG`` for verbose HTTP / retry output.
"""

import logging
import os
import sys


class _EmojiFormatter(logging.Formatter):
    """Console formatter that preserves the existing emoji-rich output style.

    * **INFO** messages are printed verbatim (no prefix) so that the current
      user-facing output is unchanged.
    * All other levels get an icon prefix for quick visual scanning.
    """

    _ICONS = {
        logging.DEBUG:    "🔍",
        logging.WARNING:  "⚠️ ",
        logging.ERROR:    "❌",
        logging.CRITICAL: "🔥",
    }

    def format(self, record: logging.LogRecord) -> str:
        icon = self._ICONS.get(record.levelno)
        if icon:
            return f"{icon} {record.getMessage()}"
        # INFO — keep output identical to the previous print() style
        return record.getMessage()


def setup_logging() -> None:
    """Configure logging for the application.

    * Reads ``LOG_LEVEL`` from the environment (default ``INFO``).
    * Installs a single :class:`~logging.StreamHandler` on the **root** logger
      so that every logger in the process inherits the configuration.
    * Suppresses noisy third-party loggers (``azure``, ``urllib3``,
      ``requests``) to ``WARNING``.
    """
    # Read the desired log level from the LOG_LEVEL environment variable.
    # Supported values: DEBUG, INFO (default), WARNING, ERROR, CRITICAL.
    # Falls back to INFO if the variable is unset or contains an invalid name.
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # Direct all log output to stdout so it appears in the same stream as
    # the previous print()-based output. The custom _EmojiFormatter keeps
    # INFO messages unchanged and prepends icons for other severity levels.
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_EmojiFormatter())

    # Attach the handler to the root logger. Every logger created with
    # logging.getLogger(__name__) in any module will inherit this handler
    # and level, so no per-module configuration is needed.
    root = logging.getLogger()
    root.setLevel(level)
    root.addHandler(handler)

    # Third-party libraries (azure-identity, urllib3, requests, msal) are
    # very chatty at DEBUG level. Pin them to WARNING so they only surface
    # actionable messages, even when our own code runs at DEBUG.
    for noisy in ("azure", "urllib3", "requests", "msal"):
        logging.getLogger(noisy).setLevel(logging.WARNING)
