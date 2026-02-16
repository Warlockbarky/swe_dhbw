# Tests und Qualitaet

Dieses Projekt enthaelt einen umfangreichen Satz an Tests fuer eine PyQt6 Desktop-Anwendung mit Backend-Kommunikation. Ziel ist eine stabile Abdeckung der Kernlogik und ein realistisches Testniveau fuer ein universitaires Software-Engineering-Projekt.

## Programmstart und Installation (Poetry + venv)

Fuehre im Projekt-Root folgende Befehle aus:

```bash
python3 -m venv .venv
source .venv/bin/activate
poetry install
```

Danach in den `src`-Ordner wechseln und die Anwendung starten:

```bash
cd src
python3 main.py
```

## Testziele und Abdeckung

Aktueller Fokus:

- Hohe Abdeckung der Controller-Logik
- Stabile Unit-Tests fuer Hilfsfunktionen und Services
- GUI-Tests fuer zentrale Views
- Systemtests gegen ein lokales Fake-Backend
- Akzeptanztests mit klaren Annahmen

Die Coverage liegt bei 80% und wird mit `pytest --cov=src --cov-report=term-missing` gemessen.

## Testtypen (11 Kategorien)

1. Assertions / Contract Checks

- Status: Teilweise.
- Warum: Der Produktivcode wurde bewusst nicht um Runtime-Assertions ergaenzt.
- Alternative: Invarianten werden durch Tests abgesichert (z. B. Normalisierung von API-Payloads, Guard-Clauses bei fehlenden IDs).

2. Unit Tests

- Status: Ja.
- Beispiele: Utilities, Validatoren, Controller-Methoden, Settings/History-Services.

3. Mocks & Stubs (Testbarkeit externer Abhaengigkeiten)

- Status: Ja.
- Verwendet fuer HTTP-Aufrufe, Dateisystem und QSettings-Logik.

4. Equivalence Class Tests

- Status: Ja.
- Beispiele: verschiedene Datumsformate, unterschiedliche API-Record-Varianten, gueltige/ungueltige Pfade.

5. Boundary Value Tests

- Status: Ja.
- Beispiele: leere Strings, fehlende Felder, kleine/grosse Dateigroessen, Min-Speicherplatz.

6. Control-Flow Coverage Tests

- Status: Teilweise, aber mit hohem Ziel.
- Messung: Coverage-Report per `pytest-cov`.
- Restluecken: GUI-Logik und Threading-Pfade lassen sich nicht vollstaendig automatisieren ohne UI-Automation auf Systemebene.

7. Integration Tests

- Status: Teilweise.
- Beispiel: Sync-Logik und File-Download mit lokalen Pfaden.

8. System Tests (End-to-End)

- Status: Teilweise.
- Umgesetzt: Systemtests gegen ein lokales Fake-Backend (HTTP).
- Nicht umgesetzt: Komplettsystem mit echtem Backend und GUI-Automation (zu hoher Infrastrukturaufwand fuer das Projekt).

9. Acceptance Tests

- Status: Teilweise.
- Annahmen: z. B. Einloggen + Dateiliste laden + Chat-Zustand wird zurueckgesetzt.
- Grund: Keine formale Spezifikation vom Backend/Stakeholder.

10. Regression Tests

- Status: Ja.
- Beispiel: Stabiler Umgang mit ungueltigen Datumswerten.

11. Load/Performance Tests

- Status: Teilweise.
- Umgesetzt: `pytest-benchmark` fuer eine zentrale Funktion.
- Nicht umgesetzt: Volllasttests (Locust) wegen fehlender realer Backend-Lastumgebung.

## Teststruktur

- Unit-Tests: [tests/unit](tests/unit)
- GUI-Tests (pytest-qt): [tests/gui](tests/gui)
- Integration: [tests/integration](tests/integration)
- Systemtests mit Fake-Backend: [tests/system](tests/system)
- Acceptance: [tests/acceptance](tests/acceptance)
- Regression: [tests/regression](tests/regression)
- Performance: [tests/performance](tests/performance)
- Fake-Backend: [tests/support/fake_backend.py](tests/support/fake_backend.py)

## Testausfuehrung

```bash
pytest -q
pytest --cov=src --cov-report=term-missing
```

Optional fuer Performance:

```bash
pip install pytest-benchmark
pytest tests/performance -q
```

## Warum einige Tests nur teilweise moeglich sind

- GUI-Apps brauchen oft Systemautomatisierung (Mouse/Keyboard). Das ist im Uni-Setup unnoetig komplex.
- Ein echtes Backend (Auth, Files, Speicherung) ist nicht Teil dieses Repos. Daher nutzen wir ein Fake-Backend.
- Threading und Signals in PyQt koennen in Unit-Tests nur eingeschraenkt simuliert werden.
