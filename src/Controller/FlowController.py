import io
import sys

import requests
from PyPDF2 import PdfReader
from PyQt6.QtCore import QObject, QSettings, QThread, QTimer, pyqtSignal
from PyQt6.QtWidgets import QApplication, QMessageBox, QStackedWidget

from View.MenueView import MenueView
from View.LoginView import LoginView
from View.PfadView import PfadView
from View.DateiListeView import DateiListeView
from View.ChatView import ChatView

from Model.PfadValidator import PfadValidator
from Controller.DateiManager import DateiManager
from Controller.BackupManager import BackupManager
from Controller.KIAnalyzer import KIAnalyzer


class _ChatWorker(QObject):
    finished = pyqtSignal(dict)
    failed = pyqtSignal(str)

    def __init__(self, *, mode: str, payload: dict, analyzer: KIAnalyzer, api_base_url: str, auth_token: str):
        super().__init__()
        self.mode = mode
        self.payload = payload
        self.analyzer = analyzer
        self.api_base_url = api_base_url
        self.auth_token = auth_token

    def run(self):
        try:
            if self.mode == "summary":
                result = self._run_summary()
            elif self.mode == "chat":
                result = self._run_chat()
            else:
                raise ValueError("Unknown worker mode")
            self.finished.emit(result)
        except Exception as exc:  # noqa: BLE001
            self.failed.emit(str(exc))

    def _run_summary(self) -> dict:
        file_id = self.payload["file_id"]
        name = self.payload["name"]
        resp = requests.get(
            f"{self.api_base_url}/files/{file_id}/download",
            headers={"Authorization": f"Bearer {self.auth_token}"},
            timeout=30,
        )
        if resp.status_code == 401:
            raise RuntimeError("Sitzung abgelaufen. Bitte erneut einloggen.")
        if resp.status_code == 403:
            raise RuntimeError("Kein Zugriff auf diese Datei.")
        if resp.status_code == 404:
            raise RuntimeError("Datei nicht gefunden.")
        if resp.status_code != 200:
            raise RuntimeError(f"Datei konnte nicht geladen werden (HTTP {resp.status_code}).")

        content_type = resp.headers.get("Content-Type", "").lower()
        if name.lower().endswith(".pdf") or content_type.startswith("application/pdf"):
            reader = PdfReader(io.BytesIO(resp.content))
            pages = [(page.extract_text() or "").strip() for page in reader.pages]
            content = "\n".join([p for p in pages if p])
        else:
            content = resp.content.decode("utf-8", errors="replace")

        if not content.strip():
            raise RuntimeError("Datei enthaelt keinen lesbaren Text.")

        max_chars = 12000
        trimmed = content[:max_chars]
        system_msg = (
            "You are a helpful assistant. Use the provided file context when relevant. "
            "If the question is not about the file, answer normally."
        )
        context_msg = f"File name: {name}\n\nFile content:\n{trimmed}"
        messages = [
            {"role": "system", "content": system_msg},
            {"role": "user", "content": context_msg},
        ]
        summary_prompt = "Bitte gib eine kurze Zusammenfassung des Dateiinhalts."
        messages.append({"role": "user", "content": summary_prompt})
        assistant_text = self.analyzer.chat(messages)
        return {"mode": "summary", "messages": messages, "assistant": assistant_text}

    def _run_chat(self) -> dict:
        messages = self.payload["messages"]
        assistant_text = self.analyzer.chat(messages)
        return {"mode": "chat", "assistant": assistant_text}

