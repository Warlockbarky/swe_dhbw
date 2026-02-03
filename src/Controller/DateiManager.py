from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog

from Model.PfadValidator import PfadValidator
import Model.Fehlertyp as Fehlertyp

@dataclass(frozen=True)
class PfadResult:
    ok: bool
    pfad: Path | None = None
    fehlertyp: Fehlertyp | None = None
    msg: str = ""

class DateiManager:
    def __init__(self, validator: PfadValidator):
        self._validator = validator
        self._zielpfad: Path | None = None

    def oeffne_dateidialog(self, parent=None) -> str | None:
        pfad = QFileDialog.getExistingDirectory(parent, "Ordner auswählen")
        return pfad if pfad else None

    def setze_und_pruefe_pfad(self, pfad_str: str) -> PfadResult:
        p = Path(pfad_str).expanduser().resolve()

        ok, ft, msg = self._validator.pruefe_pfad(p)
        if not ok:
            return PfadResult(False, None, ft, msg)

        ok, ft, msg = self._validator.pruefe_schreibrechte(p)
        if not ok:
            return PfadResult(False, None, ft, msg)

        ok, ft, msg = self._validator.pruefe_speicherplatz(p)
        if not ok:
            return PfadResult(False, None, ft, msg)

        self._zielpfad = p
        return PfadResult(True, p, None, "")

    def speichere_pfad(self, pfad: Path):
        self._config.pfad = str(pfad)
        self._config.speichern()

    def lade_pfad(self) -> Path | None:
        pfad_str = self._config.pfad
        if not pfad_str:
            return None
        return Path(pfad_str).expanduser().resolve()
    def get_zielpfad(self) -> Path:
        if self._zielpfad is None:
            raise RuntimeError("Zielpfad ist nicht gesetzt/validiert.")
        return self._zielpfad

    def speichere_datei(self, rel_name: str, data: bytes) -> Path:
        ziel = self.get_zielpfad() / rel_name
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(data)
        return ziel
