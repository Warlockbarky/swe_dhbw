from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from View.Hauptoberflaeche import Hauptoberflaeche


class ChatView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.btn_back = QPushButton("Zurueck")
        self.btn_back.setObjectName("SecondaryButton")
        self.btn_select_files = QPushButton("Dateien waehlen")
        self.btn_select_files.setObjectName("GhostButton")
        self.btn_clear_files = QPushButton("Auswahl loeschen")
        self.btn_clear_files.setObjectName("GhostButton")
        self.selected_files_label = QLabel("Keine Dateien ausgewaehlt.")
        self.selected_files_label.setObjectName("HelperText")
        self.selected_files_label.setWordWrap(True)
        self.chat_scroll = QScrollArea()
        self.chat_scroll.setObjectName("ChatScroll")
        self.chat_scroll.setWidgetResizable(True)
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setSpacing(10)
        self.chat_layout.setContentsMargins(4, 4, 4, 4)
        self.chat_layout.addStretch()
        self.chat_scroll.setWidget(self.chat_container)
        self.chat_scroll.setMinimumHeight(260)
        self.chat_input = QLineEdit()
        self.chat_input.setPlaceholderText("Nachricht an die KI...")
        self.btn_send = QPushButton("Senden")
        self.btn_send.setObjectName("PrimaryButton")
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._on_typing_tick)
        self._typing_label = None
        self._typing_text = ""
        self._typing_index = 0
        self._typing_markdown = False
        self._loading_timer = QTimer(self)
        self._loading_timer.timeout.connect(self._on_loading_tick)
        self._loading_label = None
        self._loading_dots = 0
        self._refresh_pending = False
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.btn_back)
        actions.addStretch()

        files_row = QHBoxLayout()
        files_row.setSpacing(10)
        files_row.addWidget(self.btn_select_files)
        files_row.addWidget(self.btn_clear_files)
        files_row.addWidget(self.selected_files_label, stretch=1)

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        input_row.addWidget(self.chat_input)
        input_row.addWidget(self.btn_send)

        self.root.addLayout(actions)
        self.root.addLayout(files_row)
        self.root.addWidget(self.chat_scroll)
        self.root.addLayout(input_row)
        self.mittig_auf_bildschirm()

    def add_message(self, role: str, text: str, *, stream: bool = False):
        self._stop_typing(finalize=True)
        self._stop_loading(finalize=False)
        label = self._create_message_row(role)

        if stream and role == "assistant":
            self._start_typing(label, text, markdown=True)
        else:
            label.setMarkdown(text)
            self._scroll_to_bottom()

    def start_loading(self):
        self._stop_typing(finalize=True)
        self._stop_loading(finalize=False)
        label = self._create_message_row("assistant")
        self._loading_label = label
        self._loading_dots = 0
        label.setPlainText("...")
        self._loading_timer.start(300)
        self._scroll_to_bottom()

    def stop_loading_and_stream(self, text: str):
        if self._loading_label is None:
            self.add_message("assistant", text, stream=True)
            return
        label = self._loading_label
        self._stop_loading(finalize=False)
        self._start_typing(label, text, markdown=True)

    def get_chat_input(self) -> str:
        return self.chat_input.text()

    def clear_chat_input(self):
        self.chat_input.clear()

    def clear_chat(self):
        self._stop_typing(finalize=False)
        self._stop_loading(finalize=False)
        while self.chat_layout.count() > 1:
            item = self.chat_layout.takeAt(0)
            if item is not None:
                widget = item.widget()
                layout = item.layout()
                if widget is not None:
                    widget.deleteLater()
                elif layout is not None:
                    while layout.count():
                        child = layout.takeAt(0)
                        if child.widget():
                            child.widget().deleteLater()
                    layout.deleteLater()

    def refresh_message_sizes(self):
        self._refresh_all_message_sizes()
        if not self._refresh_pending:
            self._refresh_pending = True
            QTimer.singleShot(0, self._refresh_all_message_sizes)

    def _refresh_all_message_sizes(self):
        for i in range(self.chat_layout.count() - 1):
            item = self.chat_layout.itemAt(i)
            if item is None:
                continue
            row_layout = item.layout()
            if row_layout is None:
                continue
            for j in range(row_layout.count()):
                bubble_item = row_layout.itemAt(j)
                bubble = bubble_item.widget() if bubble_item else None
                if bubble is None:
                    continue
                view = bubble.findChild(QTextBrowser)
                if view is not None:
                    self._sync_message_size(view)
        self._refresh_pending = False

    def get_btn_send(self):
        return self.btn_send

    def get_btn_back(self):
        return self.btn_back

    def get_btn_select_files(self):
        return self.btn_select_files

    def get_btn_clear_files(self):
        return self.btn_clear_files

    def set_selected_files(self, names: list[str]):
        if not names:
            self.selected_files_label.setText("Keine Dateien ausgewaehlt.")
            return
        label = ", ".join(names)
        self.selected_files_label.setText(f"Ausgewaehlt: {label}")

    def set_send_enabled(self, enabled: bool):
        self.btn_send.setEnabled(enabled)
        self.chat_input.setEnabled(enabled)

    def _create_message_row(self, role: str) -> QTextBrowser:
        bubble = QFrame()
        bubble.setObjectName("chatBubble")
        bubble.setProperty("role", role)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 8, 12, 8)
        bubble_layout.setSpacing(0)
        bubble.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        view = QTextBrowser()
        view.setProperty("role", role)
        view.setOpenExternalLinks(True)
        view.setFrameShape(QFrame.Shape.NoFrame)
        view.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        view.setSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        view.setContentsMargins(0, 0, 0, 0)
        view.document().setDocumentMargin(0)
        view.document().contentsChanged.connect(
            lambda v=view: self._sync_message_size(v)
        )
        bubble_layout.addWidget(view)

        row = QHBoxLayout()
        row.setSpacing(8)
        if role == "assistant":
            row.addWidget(bubble, stretch=0)
            row.addStretch()
        else:
            row.addStretch()
            row.addWidget(bubble, stretch=0)

        self.chat_layout.insertLayout(self.chat_layout.count() - 1, row)
        self._sync_message_size(view)
        return view

    @staticmethod
    def _sync_message_size(view: QTextBrowser):
        doc = view.document()
        doc.setTextWidth(-1)
        doc_width = int(doc.idealWidth())
        margins = view.contentsMargins()
        padding = margins.top() + margins.bottom()
        extra = view.frameWidth() * 2

        role = view.property("role")
        if role == "assistant":
            min_width = 220
            max_width = 700
        else:
            min_width = 0
            max_width = 520

        target_width = max(min_width, min(max_width, doc_width + 24))
        view.setMinimumWidth(target_width)
        view.setMaximumWidth(target_width)
        doc.setTextWidth(target_width)

        doc_height = int(doc.documentLayout().documentSize().height())
        target_height = doc_height + padding + extra
        view.setMinimumHeight(target_height)
        view.setMaximumHeight(target_height)

        bubble = view.parentWidget()
        if bubble is not None:
            layout = bubble.layout()
            if layout is not None:
                margins = layout.contentsMargins()
                bubble_padding = margins.top() + margins.bottom()
            else:
                bubble_padding = 16
            bubble_height = target_height + bubble_padding
            bubble.setMinimumHeight(bubble_height)
            bubble.setMaximumHeight(bubble_height)
            bubble.setMinimumWidth(target_width + 24)
            bubble.setMaximumWidth(target_width + 24)

    def _start_typing(self, label: QTextBrowser, text: str, *, markdown: bool):
        self._typing_label = label
        self._typing_text = text
        self._typing_index = 0
        self._typing_markdown = markdown
        label.setPlainText("")
        self._typing_timer.start(12)

    def _on_typing_tick(self):
        if self._typing_label is None:
            self._typing_timer.stop()
            return
        step = 3
        self._typing_index = min(self._typing_index + step, len(self._typing_text))
        chunk = self._typing_text[: self._typing_index]
        self._typing_label.setPlainText(chunk)
        self._scroll_to_bottom()
        if self._typing_index >= len(self._typing_text):
            self._typing_timer.stop()
            if self._typing_markdown:
                self._typing_label.setMarkdown(self._typing_text)
            self._typing_label = None

    def _stop_typing(self, *, finalize: bool):
        if self._typing_label is None:
            return
        self._typing_timer.stop()
        if finalize:
            if self._typing_markdown:
                self._typing_label.setMarkdown(self._typing_text)
            else:
                self._typing_label.setPlainText(self._typing_text)
        self._typing_label = None

    def _on_loading_tick(self):
        if self._loading_label is None:
            self._loading_timer.stop()
            return
        self._loading_dots = (self._loading_dots + 1) % 4
        dots = "." * max(1, self._loading_dots)
        self._loading_label.setPlainText(dots)
        self._scroll_to_bottom()

    def _stop_loading(self, *, finalize: bool):
        if self._loading_label is None:
            return
        self._loading_timer.stop()
        if finalize:
            self._loading_label.setText("")
        self._loading_label = None

    def _scroll_to_bottom(self):
        bar = self.chat_scroll.verticalScrollBar()
        bar.setValue(bar.maximum())
