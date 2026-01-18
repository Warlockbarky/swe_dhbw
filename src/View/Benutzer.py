from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QWidget, QPushButton, QLineEdit, QVBoxLayout, QLabel


class Benutzer(QWidget):
    loginRequested = pyqtSignal(str, str)
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)

        self.user = QLineEdit()
        self.user.setPlaceholderText("Username")

        self.pw = QLineEdit()
        self.pw.setEchoMode(QLineEdit.EchoMode.Password)

        btn = QPushButton("Login")
        btn.clicked.connect(self._login)

        layout.addWidget(QLabel("Login"))
        layout.addWidget(self.user)
        layout.addWidget(self.pw)
        layout.addWidget(btn)
    def benutzer_daten_eingeben(self):
        print("datenEingeben")
    def waehle_pfad(self):
        print("waehlePfad")
    def starte_backup(self):
        print("starteBackup")
    def zeige_ergebnis(self):
        print("zeigeErgebnis")
    def starte_Analyse(self):
        print("starteAnalyse")
    def zeige_ergebnisse(self):
        print("zeigeErgebnisse")
    def _login(self):
        self.loginRequested.emit(self.user.text(), self.pw.text())