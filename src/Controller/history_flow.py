from datetime import datetime

from PyQt6.QtWidgets import QMessageBox, QInputDialog


class history_flow:
    def __init__(self, controller):
        self.controller = controller

    def on_history_clicked(self):
        self.refresh_history_view()
        self.controller.stack.setCurrentWidget(self.controller.history_view)

    def on_history_open_clicked(self):
        self.controller.is_temp_chat = False
        self.controller.chat_started = True
        history = self.controller.visible_history_entries
        idx = self.controller.history_view.get_selected_index()
        if idx < 0 or idx >= len(history):
            self.controller.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return
        self.controller.chat_file_flow.open_history_entry(history, idx)

    def on_history_open_requested(self, row: int):
        history = self.controller.visible_history_entries
        if row < 0 or row >= len(history):
            self.controller.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return
        self.controller.chat_file_flow.open_history_entry(history, row)

    def on_history_delete_clicked(self):
        history = self.controller.visible_history_entries
        checked_rows = self.controller.history_view.get_checked_indices()
        selected_rows = self.controller.history_view.get_selected_indices()
        selected_rows = sorted(set(checked_rows or selected_rows))
        if not selected_rows:
            self.controller.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return

        entries = [history[row] for row in selected_rows if 0 <= row < len(history)]
        if not entries:
            self.controller.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return

        if len(entries) == 1:
            title = entries[0].get("title") or "Chat"
            confirm_text = f"Soll der Chat '{title}' wirklich geloescht werden?"
        else:
            confirm_text = f"Sollen {len(entries)} Chats wirklich geloescht werden?"

        confirm = QMessageBox.question(
            self.controller.history_view,
            "Chat loeschen",
            confirm_text,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        if confirm != QMessageBox.StandardButton.Yes:
            return

        removed_ids = {entry.get("id") for entry in entries}
        saved_history = self.controller.history_service.load()
        remaining = [entry for entry in saved_history if entry.get("id") not in removed_ids]
        self.controller.history_service.save(remaining)
        if self.controller.current_chat_id in removed_ids:
            self.controller.current_chat_id = None
            self.controller.chat_messages = []
            self.controller.chat_file_context = []
            self.controller.chat_file_meta = []
            self.controller.chat_view.clear_chat()
            self.controller.chat_view.set_selected_files([])
        self.refresh_history_view()

    def on_history_select_all_clicked(self):
        select_all = not self.controller.history_view.are_all_checked()
        self.controller.history_view.set_all_checked(select_all)

    def on_history_sort_changed(self, mode: str):
        self.controller.history_sort_mode = mode
        self.refresh_history_view()

    def on_history_search_changed(self, query: str):
        self.controller.history_search_query = query or ""
        self.refresh_history_view()

    def on_history_rename_clicked(self):
        history = self.controller.visible_history_entries
        idx = self.controller.history_view.get_selected_index()
        if idx < 0 or idx >= len(history):
            self.controller.history_view.show_error("Bitte einen Verlauf auswaehlen.")
            return

        entry = history[idx]
        chat_id = entry.get("id")
        current_title = (entry.get("title") or "Chat").strip()
        new_title, accepted = QInputDialog.getText(
            self.controller.history_view,
            "Chat umbenennen",
            "Neuer Name:",
            text=current_title,
        )
        if not accepted:
            return

        new_title = new_title.strip()
        if not new_title:
            self.controller.history_view.show_error("Der Chatname darf nicht leer sein.")
            return

        saved_history = self.controller.history_service.load()
        renamed = False
        for item in saved_history:
            if item.get("id") == chat_id:
                item["title"] = new_title
                item["updated_at"] = datetime.now().isoformat(timespec="seconds")
                renamed = True
                break

        if not renamed:
            self.controller.history_view.show_error("Der Chat konnte nicht gefunden werden.")
            return

        self.controller.history_service.save(saved_history)
        self.refresh_history_view()

    def refresh_history_view(self):
        history = self.controller.history_service.load()
        sorted_entries = self.controller.history_service.sort(
            history, self.controller.history_sort_mode
        )
        query = self.controller.history_search_query.strip().lower()
        if query:
            sorted_entries = [
                entry
                for entry in sorted_entries
                if query in str(entry.get("title") or "").lower()
            ]
        self.controller.visible_history_entries = sorted_entries
        self.controller.history_view.set_items(
            self.controller.history_service.format_items(self.controller.visible_history_entries)
        )

    def on_history_back_clicked(self):
        self.controller.stack.setCurrentWidget(self.controller.datei_liste_view)
