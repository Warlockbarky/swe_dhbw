from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFormLayout, QLineEdit, QPushButton

from View.Hauptoberflaeche import Hauptoberflaeche


class LoginView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.btn_login = None
        self.btn_register = None
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.__login_fenster_erstellen()

    def __login_fenster_erstellen(self):
        layout = self.__formular_erstellen()
        self.root.addLayout(layout)
        self.mittig_auf_bildschirm()
    def __formular_erstellen(self):
        layout = QFormLayout()
        # Setze Passwort-Feld als Passwort-Eingabe
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Benutzername", self.username)
        layout.addRow("Passwort", self.password)

        self.btn_login = QPushButton("Login")
        self.btn_register = QPushButton("Registrieren")
        layout.addRow(self.btn_login)
        layout.addRow(self.btn_register)
        return layout
    def get_username(self):
        return self.username.text().strip()
    def get_password(self):
        return self.password.text().strip()
    def get_btn_login(self):
        return self.btn_login

    def get_btn_register(self):
        return self.btn_register