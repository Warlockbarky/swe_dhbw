from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

from View.Hauptoberflaeche import Hauptoberflaeche


class ChatView(Hauptoberflaeche):
    def __init__(self):
        super().__init__()
        self.btn_back = QPushButton("Zurueck")
        self.chat_scroll = QScrollArea()
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
        self._typing_timer = QTimer(self)
        self._typing_timer.timeout.connect(self._on_typing_tick)
        self._typing_label = None
        self._typing_text = ""
        self._typing_index = 0
        self._loading_timer = QTimer(self)
        self._loading_timer.timeout.connect(self._on_loading_tick)
        self._loading_label = None
        self._loading_dots = 0
        self.__fenster_erstellen()

    def __fenster_erstellen(self):
        actions = QHBoxLayout()
        actions.setSpacing(10)
        actions.addWidget(self.btn_back)
        actions.addStretch()

        input_row = QHBoxLayout()
        input_row.setSpacing(10)
        input_row.addWidget(self.chat_input)
        input_row.addWidget(self.btn_send)

        self.root.addLayout(actions)
        self.root.addWidget(self.chat_scroll)
        self.root.addLayout(input_row)
        self.mittig_auf_bildschirm()

    def add_message(self, role: str, text: str, *, stream: bool = False):
        self._stop_typing(finalize=True)
        self._stop_loading(finalize=False)
        label = self._create_message_row(role)

        if stream and role == "assistant":
            self._start_typing(label, text)
        else:
            label.setText(text)
            self._scroll_to_bottom()

    def start_loading(self):
        self._stop_typing(finalize=True)
        self._stop_loading(finalize=False)
        label = self._create_message_row("assistant")
        self._loading_label = label
        self._loading_dots = 0
        label.setText("...")
        self._loading_timer.start(300)
        self._scroll_to_bottom()

    def stop_loading_and_stream(self, text: str):
        if self._loading_label is None:
            self.add_message("assistant", text, stream=True)
            return
        label = self._loading_label
        self._stop_loading(finalize=False)
        self._start_typing(label, text)

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

    def get_btn_send(self):
        return self.btn_send

    def get_btn_back(self):
        return self.btn_back

    def set_send_enabled(self, enabled: bool):
        self.btn_send.setEnabled(enabled)
        self.chat_input.setEnabled(enabled)

    def _create_message_row(self, role: str) -> QLabel:
        bubble = QFrame()
        bubble.setObjectName("chatBubble")
        bubble.setProperty("role", role)
        bubble_layout = QVBoxLayout(bubble)
        bubble_layout.setContentsMargins(12, 8, 12, 8)

        label = QLabel("")
        label.setProperty("role", role)
        label.setWordWrap(True)
        label.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        label.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        bubble_layout.addWidget(label)

        if role == "assistant":
            bubble.setMaximumWidth(700)
            label.setMaximumWidth(680)
        else:
            bubble.setMaximumWidth(520)
            label.setMaximumWidth(500)

        row = QHBoxLayout()
        row.setSpacing(8)
        if role == "assistant":
            row.addWidget(bubble, stretch=0)
            row.addStretch()
        else:
            row.addStretch()
            row.addWidget(bubble, stretch=0)

        self.chat_layout.insertLayout(self.chat_layout.count() - 1, row)
        return label

    def _start_typing(self, label: QLabel, text: str):
        self._typing_label = label
        self._typing_text = text
        self._typing_index = 0
        label.setText("")
        self._typing_timer.start(12)

    def _on_typing_tick(self):
        if self._typing_label is None:
            self._typing_timer.stop()
            return
        step = 3
        self._typing_index = min(self._typing_index + step, len(self._typing_text))
        self._typing_label.setText(self._typing_text[: self._typing_index])
        self._scroll_to_bottom()
        if self._typing_index >= len(self._typing_text):
            self._typing_timer.stop()
            self._typing_label = None

    def _stop_typing(self, *, finalize: bool):
        if self._typing_label is None:
            return
        self._typing_timer.stop()
        if finalize:
            self._typing_label.setText(self._typing_text)
        self._typing_label = None

    def _on_loading_tick(self):
        if self._loading_label is None:
            self._loading_timer.stop()
            return
        self._loading_dots = (self._loading_dots + 1) % 4
        dots = "." * max(1, self._loading_dots)
        self._loading_label.setText(dots)
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
