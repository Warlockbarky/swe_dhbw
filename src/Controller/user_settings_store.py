"""Persistence helper for user-specific settings stored in JSON files."""

import json
from pathlib import Path

from PyQt6.QtCore import QStandardPaths


class user_settings_store:
    """Save/load per-user settings in the app data directory."""
    def __init__(self, app_namespace: str):
        self.app_namespace = app_namespace

    def _get_settings_path(self, username: str) -> Path:
        """Return the per-user settings file path, or raise on empty username.

        Args:
            username (str): Logged-in username.

        Returns:
            Path: Filesystem path to the user's settings file.

        Raises:
            ValueError: If no username is provided.
        """
        if not username:
            raise ValueError("Kein Benutzer eingeloggt")

        config_dir = Path(
            QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
        )
        config_dir.mkdir(parents=True, exist_ok=True)

        # Sanitize usernames to keep file names portable across filesystems.
        safe_username = "".join(c if c.isalnum() or c == "_" else "_" for c in username)
        return config_dir / f"{safe_username}_settings.json"

    def exists(self, username: str) -> bool:
        try:
            return self._get_settings_path(username).exists()
        except ValueError:
            return False

    def load(self, username: str) -> dict:
        try:
            path = self._get_settings_path(username)
            if path.exists():
                with open(path, "r", encoding="utf-8") as handle:
                    return json.load(handle)
        except (IOError, json.JSONDecodeError, ValueError):
            pass
        return {}

    def save(self, username: str, values: dict):
        try:
            path = self._get_settings_path(username)
            with open(path, "w", encoding="utf-8") as handle:
                json.dump(values, handle, indent=2, ensure_ascii=False)
        except (IOError, ValueError):
            pass
