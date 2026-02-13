from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QCheckBox, QFrame, QHBoxLayout, QLabel, QLineEdit, QPushButton, QVBoxLayout

from view.hauptoberflaeche import hauptoberflaeche


class login_view(hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.setObjectName("login_view")
        self.btn_login = None
        self.btn_register = None
        self.remember_me = QCheckBox("Angemeldet bleiben")
        self.username = QLineEdit()
        self.password = QLineEdit()
        self.__login_fenster_erstellen()

    def __login_fenster_erstellen(self):
        layout = self.__formular_erstellen()
        self.root.addStretch()
        self.root.addLayout(layout)
        self.root.addStretch()
        self.mittig_auf_bildschirm()
    def __formular_erstellen(self):
        card = QFrame()
        card.setObjectName("Card")
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        title = QLabel("Anmeldung")
        title.setObjectName("SectionTitle")
        card_layout.addWidget(title)

        # Setze Passwort-Feld als Passwort-Eingabe
        self.password.setEchoMode(QLineEdit.EchoMode.Password)
        self.username.setPlaceholderText("Username")
        self.password.setPlaceholderText("Password")

        label_user = QLabel("Benutzername")
        label_user.setObjectName("FieldLabel")
        card_layout.addWidget(label_user)
        card_layout.addWidget(self.username)

        label_pass = QLabel("Passwort")
        label_pass.setObjectName("FieldLabel")
        card_layout.addWidget(label_pass)
        card_layout.addWidget(self.password)

        self.btn_login = QPushButton("Login")
        self.btn_register = QPushButton("Registrieren")
        self.btn_login.setObjectName("PrimaryButton")
        self.btn_register.setObjectName("SecondaryButton")

        actions = QHBoxLayout()
        actions.setSpacing(8)
        actions.addWidget(self.btn_register)
        actions.addStretch()
        actions.addWidget(self.btn_login)

        card_layout.addLayout(actions)
        card_layout.addWidget(self.remember_me)

        wrapper = QVBoxLayout()
        wrapper.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        wrapper.addWidget(card)
        return wrapper
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