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
    def __init__(self, datei_manager: datei_manager):
        self._dm = datei_manager

    def starte_backup(self) -> backup_result:
        try:
            zielordner = self._dm.get_zielpfad()
        except Exception as e:
            return backup_result(False, None, "Zielpfad ist nicht gesetzt/validiert.", e)

        try:
            ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            # TODO: richtige Datei Backupen (aktuell nur Testdatei)
            rel_name = f"backup_{ts}.txt"

            content = (
                f"Backup gestartet am {datetime.now().isoformat(timespec='seconds')}\n"
                f"Zielordner: {zielordner}\n"
            ).encode("utf-8")

            ziel_datei = self._dm.speichere_datei(rel_name, content)
            return backup_result(True, ziel_datei, "Backup (Demo) geschrieben.")
        except Exception as e:
            return backup_result(False, None, "Backup konnte nicht geschrieben werden.", e)
