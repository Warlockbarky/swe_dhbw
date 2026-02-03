from Controller.DateiManager import DateiManager


class BackupManager:
    def __init__(self, datei_manager: DateiManager):
        self._dm = datei_manager

    def starte_backup(self):
        ziel = self._dm.get_zielpfad()
        print("Backup nach:", ziel)

        # Demo: schreiben
        self._dm.speichere_datei("test.txt", b"backup gestartet")