class FlowController:
    def __init__(self):
        self.app = QApplication(sys.argv)

        self.api_base_url = "http://localhost:8000"
        self.auth_token = None
        self.file_records = []
        self.ki_analyzer = KIAnalyzer()
        self.chat_messages = []
        self._chat_thread = None
        self._chat_worker = None
        self.settings = QSettings("swe_dhbw", "swe_dhbw")

        self.start_view = MenueView()
        self.login_view = LoginView()
        self.pfad_view = PfadView()
        self.datei_liste_view = DateiListeView()
        self.chat_view = ChatView()

        self.stack = QStackedWidget()
        self.stack.addWidget(self.start_view)
        self.stack.addWidget(self.login_view)
        self.stack.addWidget(self.pfad_view)
        self.stack.addWidget(self.datei_liste_view)
        self.stack.addWidget(self.chat_view)

        # Controller/Model verdrahten
        self.pfad_validator = PfadValidator()
        self.datei_manager = DateiManager(self.pfad_validator)
        self.backup_manager = BackupManager(self.datei_manager)

        self.__setup_connections()
        self.__load_saved_credentials()

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
        self.datei_liste_view.get_btn_upload().clicked.connect(self.__on_upload_clicked)
        self.datei_liste_view.get_btn_download().clicked.connect(self.__on_download_clicked)
        self.datei_liste_view.get_btn_delete().clicked.connect(self.__on_delete_clicked)
        self.datei_liste_view.get_btn_ai_summary().clicked.connect(self.__on_ai_summary_clicked)

        self.chat_view.get_btn_send().clicked.connect(self.__on_chat_send_clicked)
        self.chat_view.get_btn_back().clicked.connect(self.__on_chat_back_clicked)

        self.pfad_view.get_btn_ok().clicked.connect(self.__on_pfad_ok)

    def __starte_login(self):
        self.stack.setCurrentWidget(self.login_view)
        self.__maybe_auto_login()

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
            self.__save_credentials(username, password)
            self.__load_files_and_show()
            return

        if resp.status_code == 401:
            self.login_view.show_error("Login fehlgeschlagen: Ungueltige Zugangsdaten.")
            return

        self.login_view.show_error(
            f"Login fehlgeschlagen (HTTP {resp.status_code}). Bitte erneut versuchen."
        )

    def __load_saved_credentials(self):
        remember = bool(self.settings.value("auth/remember", False, type=bool))
        if not remember:
            return
        username = self.settings.value("auth/username", "", type=str)
        password = self.settings.value("auth/password", "", type=str)
        if username:
            self.login_view.set_username(username)
        if password:
            self.login_view.set_password(password)
        self.login_view.set_remember_checked(True)

    def __maybe_auto_login(self):
        remember = bool(self.settings.value("auth/remember", False, type=bool))
        if not remember:
            return
        username = self.login_view.get_username()
        password = self.login_view.get_password()
        if not username or not password:
            return
        QTimer.singleShot(0, self.__on_login_clicked)

    def __save_credentials(self, username: str, password: str):
        if self.login_view.get_remember_checked():
            self.settings.setValue("auth/remember", True)
            self.settings.setValue("auth/username", username)
            self.settings.setValue("auth/password", password)
        else:
            self.settings.remove("auth")

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
            self.chat_messages = []
            self.chat_view.clear_chat()
            self.chat_view.clear_chat_input()
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

    def __on_upload_clicked(self):
        if not self.auth_token:
            self.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return

        path = self.datei_liste_view.prompt_open_file()
        if not path:
            return

        try:
            with open(path, "rb") as f:
                resp = requests.post(
                    f"{self.api_base_url}/files/upload",
                    headers={"Authorization": f"Bearer {self.auth_token}"},
                    files={"file": f},
                    timeout=60,
                )
        except OSError as exc:
            self.datei_liste_view.show_error(f"Datei konnte nicht gelesen werden: {exc}")
            return
        except requests.RequestException as exc:
            self.datei_liste_view.show_error(f"Upload fehlgeschlagen: {exc}")
            return

        if resp.status_code == 401:
            self.datei_liste_view.show_error("Sitzung abgelaufen. Bitte erneut einloggen.")
            self.stack.setCurrentWidget(self.login_view)
            return

        if resp.status_code >= 400:
            self.datei_liste_view.show_error(
                f"Upload fehlgeschlagen (HTTP {resp.status_code})."
            )
            return

        self.__load_files_and_show()

    def __on_delete_clicked(self):
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

        name = record.get("name") or f"file_{file_id}"
        confirm = QMessageBox.question(
            self.datei_liste_view,
            "Datei loeschen",
            f"Soll die Datei '{name}' wirklich geloescht werden?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        try:
            resp = requests.delete(
                f"{self.api_base_url}/files/{file_id}",
                headers={"Authorization": f"Bearer {self.auth_token}"},
                timeout=30,
            )
        except requests.RequestException as exc:
            self.datei_liste_view.show_error(f"Loeschen fehlgeschlagen: {exc}")
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

        if resp.status_code >= 400:
            self.datei_liste_view.show_error(
                f"Loeschen fehlgeschlagen (HTTP {resp.status_code})."
            )
            return

        self.__load_files_and_show()

    def __on_ai_summary_clicked(self):
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

        name = record.get("name") or f"file_{file_id}"
        self.chat_view.clear_chat()
        self.stack.setCurrentWidget(self.chat_view)
        self.chat_view.set_send_enabled(False)
        self.chat_view.start_loading()
        self.__start_chat_worker(
            mode="summary",
            payload={"file_id": file_id, "name": name},
        )

    def __on_chat_send_clicked(self):
        if not self.chat_messages:
            self.datei_liste_view.show_error("Bitte zuerst KI Chat starten.")
            return

        text = self.chat_view.get_chat_input().strip()
        if not text:
            return

        self.chat_view.add_message("user", text)
        self.chat_view.clear_chat_input()
        self.chat_messages.append({"role": "user", "content": text})
        self.chat_view.set_send_enabled(False)
        self.chat_view.start_loading()
        self.__start_chat_worker(
            mode="chat",
            payload={"messages": list(self.chat_messages)},
        )

    def __on_chat_back_clicked(self):
        self.stack.setCurrentWidget(self.datei_liste_view)

    def __start_chat_worker(self, *, mode: str, payload: dict):
        if self._chat_thread is not None and self._chat_thread.isRunning():
            return
        thread = QThread()
        worker = _ChatWorker(
            mode=mode,
            payload=payload,
            analyzer=self.ki_analyzer,
            api_base_url=self.api_base_url,
            auth_token=self.auth_token or "",
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self.__on_chat_worker_finished)
        worker.failed.connect(self.__on_chat_worker_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(self.__on_chat_thread_finished)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(worker.deleteLater)
        self._chat_thread = thread
        self._chat_worker = worker
        thread.start()

    def __on_chat_worker_finished(self, result: dict):
        mode = result.get("mode")
        assistant_text = result.get("assistant", "")
        if mode == "summary":
            self.chat_messages = result.get("messages", [])
            if assistant_text:
                self.chat_messages.append({"role": "assistant", "content": assistant_text})
        else:
            if assistant_text:
                self.chat_messages.append({"role": "assistant", "content": assistant_text})

        self.chat_view.set_send_enabled(True)
        self.chat_view.stop_loading_and_stream(assistant_text)

    def __on_chat_worker_failed(self, message: str):
        self.chat_view.set_send_enabled(True)
        self.chat_view.stop_loading_and_stream("")
        self.datei_liste_view.show_error(f"KI Chat fehlgeschlagen: {message}")

    def __on_chat_thread_finished(self):
        self._chat_thread = None
        self._chat_worker = None

    def __on_pfad_ok(self):
        pfad_str = self.pfad_view.get_path()

        res = self.datei_manager.setze_und_pruefe_pfad(pfad_str)
        if not res.ok:
            # aktuell nur print – du kannst hier auch QMessageBox nutzen
            self.pfad_view.show_error(f"{res.fehlertyp}: {res.msg}")
            return

        # Wenn ok -> Backup starten
        self.backup_manager.starte_backup()
