import sys
from PyQt6.QtWidgets import QApplication
from src.View.Hauptoberflaeche import Hauptoberflaeche


class LoginController:
    def __init__(self):
        self.app = QApplication.instance() or QApplication(sys.argv)
        self.oberflaeche = Hauptoberflaeche()

    def starteLoginProzess(self):
        print("starte LoginProzess")
        self.oberflaeche.anzeigen()
        sys.exit(self.app.exec())

    def pruefeLogin(self):
        print("pruefeLogin")

    def starteSitzung(self):
        print("starteSitzung")

    def zeigeFehler(self):
        print("zeigeFehler")
