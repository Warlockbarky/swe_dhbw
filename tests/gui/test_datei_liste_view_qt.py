from view.datei_liste_view import datei_liste_view


def test_datei_liste_view_items_and_checks(qtbot):
    view = datei_liste_view()
    qtbot.addWidget(view)
    view.set_items(["1: report.pdf", "2: notes.txt"])
    assert view.list_widget.count() == 2

    assert view.are_all_checked() is False
    view.set_all_checked(True)
    assert view.are_all_checked() is True


def test_datei_liste_view_signals(qtbot):
    view = datei_liste_view()
    qtbot.addWidget(view)

    with qtbot.waitSignal(view.sort_changed, timeout=1000):
        view.sort_combo.setCurrentText("Name (Z-A)")

    with qtbot.waitSignal(view.search_changed, timeout=1000):
        view.search_input.setText("report")
