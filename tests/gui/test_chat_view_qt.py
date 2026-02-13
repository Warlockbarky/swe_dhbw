from view.chat_view import chat_view


def test_chat_view_temp_chat_and_selected_files(qtbot):
    view = chat_view()
    qtbot.addWidget(view)

    view.set_temp_chat_checked(True)
    assert "aktiv" in view.btn_temp_chat.text().lower()

    view.set_selected_files(["a.txt", "b.txt"])
    assert "a.txt" in view.selected_files_label.text()
