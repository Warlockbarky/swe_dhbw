from view.login_view import login_view


def test_login_view_inputs(qtbot):
    view = login_view()
    qtbot.addWidget(view)
    view.set_username("  user  ")
    view.set_password("  pass  ")
    assert view.get_username() == "user"
    assert view.get_password() == "pass"

    view.set_remember_checked(True)
    assert view.get_remember_checked() is True
