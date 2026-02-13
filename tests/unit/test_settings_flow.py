from controller.settings_flow import settings_flow


class DummySettings:
    def __init__(self):
        self.store = {}

    def value(self, key, default=None, type=str):
        if key not in self.store:
            return default
        value = self.store[key]
        if type is None:
            return value
        try:
            return type(value)
        except Exception:
            return value

    def setValue(self, key, value):
        self.store[key] = value


class DummyView:
    def __init__(self):
        self.applied = []

    def apply_theme(self, theme: str, palette: str):
        self.applied.append((theme, palette))


class DummyController:
    def __init__(self):
        self.settings = DummySettings()
        self.start_view = DummyView()
        self.login_view = DummyView()
        self.pfad_view = DummyView()
        self.datei_liste_view = DummyView()
        self.chat_view = DummyView()
        self.history_view = DummyView()


def test_build_ai_preferences_includes_notes():
    controller = DummyController()
    controller.settings.setValue("ai/tone", "Friendly")
    controller.settings.setValue("ai/format", "Plain")
    controller.settings.setValue("ai/length", "Short")
    controller.settings.setValue("ai/notes", "Use bullets")

    flow = settings_flow(controller)
    prefs = flow.build_ai_preferences()
    assert "Tone: Friendly" in prefs
    assert "Notes: Use bullets" in prefs


def test_apply_theme_values_updates_views():
    controller = DummyController()
    flow = settings_flow(controller)

    flow.apply_theme_values({"theme": "Dark", "palette": "Blue"})

    assert controller.start_view.applied
    assert controller.chat_view.applied
