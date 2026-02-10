from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QApplication


class Hauptoberflaeche(QWidget):
    def __init__(self, title: str = "", width: int = 720, height: int = 520):
        super().__init__()
        self.setMinimumSize(width, height)
        self.resize(width, height)
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(24, 20, 24, 24)
        self.root.setSpacing(12)
        if title:
            self.root.addWidget(QLabel(title))
        self._apply_theme()
    def mittig_auf_bildschirm(self):
        screen = QApplication.primaryScreen().availableGeometry()
        self.move(
            (screen.width() - self.width()) // 2,
            (screen.height() - self.height()) // 2
        )

    def show_error(self, msg: str):
        print("ERROR:", msg)
    def show_UI(self):
        self.show()

    def _apply_theme(self):
        self.setStyleSheet(
            """
            QWidget {
                background: #fafafa;
                color: #0f172a;
                font-family: "Segoe UI", "Helvetica Neue", Arial;
                font-size: 15px;
            }
            QLabel {
                color: #0f172a;
                font-size: 15px;
                font-weight: 500;
            }
            QLineEdit, QTextEdit, QListWidget {
                background: #ffffff;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 10px 12px;
            }
            QLineEdit:focus, QTextEdit:focus, QListWidget:focus {
                border: 1px solid #2563eb;
            }
            QListWidget::item {
                padding: 6px 8px;
                border-radius: 8px;
            }
            QListWidget::item:selected {
                background: #dbeafe;
                color: #1e3a8a;
            }
            QScrollArea {
                border: 0;
                background: transparent;
            }
            QFrame#chatBubble {
                border-radius: 18px;
            }
            QFrame#chatBubble[role="assistant"] {
                background: #ffffff;
                border: 1px solid #e5e7eb;
            }
            QFrame#chatBubble[role="user"] {
                background: #f1f5f9;
                border: 1px solid #e2e8f0;
            }
            QFrame#chatBubble[role="user"] QLabel {
                color: #0f172a;
            }
            QFrame#chatBubble QLabel {
                font-size: 15px;
                line-height: 1.5;
                background: transparent;
            }
            QPushButton {
                background: #10b981;
                color: #ffffff;
                border: 0;
                border-radius: 12px;
                padding: 8px 14px;
                font-weight: 600;
            }
            QPushButton:hover {
                background: #0ea5a1;
            }
            QPushButton:pressed {
                background: #0f766e;
            }
            QPushButton:disabled {
                background: #e2e8f0;
                color: #94a3b8;
            }
            """
        )
