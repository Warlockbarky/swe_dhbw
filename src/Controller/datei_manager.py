from dataclasses import dataclass
from pathlib import Path

from PyQt6.QtWidgets import QFileDialog

from model.konfiguration import konfiguration
from model.pfad_validator import pfad_validator
import model.fehlertyp as fehlertyp

@dataclass(frozen=True)
class pfad_result:
    ok: bool
    pfad: Path | None = None
    fehlertyp: fehlertyp.app_error | None = None
    msg: str = ""

class datei_manager:
    def __init__(self, validator: pfad_validator):
        self._validator = pfad_validator()
        self.config = konfiguration()
        self._zielpfad: Path | None = None

    def setze_und_pruefe_pfad(self, pfad_str: str) -> pfad_result:
        p = Path(pfad_str).expanduser().resolve()

        ok, ft, msg = self._validator.pruefe_pfad(p)
        if not ok:
            return pfad_result(False, None, ft, msg)

        ok, ft, msg = self._validator.pruefe_schreibrechte(p)
        if not ok:
            return pfad_result(False, None, ft, msg)

        ok, ft, msg = self._validator.pruefe_speicherplatz(p)
        if not ok:
            return pfad_result(False, None, ft, msg)

        self._zielpfad = p
        return pfad_result(True, p, None, "")

    def speichere_pfad(self, pfad: Path):
        self.config.set_pfad(str(pfad))
        self.config.speichere()

    def lade_pfad_und_setze(self) -> pfad_result:
        pfad = self.lade_pfad()
        if pfad is None:
            return pfad_result(False, None, fehlertyp.KEIN_PFAD, "Kein Pfad gespeichert")
        return self.setze_und_pruefe_pfad(str(pfad))

    def get_zielpfad(self) -> Path:
        if self._zielpfad is None:
            raise RuntimeError("Zielpfad ist nicht gesetzt/validiert.")
        return self._zielpfad

    def speichere_datei(self, rel_name: str, data: bytes) -> Path:
        ziel = self.get_zielpfad() / rel_name
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(data)
        return ziel
