"""Backup manager that writes a demo backup file to the target folder."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

from controller.datei_manager import datei_manager


@dataclass(frozen=True)
class backup_result:
    ok: bool
    ziel_datei: Path | None = None
    msg: str = ""
    error: Exception | None = None


class backup_manager:
    """Writes a small backup artifact to validate the backup pipeline."""
    def __init__(self, dm: datei_manager):
        self._dm = dm

    def starte_backup(self) -> backup_result:
        """Create a demo backup file under the validated target directory.

        Returns:
            backup_result: Outcome metadata for the backup attempt.
        """
        try:
            zielordner = self._dm.get_zielpfad()
        except Exception as e:
            return backup_result(False, None, "Zielpfad ist nicht gesetzt/validiert.", e)

        try:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            rel_name = f"backup_{ts}.txt"

            content = (
                f"Backup gestartet am {datetime.now().isoformat(timespec='seconds')}\n"
                f"Zielordner: {zielordner}\n"
            ).encode("utf-8")

            ziel_datei = self._dm.speichere_datei(rel_name, content)
            return backup_result(True, ziel_datei, "Backup (Demo) geschrieben.")
        except Exception as e:
            return backup_result(False, None, "Backup konnte nicht geschrieben werden.", e)
