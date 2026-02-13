from view.chat_view import chat_view


def test_chat_view_message_flow(qtbot):
    view = chat_view()
    qtbot.addWidget(view)

    view.add_message("user", "Hello", stream=False)
    view.add_message("assistant", "Hi there", stream=False)

    view.start_loading()
    view._on_loading_tick()
    view.stop_loading_and_stream("Done")

    view.add_message("assistant", "Stream", stream=True)
    for _ in range(5):
        view._on_typing_tick()
    view._stop_typing(finalize=True)

    view.set_send_enabled(False)
    assert view.btn_send.isEnabled() is False

    view.set_selected_files(["a.txt", "b.txt"])
    assert "a.txt" in view.selected_files_label.text()

    view.clear_chat()
    assert view.chat_layout.count() == 1


def test_chat_view_refresh_sizes(qtbot):
    view = chat_view()
    qtbot.addWidget(view)

    view.add_message("user", "Hello")
    view.add_message("assistant", "World")
    view.refresh_message_sizes()
