from pathlib import Path
import Model.Fehlertyp
class PfadValidator:
    def __init__(self):
        print("PfadValidator")
    def pruefe_schreibrechte(self):
        print("pruefeSchreibrechte")
    def pruefe_speicherplatz(self):
        print("pruefeSpeicherplatz")
    def pruefe_pfad(self):
        print("pruefePfad")
        pfad_str = self.pfad_view.get_path()
        p = Path(pfad_str).expanduser()
        if p.is_dir():
            print("Es kann weitergehen, der Pfad ist ein Ordner")
            # hier
        elif p.is_file():
            print("Bitte ändern Sie den Pfad in einen Ordner")
            self.__zeige_fehler(Model.Fehlertyp.PfadFehler)
        else:
            print("Ihr Pfad ist nicht korrekt")
            self.__zeige_fehler(Model.Fehlertyp.PfadFehler)