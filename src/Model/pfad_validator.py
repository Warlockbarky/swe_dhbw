from pathlib import Path
import os
import model.fehlertyp as fehlertyp

class pfad_validator:
    def pruefe_pfad(self, p: Path):
        if not p.exists() or not p.is_dir():
            return False, fehlertyp.pfad_fehler, "Pfad existiert nicht oder ist kein Ordner."
        return True, None, ""

    def pruefe_schreibrechte(self, p: Path):
        try:
            test = p / ".write_test"
            test.touch(exist_ok=True)
            test.unlink()
            return True, None, ""
        except Exception:
            return False, fehlertyp.schreibrechte_fehler, "Keine Schreibrechte im Zielordner."

    def pruefe_speicherplatz(self, p: Path, min_bytes: int = 100 * 1024 * 1024):
        # 100 MB default
        try:
            stat = os.statvfs(str(p))
            free = stat.f_bavail * stat.f_frsize
            if free < min_bytes:
                return False, fehlertyp.speicherplatz_fehler, "Zu wenig freier Speicherplatz."
            return True, None, ""
        except Exception:
            return False, fehlertyp.speicherplatz_fehler, "Speicherplatz konnte nicht geprüft werden."
