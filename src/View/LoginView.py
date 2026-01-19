from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QFormLayout, QLineEdit, QPushButton

from View.Hauptoberflaeche import Hauptoberflaeche


class LoginView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.btn_login = None
        self.__login_fenster_erstellen()

    def __login_fenster_erstellen(self):
        layout = self.__formular_erstellen()
        self.root.addLayout(layout)
        self.setFixedSize(600, 300)
        # Setze Fenstergröße fest und nicht vergrößer/verkleinerbar
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
    def __formular_erstellen(self):
        layout = QFormLayout()
        username = QLineEdit()
        password = QLineEdit()
        # Setze Passwort-Feld als Passwort-Eingabe
        password.setEchoMode(QLineEdit.EchoMode.Password)
        layout.addRow("Benutzername", username)
        layout.addRow("Passwort", password)

        btn_login = QPushButton("Login")
        layout.addRow(btn_login)
        return layout

