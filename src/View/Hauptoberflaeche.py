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
        self.apply_theme("light", "emerald")
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

    @staticmethod
    def build_stylesheet(theme: str, palette: str) -> str:
        theme = (theme or "light").lower()
        palette = (palette or "emerald").lower()

        if theme == "dark":
            colors = {
                "bg": "#0b0f19",
                "text": "#e5e7eb",
                "muted": "#94a3b8",
                "surface": "#111827",
                "border": "#1f2937",
                "bubble_user": "#1f2937",
                "bubble_ai": "#111827",
                "list_sel_bg": "#1f2937",
                "list_sel_text": "#e5e7eb",
            }
        else:
            colors = {
                "bg": "#fafafa",
                "text": "#0f172a",
                "muted": "#64748b",
                "surface": "#ffffff",
                "border": "#e5e7eb",
                "bubble_user": "#f1f5f9",
                "bubble_ai": "#ffffff",
                "list_sel_bg": "#dbeafe",
                "list_sel_text": "#1e3a8a",
            }

        accents = {
            "emerald": ("#10b981", "#0ea5a1", "#0f766e"),
            "blue": ("#2563eb", "#1d4ed8", "#1e40af"),
            "slate": ("#334155", "#1f2937", "#0f172a"),
        }
        accent, accent_hover, accent_press = accents.get(palette, accents["emerald"])

        return f"""
            QWidget {{
                background: {colors['bg']};
                color: {colors['text']};
                font-family: "Segoe UI", "Helvetica Neue", Arial;
                font-size: 15px;
            }}
            QLabel {{
                color: {colors['text']};
                font-size: 15px;
                font-weight: 500;
            }}
            QLineEdit, QTextEdit, QListWidget {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
                padding: 10px 12px;
            }}
            QLineEdit:focus, QTextEdit:focus, QListWidget:focus {{
                border: 1px solid {accent};
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 8px;
            }}
            QListWidget::item:selected {{
                background: {colors['list_sel_bg']};
                color: {colors['list_sel_text']};
            }}
            QScrollArea {{
                border: 0;
                background: transparent;
            }}
            QFrame#chatBubble {{
                border-radius: 18px;
            }}
            QFrame#chatBubble[role="assistant"] {{
                background: {colors['bubble_ai']};
                border: 1px solid {colors['border']};
            }}
            QFrame#chatBubble[role="user"] {{
                background: {colors['bubble_user']};
                border: 1px solid {colors['border']};
            }}
            QFrame#chatBubble[role="user"] QLabel {{
                color: {colors['text']};
            }}
            QFrame#chatBubble QTextBrowser {{
                background: transparent;
                border: 0;
                padding: 0;
            }}
            QFrame#chatBubble QTextBrowser * {{
                font-size: 15px;
                line-height: 1.5;
                background: transparent;
            }}
            QPushButton {{
                background: {accent};
                color: #ffffff;
                border: 0;
                border-radius: 12px;
                padding: 8px 14px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                background: {accent_hover};
            }}
            QPushButton:pressed {{
                background: {accent_press};
            }}
            QPushButton:disabled {{
                background: {colors['border']};
                color: {colors['muted']};
            }}
            """

    def apply_theme(self, theme: str, palette: str) -> None:
        self.setStyleSheet(self.build_stylesheet(theme, palette))
