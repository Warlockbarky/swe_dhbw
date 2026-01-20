import sys
from pathlib import Path
from PyQt6.QtWidgets import QApplication, QStackedWidget

from Controller.BackupManager import BackupManager
from View.LoginView import LoginView
from View.MenueView import MenueView
from View.PfadView import PfadView

import Model.Fehlertyp

class LoginController:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.start_view = MenueView()
        self.login_view = LoginView()
        self.pfad_view = PfadView()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.pfad_view)

        self.__setup_connections()
        self.backup_manager = BackupManager()
    def run(self):
        self.stack.setCurrentWidget(self.start_view)
        self.stack.show()
        return self.app.exec()

    def __setup_connections(self):
        # Menue
        self.start_view.get_btn_start().clicked.connect(self.__starte_login)
        self.start_view.get_btn_stop().clicked.connect(self.app.quit)

        # Login
        self.login_view.get_btn_login().clicked.connect(self.__on_login_clicked)

        # Pfad
        self.pfad_view.get_btn_ok().clicked.connect(self.__pruefe_pfad)

    def __starte_login(self):
        print("starteLogin")
        self.stack.setCurrentWidget(self.login_view)
    def __on_login_clicked(self):
        print("onLoginClicked")
        if self.__pruefe_login(self.login_view.get_username(), self.login_view.get_password()):
            self.__starte_pfad_auswahl()
        else:
            fehlertyp = Model.Fehlertyp.LoginFehler
            self.__zeige_fehler(fehlertyp)
    def __exit(self):
        print("beenden des Programms")
        sys.exit(self.app.exec())
    def __pruefe_login(self, username: str = "admin", password: str = ""):
        print("pruefeLogin")
        if False:
            self.__zeige_fehler(Model.Fehlertyp.LoginFehler, "Benutzername oder Passwort falsch")
            return False
        # Hier würden Moodle API Aufrufe stattfinden
        return True

    def __starte_pfad_auswahl(self):
        print("pfad auswählen")
        self.stack.setCurrentWidget(self.pfad_view)

    def __pruefe_pfad(self):
        print("pruefePfad")
        pfad_str = self.pfad_view.get_path()
        p = Path(pfad_str).expanduser()
        if p.is_dir():
            print("Es kann weitergehen, der Pfad ist ein Ordner")
            # hier
        elif p.is_file():
            print("Bitte ändern Sie den Pfad in einen Ordner")
            self.__zeige_fehler(Model.Fehlertyp.PfadFehler)
        else:
            print("Ihr Pfad ist nicht korrekt")
            self.__zeige_fehler(Model.Fehlertyp.PfadFehler)

    def __zeige_fehler(self, fehlertyp: Model.Fehlertyp, details: str = ""):
        print("Fehler:", fehlertyp, details)