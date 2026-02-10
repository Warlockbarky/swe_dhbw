import sys

import requests
from PyQt6.QtWidgets import QApplication, QStackedWidget

from View.MenueView import MenueView
from View.LoginView import LoginView
from View.PfadView import PfadView
from View.DateiListeView import DateiListeView

from Model.PfadValidator import PfadValidator
from Controller.DateiManager import DateiManager
from Controller.BackupManager import BackupManager

class FlowController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.api_base_url = "http://localhost:8000"
        self.auth_token = None
        self.file_records = []

        self.start_view = MenueView()
        self.login_view = LoginView()
        self.pfad_view = PfadView()
        self.datei_liste_view = DateiListeView()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.pfad_view)
        self.stack.addWidget(self.datei_liste_view)

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
        self.login_view.get_btn_register().clicked.connect(self.__on_register_clicked)

        self.datei_liste_view.get_btn_refresh().clicked.connect(self.__load_files_and_show)
        self.datei_liste_view.get_btn_download().clicked.connect(self.__on_download_clicked)

        self.pfad_view.get_btn_ok().clicked.connect(self.__on_pfad_ok)

    def __starte_login(self):
        self.stack.setCurrentWidget(self.login_view)

    def __on_login_clicked(self):
        username = self.login_view.get_username()
        password = self.login_view.get_password()

        if not username or not password:
            self.login_view.show_error("Bitte Benutzername und Passwort eingeben.")
            return

        try:
            resp = requests.post(
                f"{self.api_base_url}/token",
                headers={"Content-Type": "application/x-www-form-urlencoded"},
                data={"username": username, "password": password},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.login_view.show_error(f"Login fehlgeschlagen: {exc}")
            return

        if resp.status_code == 200:
            data = resp.json()
            token = data.get("access_token")
            if not token:
                self.login_view.show_error("Login fehlgeschlagen: Token fehlt in der Antwort.")
                return
            self.auth_token = token
            self.__load_files_and_show()
            return

        if resp.status_code == 401:
            self.login_view.show_error("Login fehlgeschlagen: Ungueltige Zugangsdaten.")
            return

        self.login_view.show_error(
            f"Login fehlgeschlagen (HTTP {resp.status_code}). Bitte erneut versuchen."
        )

    def __on_register_clicked(self):
        username = self.login_view.get_username()
        password = self.login_view.get_password()

        if not username or not password:
            self.login_view.show_error("Bitte Benutzername und Passwort eingeben.")
            return

        try:
            resp = requests.post(
                f"{self.api_base_url}/register",
                json={"username": username, "password_hash": password},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.login_view.show_error(f"Registrierung fehlgeschlagen: {exc}")
            return

        if resp.status_code == 400:
            self.login_view.show_error("Registrierung fehlgeschlagen: Benutzername existiert bereits.")
            return

        if resp.status_code >= 400:
            self.login_view.show_error(
                f"Registrierung fehlgeschlagen (HTTP {resp.status_code}). Bitte erneut versuchen."
            )
            return

        print("Registrierung erfolgreich. Bitte einloggen.")

    def __load_files_and_show(self):
        if not self.auth_token:
            self.login_view.show_error("Bitte zuerst einloggen.")
            return

        try:
            resp = requests.get(
                f"{self.api_base_url}/files/",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.login_view.show_error(f"Dateiliste konnte nicht geladen werden: {exc}")
            return

        if resp.status_code == 200:
            data = resp.json()
            self.file_records = self.__normalize_file_records(data)
            items = self.__format_file_labels(self.file_records)
            self.datei_liste_view.set_items(items)
            self.stack.setCurrentWidget(self.datei_liste_view)
            return

        if resp.status_code == 401:
            self.login_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
            self.stack.setCurrentWidget(self.login_view)
            return

        self.login_view.show_error(
            f"Dateiliste konnte nicht geladen werden (HTTP {resp.status_code})."
        )

    @staticmethod
    def __normalize_file_records(data):
        if not isinstance(data, list):
            return []

        records = []
        for item in data:
            if isinstance(item, dict):
                file_id = item.get("id")
                name = (
                    item.get("filename")
                    or item.get("name")
                    or item.get("original_filename")
                    or item.get("path")
                )
                records.append({"id": file_id, "name": name})
            else:
                records.append({"id": None, "name": str(item)})

        return records

    @staticmethod
    def __format_file_labels(records):
        items = []
        for record in records:
            file_id = record.get("id")
            name = record.get("name") or "Datei"
            if file_id is not None:
                items.append(f"{file_id}: {name}")
            else:
                items.append(str(name))
        return items

    def __on_download_clicked(self):
        if not self.auth_token:
            self.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return

        idx = self.datei_liste_view.get_selected_index()
        if idx < 0 or idx >= len(self.file_records):
            self.datei_liste_view.show_error("Bitte eine Datei aus der Liste auswaehlen.")
            return

        record = self.file_records[idx]
        file_id = record.get("id")
        if file_id is None:
            self.datei_liste_view.show_error("Ausgewaehlter Eintrag hat keine Datei-ID.")
            return

        suggested_name = record.get("name") or f"file_{file_id}"
        save_path = self.datei_liste_view.prompt_save_path(suggested_name)
        if not save_path:
            return

        try:
            resp = requests.get(
                f"{self.api_base_url}/files/{file_id}/download",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=30,
                stream=True,
            )
        except requests.RequestException as exc:
            self.datei_liste_view.show_error(f"Download fehlgeschlagen: {exc}")
            return

        if resp.status_code == 200:
            try:
                with open(save_path, "wb") as f:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
            except OSError as exc:
                self.datei_liste_view.show_error(f"Datei konnte nicht gespeichert werden: {exc}")
                return
            print(f"Datei gespeichert: {save_path}")
            return

        if resp.status_code == 401:
            self.datei_liste_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
            self.stack.setCurrentWidget(self.login_view)
            return

        if resp.status_code == 403:
            self.datei_liste_view.show_error("Kein Zugriff auf diese Datei.")
            return

        if resp.status_code == 404:
            self.datei_liste_view.show_error("Datei nicht gefunden.")
            return

        self.datei_liste_view.show_error(
            f"Download fehlgeschlagen (HTTP {resp.status_code})."
        )

    def __on_pfad_ok(self):
        pfad_str = self.pfad_view.get_path()

        res = self.datei_manager.setze_und_pruefe_pfad(pfad_str)
        if not res.ok:
            # aktuell nur print – du kannst hier auch QMessageBox nutzen
            self.pfad_view.show_error(f"{res.fehlertyp}: {res.msg}")
            return

        # Wenn ok -> Backup starten
        self.backup_manager.starte_backup()
