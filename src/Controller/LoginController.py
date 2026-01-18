import sys
from PyQt6.QtWidgets import QApplication

from View.Benutzer import Benutzer
from src.View.Hauptoberflaeche import Hauptoberflaeche

class LoginController:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)

        self.haupt = Hauptoberflaeche()
        self.benutzer = Benutzer()

        self.benutzer.loginRequested.connect(self.pruefe_login)
        self.haupt.setInhalt(self.benutzer)

    def starte_login_prozess(self):
        self.haupt.show()
        sys.exit(self.app.exec())

    def pruefe_login(self):
        print("pruefeLogin")
        # Return True just for demo purposes. Function will be implemented later
        return True

    def starte_sitzung(self):
        print("starteSitzung")

    def zeige_fehler(self):
        print("zeigeFehler")
