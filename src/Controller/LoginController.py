import sys
from PyQt6.QtWidgets import QApplication
from src.View.Hauptoberflaeche import Hauptoberflaeche


class LoginController:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.oberflaeche = Hauptoberflaeche()

    def starte_login_prozess(self):
        print("starte LoginProzess")
        self.oberflaeche.anzeigen()
        sys.exit(self.app.exec())

    def pruefe_login(self):
        print("pruefeLogin")

    def starte_sitzung(self):
        print("starteSitzung")

    def zeige_fehler(self):
        print("zeigeFehler")
