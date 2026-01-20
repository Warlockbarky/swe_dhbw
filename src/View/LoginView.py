from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFormLayout, QLineEdit, QPushButton

from View.Hauptoberflaeche import Hauptoberflaeche


class LoginView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.btn_login = None
        self.username = None
        self.password = None
        self.__login_fenster_erstellen()

    def __login_fenster_erstellen(self):
        layout = self.__formular_erstellen()
        self.root.addLayout(layout)
        self.fenstergrößen_fixierung()
        self.mittig_auf_bildschirm()
    def __formular_erstellen(self):
        layout = QFormLayout()
        username = QLineEdit()
        password = QLineEdit()
        # Setze Passwort-Feld als Passwort-Eingabe
        password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Benutzername", username)
        layout.addRow("Passwort", password)

        self.btn_login = QPushButton("Login")
        layout.addRow(self.btn_login)
        return layout
    def get_username(self):
        return self.username
    def get_password(self):
        return self.password
    def get_btn_login(self):
        return self.btn_login

