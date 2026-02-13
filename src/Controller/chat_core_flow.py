"""Chat flow that manages background AI requests."""

from PyQt6.QtCore import QThread

from controller.chat_worker import chat_worker


class chat_core_flow:
    """Coordinates chat session state and background worker lifecycle."""
    def __init__(self, controller):
        self.controller = controller

    def on_ai_summary_clicked(self):
        if not self.controller.auth_token:
            self.controller.datei_liste_view.show_error("Bitte zuerst einloggen.")
            return
        self.controller.is_temp_chat = False
        self.controller.chat_started = False
        self.controller.chat_view.clear_chat()
        self.controller.chat_view.clear_chat_input()
        self.controller.chat_file_context = []
        self.controller.chat_file_meta = []
        self.controller.chat_view.set_selected_files([])
        self.controller.current_chat_id = None
        self.controller.stack.setCurrentWidget(self.controller.chat_view)
        self.controller.chat_view.set_send_enabled(True)
        self.controller.chat_view.set_temp_chat_checked(False)
        self.controller.chat_view.set_temp_chat_enabled(True)

    def on_chat_send_clicked(self):
        text = self.controller.chat_view.get_chat_input().strip()
        if not text:
            return

        if not self.controller.chat_started:
            self.controller.is_temp_chat = self.controller.chat_view.is_temp_chat_checked()
            if not self.controller.is_temp_chat and not self.controller.current_chat_id:
                self.controller.current_chat_id = self.new_chat_session(title="Chat")
            self.controller.chat_started = True
            self.controller.chat_view.set_temp_chat_enabled(False)

        self.controller.chat_view.add_message("user", text)
        self.controller.chat_view.clear_chat_input()
        self.controller.chat_messages.append({"role": "user", "content": text})
        self.controller.chat_view.set_send_enabled(False)
        self.controller.chat_view.start_loading()
        self.start_chat_worker(
            mode="chat",
            payload={"messages": self.build_chat_request_messages()},
        )

    def on_chat_back_clicked(self):
        if self.controller.is_temp_chat:
            self.controller.current_chat_id = None
            self.controller.chat_messages = []
            self.controller.chat_file_context = []
            self.controller.chat_file_meta = []
            self.controller.chat_view.clear_chat()
            self.controller.chat_view.clear_chat_input()
            self.controller.chat_view.set_selected_files([])
            self.controller.chat_view.set_temp_chat_checked(False)
            self.controller.chat_view.set_temp_chat_enabled(True)
            self.controller.chat_started = False
        self.controller.stack.setCurrentWidget(self.controller.datei_liste_view)

    def start_chat_worker(self, *, mode: str, payload: dict):
        """Start a background worker to avoid blocking the UI thread.

        Args:
            mode (str): Worker mode identifier.
            payload (dict): Serialized request payload for the worker.

        Returns:
            None
        """
        if self.controller._chat_thread is not None and self.controller._chat_thread.isRunning():
            # Prevent concurrent workers from racing against shared UI state.
            return
        thread = QThread()
        worker = chat_worker(
            mode=mode,
            payload=payload,
            analyzer=self.controller.ki_analyzer,
            api_base_url=self.controller.api_base_url,
            auth_token=self.controller.auth_token or "",
            ai_prefs=self.controller.settings_flow.build_ai_preferences(),
        )
        worker.moveToThread(thread)
        thread.started.connect(worker.run)
        worker.finished.connect(self.on_chat_worker_finished)
        worker.failed.connect(self.on_chat_worker_failed)
        worker.finished.connect(thread.quit)
        worker.failed.connect(thread.quit)
        thread.finished.connect(self.on_chat_thread_finished)
        thread.finished.connect(thread.deleteLater)
        thread.finished.connect(worker.deleteLater)
        self.controller._chat_thread = thread
        self.controller._chat_worker = worker
        thread.start()

    def on_chat_worker_finished(self, result: dict):
        assistant_text = result.get("assistant", "")
        if assistant_text:
            self.controller.chat_messages.append(
                {"role": "assistant", "content": assistant_text}
            )

        self.controller.chat_view.set_send_enabled(True)
        self.controller.chat_view.stop_loading_and_stream(assistant_text)
        if (
            not self.controller.is_temp_chat
            and self.controller.chat_started
            and self.controller.current_chat_id
        ):
            self.persist_current_chat()

    def on_chat_worker_failed(self, message: str):
        self.controller.chat_view.set_send_enabled(True)
        self.controller.chat_view.stop_loading_and_stream("")
        self.controller.datei_liste_view.show_error(f"KI Chat fehlgeschlagen: {message}")

    def on_chat_thread_finished(self):
        self.controller._chat_thread = None
        self.controller._chat_worker = None

    def build_chat_request_messages(self) -> list[dict]:
        system_msg = (
            "You are a helpful assistant. Use the provided file context when relevant. "
            "If the question is not about the file, answer normally."
        )
        ai_prefs = self.controller.settings_flow.build_ai_preferences()
        if ai_prefs:
            system_msg = f"{system_msg}\n\nUser preferences:\n{ai_prefs}"

        messages = [{"role": "system", "content": system_msg}]
        for entry in self.controller.chat_file_context:
            name = entry.get("name") or "Datei"
            content = entry.get("content") or ""
            context_msg = f"File name: {name}\n\nFile content:\n{content}"
            messages.append({"role": "user", "content": context_msg})

        messages.extend(self.controller.chat_messages)
        return messages

    def new_chat_session(self, *, title: str) -> str:
        if self.controller.is_temp_chat:
            return ""
        chat_id = self.controller.history_service.create_chat_session(
            title=title, files=self.controller.chat_file_meta
        )
        self.controller.current_chat_id = chat_id
        self.controller.chat_messages = []
        return chat_id

    def persist_current_chat(self):
        if not self.controller.current_chat_id:
            return
        self.controller.history_service.update_chat_session(
            chat_id=self.controller.current_chat_id,
            messages=self.controller.chat_messages,
            files=self.controller.chat_file_meta,
        )

    def render_chat_messages(self, messages: list[dict]):
        for msg in messages:
            role = msg.get("role")
            if role not in {"user", "assistant"}:
                continue
            text = str(msg.get("content") or "")
            self.controller.chat_view.add_message(role, text, stream=False)
        self.controller.chat_view.refresh_message_sizes()
