from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QFormLayout, QLineEdit, QPushButton

from View.Hauptoberflaeche import Hauptoberflaeche


class LoginView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.btn_login = None
        self.btn_register = None
        self.remember_me = QCheckBox("Angemeldet bleiben")
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.__login_fenster_erstellen()

    def __login_fenster_erstellen(self):
        layout = self.__formular_erstellen()
        self.root.addLayout(layout)
        self.mittig_auf_bildschirm()
    def __formular_erstellen(self):
        layout = QFormLayout()
        layout.setFormAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        layout.setSpacing(10)
        # Setze Passwort-Feld als Passwort-Eingabe
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.username.setPlaceholderText("Username")
        self.password.setPlaceholderText("Password")
        layout.addRow("Benutzername", self.username)
        layout.addRow("Passwort", self.password)

        self.btn_login = QPushButton("Login")
        self.btn_register = QPushButton("Registrieren")
        layout.addRow(self.btn_login)
        layout.addRow(self.btn_register)
        layout.addRow(self.remember_me)
        return layout
    def get_username(self):
        return self.username.text().strip()
    def get_password(self):
        return self.password.text().strip()
    def get_btn_login(self):
        return self.btn_login

    def get_btn_register(self):
        return self.btn_register

    def get_remember_checked(self) -> bool:
        return self.remember_me.isChecked()

    def set_remember_checked(self, checked: bool):
        self.remember_me.setChecked(checked)

    def set_username(self, value: str):
        self.username.setText(value)

    def set_password(self, value: str):
        self.password.setText(value)