import sys
from PyQt6.QtWidgets import QApplication, QStackedWidget

from View.MenueView import MenueView
from View.LoginView import LoginView
from View.PfadView import PfadView

from Model.PfadValidator import PfadValidator
from Controller.DateiManager import DateiManager
from Controller.BackupManager import BackupManager

class FlowController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.start_view = MenueView()
        self.login_view = LoginView()
        self.pfad_view = PfadView()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.pfad_view)

        # Controller/Model verdrahten
        self.pfad_validator = PfadValidator()
        self.datei_manager = DateiManager(self.pfad_validator)
        self.backup_manager = BackupManager(self.datei_manager)

        self.__setup_connections()

    def run(self):
        self.stack.setCurrentWidget(self.start_view)
        self.stack.show()
        return self.app.exec()

    def __setup_connections(self):
        self.start_view.get_btn_start().clicked.connect(self.__starte_login)
        self.start_view.get_btn_stop().clicked.connect(self.app.quit)

        self.login_view.get_btn_login().clicked.connect(self.__on_login_clicked)

        self.pfad_view.get_btn_ok().clicked.connect(self.__on_pfad_ok)

    def __starte_login(self):
        self.stack.setCurrentWidget(self.login_view)

    def __on_login_clicked(self):
        # hier echte Prüfung später
        self.stack.setCurrentWidget(self.pfad_view)

    def __on_pfad_ok(self):
        pfad_str = self.pfad_view.get_path()

        res = self.datei_manager.setze_und_pruefe_pfad(pfad_str)
        if not res.ok:
            # aktuell nur print – du kannst hier auch QMessageBox nutzen
            self.pfad_view.show_error(f"{res.fehlertyp}: {res.msg}")
            return

        # Wenn ok -> Backup starten
        self.backup_manager.starte_backup()
        # optional: zurück zum Menü oder Fortschrittsview
        # self.stack.setCurrentWidget(self.start_view)
