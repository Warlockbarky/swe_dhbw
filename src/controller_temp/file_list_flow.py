"""File list retrieval and presentation logic."""

import requests

from controller.file_utils import (
    file_extension,
    format_date,
    format_size,
    normalize_file_records,
    parse_iso_datetime,
)


class file_list_flow:
    """Handles listing, sorting, and filtering remote files."""
    def __init__(self, controller):
        self.controller = controller

    def load_files_and_show(self):
        """Fetch file list from the API and refresh the UI state.

        Returns:
            None
        """
        if not self.controller.auth_token:
            self.controller.login_view.show_error("Bitte zuerst einloggen.")
            return

        try:
            resp = requests.get(
                f"{self.controller.api_base_url}/files/",
                headers={"Authorization": f"Bearer {self.controller.auth_token}"},
                timeout=10,
            )
        except requests.RequestException as exc:
            self.controller.login_view.show_error(
                f"Dateiliste konnte nicht geladen werden: {exc}"
            )
            return

        if resp.status_code == 200:
            data = resp.json()
            self.controller.file_records = normalize_file_records(data)
            self.refresh_file_list_view()
            self.controller.chat_messages = []
            self.controller.current_chat_id = None
            self.controller.chat_file_context = []
            self.controller.chat_file_meta = []
            self.controller.chat_view.clear_chat()
            self.controller.chat_view.clear_chat_input()
            self.controller.chat_view.set_selected_files([])
            self.controller.file_mutation_flow.sync_files_to_folder()
            self.controller.stack.setCurrentWidget(self.controller.datei_liste_view)
            return

        if resp.status_code == 401:
            self.controller.login_view.show_error(
                "Sitzung abgelaufen. Bitte erneut einloggen."
            )
            self.controller.stack.setCurrentWidget(self.controller.login_view)
            return

        self.controller.login_view.show_error(
            f"Dateiliste konnte nicht geladen werden (HTTP {resp.status_code})."
        )

    def sorted_file_records(self, records: list[dict]) -> list[dict]:
        mode = self.controller.file_sort_mode
        sorted_records = list(records)

        if mode == "Name (Z-A)":
            sorted_records.sort(key=lambda r: str(r.get("name") or "").lower(), reverse=True)
            return sorted_records
        if mode == "Datum (neu-alt)":
            sorted_records.sort(
                key=lambda r: parse_iso_datetime(r.get("created_at") or r.get("updated_at")),
                reverse=True,
            )
            return sorted_records
        if mode == "Datum (alt-neu)":
            sorted_records.sort(
                key=lambda r: parse_iso_datetime(r.get("created_at") or r.get("updated_at")),
            )
            return sorted_records
        if mode == "Format (A-Z)":
            sorted_records.sort(key=lambda r: file_extension(str(r.get("name") or "")))
            return sorted_records
        if mode == "Format (Z-A)":
            sorted_records.sort(
                key=lambda r: file_extension(str(r.get("name") or "")),
                reverse=True,
            )
            return sorted_records

        sorted_records.sort(key=lambda r: str(r.get("name") or "").lower())
        return sorted_records

    def refresh_file_list_view(self):
        sorted_records = self.sorted_file_records(self.controller.file_records)
        query = self.controller.file_search_query.strip().lower()
        if query:
            sorted_records = [
                record
                for record in sorted_records
                if query in str(record.get("name") or "").lower()
            ]
        self.controller.visible_file_records = sorted_records
        items = self.format_file_labels(self.controller.visible_file_records)
        self.controller.datei_liste_view.set_items(items)

    @staticmethod
    def format_file_labels(records):
        items = []
        for record in records:
            file_id = record.get("id")
            name = record.get("name") or "Datei"
            if file_id is not None:
                label = f"{file_id}: {name}"
            else:
                label = str(name)
            items.append(label)
        return items

    def on_file_details_requested(self, row: int):
        if row < 0 or row >= len(self.controller.visible_file_records):
            self.controller.datei_liste_view.show_error(
                "Bitte eine Datei aus der Liste auswaehlen."
            )
            return

        record = self.controller.visible_file_records[row]
        name = record.get("name") or "Datei"
        file_id = record.get("id")
        local_info = self.controller.file_access_flow.get_local_file_info(record)
        size_label = local_info.get("size") or format_size(record.get("size")) or "Unbekannt"
        created_label = (
            local_info.get("created")
            or format_date(record.get("created_at"))
            or "Unbekannt"
        )

        details = [
            f"Name: {name}",
            f"ID: {file_id if file_id is not None else 'Unbekannt'}",
            f"Groesse: {size_label}",
            f"Erstellt: {created_label}",
        ]
        self.controller.datei_liste_view.show_error("Dateidetails\n\n" + "\n".join(details))

    def on_files_select_all_clicked(self):
        select_all = not self.controller.datei_liste_view.are_all_checked()
        self.controller.datei_liste_view.set_all_checked(select_all)

    def on_file_sort_changed(self, mode: str):
        self.controller.file_sort_mode = mode
        self.refresh_file_list_view()

    def on_file_search_changed(self, query: str):
        self.controller.file_search_query = query or ""
        self.refresh_file_list_view()
