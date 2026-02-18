# OMAS Moodle Anwendung

OMAS Moodle Anwendung ist eine PyQt6-Desktopanwendung zur Interaktion mit einem Moodle-nahen Backend (Authentifizierung, Dateiverwaltung, Chat- und Verlaufskomponenten).

## Voraussetzungen

Fuer den produktiven Programmbetrieb wird ein separater Backend-API-Server benoetigt.

- Backend-Repository: [Warlockbarky/swe_dhbw_api](https://github.com/Warlockbarky/swe_dhbw_api)
- Wichtig: Backend zuerst starten, danach diese Desktopanwendung ausfuehren.

## Installation und Start (Poetry + venv)

Im Projekt-Root:

```bash
python3 -m venv .venv
source .venv/bin/activate
poetry install
```

Anwendung starten:

```bash
cd src
python3 main.py
```

## Tests und Qualitaet

Das Projekt enthaelt einen breiten Testmix fuer Controller-Logik, Services, GUI-Verhalten und End-to-End-Pfade gegen ein lokales Fake-Backend.

- Aktuelle Coverage: ca. 80%
- Messung: `pytest --cov=src --cov-report=term-missing`

### Testarten (Kurzueberblick)

| Bereich                      | Status    | Kurzbeschreibung                                                                             |
| ---------------------------- | --------- | -------------------------------------------------------------------------------------------- |
| Assertions / Contract Checks | Teilweise | Invarianten werden ueber Tests abgesichert, nicht ueber Runtime-Assertions im Produktivcode. |
| Unit-Tests                   | Ja        | Utilities, Validatoren, Controller-Methoden, Settings/History-Services.                      |
| Mocks & Stubs                | Ja        | Externe Abhaengigkeiten wie HTTP, Dateisystem und QSettings werden isoliert.                 |
| Equivalence Class Tests      | Ja        | Verschiedene API-/Datums-/Pfadvarianten werden systematisch abgedeckt.                       |
| Boundary Value Tests         | Ja        | Leere/falsche Werte und Grenzfaelle bei Dateidaten werden geprueft.                          |
| Control-Flow Coverage        | Teilweise | Hoher Abdeckungsgrad, Restluecken v. a. bei GUI- und Threading-Pfaden.                       |
| Integrationstests            | Teilweise | Zusammenspiel zentraler Flows, z. B. Sync und Download.                                      |
| Systemtests (E2E)            | Teilweise | Gegen lokales Fake-Backend; kein Full-Stack mit realem Backend + UI-Automation.              |
| Akzeptanztests               | Teilweise | Kernannahmen aus Nutzersicht (z. B. Login, Laden, Zustandswechsel).                          |
| Regressionstests             | Ja        | Reproduktion und Absicherung bekannter Fehlerbilder.                                         |
| Load/Performance             | Teilweise | Benchmark einer Kernfunktion via `pytest-benchmark`; keine Volllastumgebung.                 |

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

## Konfiguration fuer den KI-Chat (.env)

Damit der KI-Chat korrekt funktioniert, muss im Projekt-Root eine Datei `.env` vorhanden sein.

Beispiel:

```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o-mini
OPENAI_BASE_URL=https://api.openai.com/v1
```

Hinweis: Die `.env` enthaelt sensible Daten (API-Key) und sollte nicht in Git eingecheckt werden.

Optional fuer Performance:

```bash
pip install pytest-benchmark
pytest tests/performance -q
```

## Hinweise zur Testabdeckung

- GUI-Systemautomation (Maus/Tastatur auf OS-Ebene) ist im Projektumfang bewusst begrenzt.
- Ein echtes Backend ist nicht Teil dieses Repositories; fuer reproduzierbare Tests wird ein Fake-Backend genutzt.
- Threading und Qt-Signals lassen sich in klassischen Unit-Tests nur eingeschraenkt realistisch abbilden.
