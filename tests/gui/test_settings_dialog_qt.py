from view.settings_dialog import settings_dialog


def test_settings_dialog_set_get_values(qtbot, monkeypatch):
    dialog = settings_dialog()
    qtbot.addWidget(dialog)

    dialog.set_values(
        {
            "theme": "Dark",
            "palette": "Blue",
            "default_path": "/tmp",
            "ai_tone": "Formal",
            "ai_format": "Plain",
            "ai_length": "Short",
            "ai_notes": "Use bullets",
        }
    )

    values = dialog.get_values()
    assert values["theme"] == "Dark"
    assert values["palette"] == "Blue"
    assert values["default_path"] == "/tmp"
    assert values["ai_notes"] == "Use bullets"

    monkeypatch.setattr(
        "view.settings_dialog.QFileDialog.getExistingDirectory",
        lambda *a, **k: "/var/tmp",
    )
    dialog._settings_dialog__choose_path()
    assert dialog.default_path.text() == "/var/tmp"
