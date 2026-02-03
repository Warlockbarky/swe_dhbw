from dataclasses import dataclass
from pathlib import Path
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

    def get_zielpfad(self) -> Path:
        if self._zielpfad is None:
            raise RuntimeError("Zielpfad ist nicht gesetzt/validiert.")
        return self._zielpfad

    def speichere_datei(self, rel_name: str, data: bytes) -> Path:
        ziel = self.get_zielpfad() / rel_name
        ziel.parent.mkdir(parents=True, exist_ok=True)
        ziel.write_bytes(data)
        return ziel
