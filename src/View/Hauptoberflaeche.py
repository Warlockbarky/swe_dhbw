from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class Hauptoberflaeche(QWidget):
    def __init__(self, title: str = "", width: int = 1200, height: int = 800):
        super().__init__()
        self.setObjectName("MainWindow")
        self.setMinimumSize(width, height)
        self.resize(width, height)
        self.root = QVBoxLayout(self)
        self.root.setContentsMargins(20, 20, 20, 20)
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
    def _resolve_colors(theme: str, palette: str) -> dict:
        theme = (theme or "light").lower()
        palette = (palette or "emerald").lower()

        if theme == "dark":
            colors = {
                "bg": "#0B1220",
                "surface": "#111A2E",
                "surface_alt": "#0F172A",
                "border": "#22304A",
                "text": "#E5E7EB",
                "text_muted": "#9CA3AF",
                "danger": "#F87171",
                "success": "#34D399",
                "list_hover": "rgba(96, 165, 250, 0.10)",
                "list_selected": "rgba(96, 165, 250, 0.20)",
            }
            accents = {
                "emerald": ("#34D399", "#10B981", "#059669"),
                "blue": ("#60A5FA", "#3B82F6", "#2563EB"),
                "slate": ("#94A3B8", "#64748B", "#475569"),
            }
        else:
            colors = {
                "bg": "#F7F8FA",
                "surface": "#FFFFFF",
                "surface_alt": "#F1F3F5",
                "border": "#E3E6EA",
                "text": "#111827",
                "text_muted": "#6B7280",
                "danger": "#DC2626",
                "success": "#16A34A",
                "list_hover": "rgba(37, 99, 235, 0.08)",
                "list_selected": "rgba(37, 99, 235, 0.18)",
            }
            accents = {
                "emerald": ("#10B981", "#059669", "#047857"),
                "blue": ("#2563EB", "#1D4ED8", "#1E40AF"),
                "slate": ("#334155", "#1F2937", "#0F172A"),
            }

        accent, accent_hover, accent_press = accents.get(palette, accents["emerald"])
        focus_ring = "rgba(37, 99, 235, 0.25)" if palette == "blue" else "rgba(16, 185, 129, 0.25)"

        return {
            "theme": theme,
            "palette": palette,
            "colors": colors,
            "accent": accent,
            "accent_hover": accent_hover,
            "accent_press": accent_press,
            "focus_ring": focus_ring,
        }

    @classmethod
    def build_stylesheet(cls, theme: str, palette: str) -> str:
        tokens = cls._resolve_colors(theme, palette)
        colors = tokens["colors"]
        accent = tokens["accent"]
        accent_hover = tokens["accent_hover"]
        accent_press = tokens["accent_press"]
        focus_ring = tokens["focus_ring"]

        return f"""
            /* Base */
            QWidget {{
                background: {colors['bg']};
                color: {colors['text']};
                font-family: "Segoe UI", "SF Pro Text", "Helvetica Neue", "Noto Sans", "DejaVu Sans", Arial;
                font-size: 14px;
            }}
            QLabel {{
                color: {colors['text']};
            }}
            QLabel#SectionTitle {{
                font-size: 16px;
                font-weight: 600;
            }}
            QLabel#FieldLabel {{
                color: {colors['text_muted']};
                font-size: 12px;
            }}
            QLabel#HelperText {{
                color: {colors['text_muted']};
                font-size: 12px;
            }}

            /* Cards */
            QFrame#Card {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
            }}
            QFrame#Sidebar {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 12px;
            }}

            /* Inputs */
            QLineEdit, QTextEdit, QPlainTextEdit, QComboBox {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 8px;
                padding: 8px 10px;
                min-height: 34px;
                selection-background-color: {accent};
                selection-color: #ffffff;
            }}
            QLineEdit:hover, QTextEdit:hover, QPlainTextEdit:hover, QComboBox:hover {{
                border: 1px solid {accent_hover};
            }}
            QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
                border: 1px solid {accent};
                background: {colors['surface']};
            }}
            QLineEdit#ErrorField, QTextEdit#ErrorField, QPlainTextEdit#ErrorField, QComboBox#ErrorField {{
                border: 1px solid {colors['danger']};
                background: rgba(220, 38, 38, 0.06);
            }}
            QLineEdit::placeholder {{
                color: {colors['text_muted']};
            }}

            /* ComboBox dropdown */
            QComboBox::drop-down {{
                border: 0;
                width: 22px;
                subcontrol-origin: padding;
                subcontrol-position: right center;
            }}
            QComboBox::down-arrow {{
                width: 10px;
                height: 10px;
            }}
            QComboBox QAbstractItemView {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                selection-background-color: {colors['list_selected']};
                selection-color: {colors['text']};
                outline: 0;
            }}
            QComboBox QAbstractItemView::item {{
                padding: 6px 10px;
                min-height: 28px;
            }}
            QComboBox QAbstractItemView::item:hover {{
                background: {colors['list_hover']};
            }}

            /* Buttons */
            QPushButton, QToolButton {{
                min-height: 34px;
                padding: 8px 12px;
                border-radius: 8px;
                border: 1px solid {colors['border']};
                background: {colors['surface_alt']};
                color: {colors['text']};
            }}
            QPushButton:hover, QToolButton:hover {{
                background: {colors['surface']};
                border: 1px solid {accent_hover};
            }}
            QPushButton:pressed, QToolButton:pressed {{
                background: {colors['surface_alt']};
                border: 1px solid {accent_press};
            }}
            QPushButton:disabled, QToolButton:disabled {{
                background: {colors['surface_alt']};
                color: {colors['text_muted']};
                border: 1px solid {colors['border']};
            }}
            QPushButton#PrimaryButton, QToolButton#PrimaryButton {{
                background: {accent};
                border: 0;
                color: #ffffff;
                font-weight: 600;
            }}
            QPushButton#PrimaryButton:hover, QToolButton#PrimaryButton:hover {{
                background: {accent_hover};
            }}
            QPushButton#PrimaryButton:pressed, QToolButton#PrimaryButton:pressed {{
                background: {accent_press};
            }}
            QPushButton#SecondaryButton, QToolButton#SecondaryButton {{
                background: {colors['surface_alt']};
                border: 1px solid {colors['border']};
                color: {colors['text']};
            }}
            QPushButton#GhostButton, QToolButton#GhostButton {{
                background: transparent;
                border: 0;
                color: {accent};
                padding: 6px 8px;
            }}
            QPushButton#GhostButton:hover, QToolButton#GhostButton:hover {{
                background: rgba(37, 99, 235, 0.08);
            }}
            QPushButton#DangerButton, QToolButton#DangerButton {{
                background: {colors['danger']};
                border: 0;
                color: #ffffff;
            }}
            QPushButton#DangerButton:hover, QToolButton#DangerButton:hover {{
                background: rgba(220, 38, 38, 0.9);
            }}

            /* Checkbox / Radio */
            QCheckBox, QRadioButton {{
                spacing: 8px;
                color: {colors['text']};
            }}
            QCheckBox::indicator, QRadioButton::indicator {{
                width: 16px;
                height: 16px;
            }}
            QCheckBox::indicator {{
                border: 1px solid {colors['border']};
                border-radius: 4px;
                background: {colors['surface']};
            }}
            QCheckBox::indicator:hover {{
                border: 1px solid {accent};
            }}
            QCheckBox::indicator:checked {{
                background: {accent};
                border: 1px solid {accent};
            }}
            QRadioButton::indicator {{
                border: 1px solid {colors['border']};
                border-radius: 8px;
                background: {colors['surface']};
            }}
            QRadioButton::indicator:checked {{
                background: {accent};
                border: 1px solid {accent};
            }}

            /* Tabs */
            QTabWidget::pane {{
                border: 1px solid {colors['border']};
                border-radius: 10px;
                background: {colors['surface']};
            }}
            QTabBar::tab {{
                background: transparent;
                color: {colors['text_muted']};
                padding: 8px 14px;
                min-height: 30px;
                border: 0;
            }}
            QTabBar::tab:selected {{
                color: {colors['text']};
                border-bottom: 2px solid {accent};
            }}

            /* Lists / Tables */
            QListWidget, QTableView {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 10px;
                padding: 6px;
            }}
            QListWidget::item {{
                padding: 6px 8px;
                border-radius: 6px;
            }}
            QListWidget::item:hover {{
                background: {colors['list_hover']};
            }}
            QListWidget::item:selected {{
                background: {colors['list_selected']};
                color: {colors['text']};
            }}
            QHeaderView::section {{
                background: {colors['surface_alt']};
                color: {colors['text_muted']};
                padding: 6px 8px;
                border: 0;
                font-weight: 600;
            }}
            QTableView::item:selected {{
                background: {colors['list_selected']};
            }}

            /* Scrollbar */
            QScrollBar:vertical, QScrollBar:horizontal {{
                background: transparent;
                width: 10px;
                height: 10px;
                margin: 0;
            }}
            QScrollBar::handle:vertical, QScrollBar::handle:horizontal {{
                background: {colors['border']};
                border-radius: 5px;
                min-height: 24px;
                min-width: 24px;
            }}
            QScrollBar::handle:vertical:hover, QScrollBar::handle:horizontal:hover {{
                background: {colors['text_muted']};
            }}
            QScrollBar::add-line, QScrollBar::sub-line {{
                width: 0;
                height: 0;
            }}

            /* Menu */
            QMenu {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
                border-radius: 10px;
                padding: 6px;
            }}
            QMenu::item {{
                padding: 8px 12px;
                border-radius: 6px;
            }}
            QMenu::item:selected {{
                background: {colors['list_hover']};
            }}
            QMenu::separator {{
                height: 1px;
                background: {colors['border']};
                margin: 6px 8px;
            }}

            /* Tooltips */
            QToolTip {{
                background: {colors['surface']};
                color: {colors['text']};
                border: 1px solid {colors['border']};
                border-radius: 6px;
                padding: 6px 8px;
            }}

            /* Chat bubbles */
            QScrollArea#ChatScroll {{
                border: 0;
                background: transparent;
            }}
            QFrame#chatBubble {{
                border-radius: 12px;
            }}
            QFrame#chatBubble[role="assistant"] {{
                background: {colors['surface']};
                border: 1px solid {colors['border']};
            }}
            QFrame#chatBubble[role="user"] {{
                background: {colors['surface_alt']};
                border: 1px solid {colors['border']};
            }}
            QFrame#chatBubble QTextBrowser {{
                background: transparent;
                border: 0;
                padding: 0;
            }}
            QFrame#chatBubble QTextBrowser * {{
                font-size: 14px;
                line-height: 1.5;
                background: transparent;
            }}
        """

    @classmethod
    def build_palette(cls, theme: str, palette: str) -> QPalette:
        tokens = cls._resolve_colors(theme, palette)
        colors = tokens["colors"]
        accent = tokens["accent"]

        pal = QPalette()
        pal.setColor(QPalette.ColorRole.Window, QColor(colors["bg"]))
        pal.setColor(QPalette.ColorRole.WindowText, QColor(colors["text"]))
        pal.setColor(QPalette.ColorRole.Base, QColor(colors["surface"]))
        pal.setColor(QPalette.ColorRole.AlternateBase, QColor(colors["surface_alt"]))
        pal.setColor(QPalette.ColorRole.Text, QColor(colors["text"]))
        pal.setColor(QPalette.ColorRole.Button, QColor(colors["surface_alt"]))
        pal.setColor(QPalette.ColorRole.ButtonText, QColor(colors["text"]))
        pal.setColor(QPalette.ColorRole.ToolTipBase, QColor(colors["surface"]))
        pal.setColor(QPalette.ColorRole.ToolTipText, QColor(colors["text"]))
        pal.setColor(QPalette.ColorRole.Highlight, QColor(accent))
        pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#ffffff"))
        return pal

    def apply_theme(self, theme: str, palette: str) -> None:
        app = QApplication.instance()
        if app is None:
            self.setStyleSheet(self.build_stylesheet(theme, palette))
            return
        app.setPalette(self.build_palette(theme, palette))
        app.setStyleSheet(self.build_stylesheet(theme, palette))
