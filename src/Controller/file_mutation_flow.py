from pathlib import Path

import requests
from PyQt6.QtWidgets import QMessageBox

from controller.file_path_service import resolve_download_dir


class file_mutation_flow:
    def __init__(self, controller):
        self.controller = controller

    def on_upload_clicked(self):
        if not self.controller.auth_token:
            self.controller.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return

        default_dir = self.controller.settings.value("files/default_dir", "", type=str)
        path = self.controller.datei_liste_view.prompt_open_file(default_dir)
        if not path:
            return

        try:
            with open(path, "rb") as handle:
                resp = requests.post(
                    f"{self.controller.api_base_url}/files/upload",
                    headers={"Authorization": f"Bearer {self.controller.auth_token}"},
                    files={"file": handle},
                    timeout=60,
                )
        except OSError as exc:
            self.controller.datei_liste_view.show_error(
                f"Datei konnte nicht gelesen werden: {exc}"
            )
            return
        except requests.RequestException as exc:
            self.controller.datei_liste_view.show_error(f"Upload fehlgeschlagen: {exc}")
            return

        if resp.status_code == 401:
            self.controller.datei_liste_view.show_error(
                "Sitzung abgelaufen. Bitte erneut einloggen."
            )
            self.controller.stack.setCurrentWidget(self.controller.login_view)
            return

        if resp.status_code >= 400:
            self.controller.datei_liste_view.show_error(
                f"Upload fehlgeschlagen (HTTP {resp.status_code})."
            )
            return

        self.controller.file_list_flow.load_files_and_show()

    def on_delete_clicked(self):
        if not self.controller.auth_token:
            self.controller.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return

        checked_rows = self.controller.datei_liste_view.get_checked_indices()
        selected_rows = self.controller.datei_liste_view.get_selected_indices()
        selected_rows = sorted(set(checked_rows or selected_rows))
        if not selected_rows:
            self.controller.datei_liste_view.show_error(
                "Bitte eine Datei aus der Liste auswaehlen."
            )
            return

        records = []
        for row in selected_rows:
            if 0 <= row < len(self.controller.visible_file_records):
                records.append(self.controller.visible_file_records[row])

        if not records:
            self.controller.datei_liste_view.show_error(
                "Bitte eine Datei aus der Liste auswaehlen."
            )
            return

        if len(records) == 1:
            record = records[0]
            file_id = record.get("id")
            name = record.get("name") or f"file_{file_id}"
            confirm_text = f"Soll die Datei '{name}' wirklich geloescht werden?"
        else:
            confirm_text = f"Sollen {len(records)} Dateien wirklich geloescht werden?"

        confirm = QMessageBox.question(
            self.controller.datei_liste_view,
            "Dateien loeschen",
            confirm_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        errors: list[str] = []
        for record in records:
            file_id = record.get("id")
            if file_id is None:
                errors.append("Ausgewaehlter Eintrag hat keine Datei-ID.")
                continue
            try:
                resp = requests.delete(
                    f"{self.controller.api_base_url}/files/{file_id}",
                    headers={"Authorization": f"Bearer {self.controller.auth_token}"},
                    timeout=30,
                )
            except requests.RequestException as exc:
                errors.append(f"Loeschen fehlgeschlagen: {exc}")
                continue

            if resp.status_code == 401:
                self.controller.datei_liste_view.show_error(
                    "Sitzung abgelaufen. Bitte erneut einloggen."
                )
                self.controller.stack.setCurrentWidget(self.controller.login_view)
                return

            if resp.status_code == 403:
                errors.append("Kein Zugriff auf diese Datei.")
                continue

            if resp.status_code == 404:
                errors.append("Datei nicht gefunden.")
                continue

            if resp.status_code >= 400:
                errors.append(f"Loeschen fehlgeschlagen (HTTP {resp.status_code}).")
                continue

        self.controller.file_list_flow.load_files_and_show()
        if errors:
            self.controller.datei_liste_view.show_error("\n".join(errors))

    def sync_files_to_folder(self):
        target = resolve_download_dir(self.controller.settings, self.controller.datei_liste_view)
        if target is None:
            return

        res = self.controller.datei_manager.setze_und_pruefe_pfad(str(target))
        if not res.ok:
            self.controller.datei_liste_view.show_error(f"{res.fehlertyp}: {res.msg}")
            return

        for record in self.controller.file_records:
            file_id = record.get("id")
            if file_id is None:
                continue
            name = record.get("name") or f"file_{file_id}"
            safe_name = Path(name).name or f"file_{file_id}"
            dest = self.controller.datei_manager.get_zielpfad() / safe_name
            if dest.exists():
                continue

            try:
                resp = requests.get(
                    f"{self.controller.api_base_url}/files/{file_id}/download",
                    headers={"Authorization": f"Bearer {self.controller.auth_token}"},
                    timeout=60,
                    stream=True,
                )
            except requests.RequestException as exc:
                self.controller.datei_liste_view.show_error(
                    f"Download fehlgeschlagen: {exc}"
                )
                continue

            if resp.status_code == 401:
                self.controller.datei_liste_view.show_error(
                    "Sitzung abgelaufen. Bitte erneut einloggen."
                )
                self.controller.stack.setCurrentWidget(self.controller.login_view)
                return

            if resp.status_code != 200:
                self.controller.datei_liste_view.show_error(
                    f"Download fehlgeschlagen (HTTP {resp.status_code})."
                )
                continue

            dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                with open(dest, "wb") as handle:
                    for chunk in resp.iter_content(chunk_size=8192):
                        if chunk:
                            handle.write(chunk)
            except OSError as exc:
                self.controller.datei_liste_view.show_error(
                    f"Datei konnte nicht gespeichert werden: {exc}"
                )
                continue
