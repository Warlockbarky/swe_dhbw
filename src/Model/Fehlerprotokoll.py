from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any


class Fehlerprotokoll:
	def __init__(
		self,
		datum: datetime | None = None,
		meldungen: list[Any] | None = None,
	):
		self.datum = datum or datetime.now()
		self.meldungen = list(meldungen) if meldungen is not None else []

	def hinzufuegen(self, meldung: Any) -> None:
		self.meldungen.append(meldung)

	def speichern(self, pfad: str | Path = "fehlerprotokoll.txt") -> Path:
		pfad = Path(pfad)
		pfad.parent.mkdir(parents=True, exist_ok=True)

		with pfad.open("a", encoding="utf-8") as f:
			f.write(f"[{self.datum.isoformat(sep=' ', timespec='seconds')}]\n")
			for meldung in self.meldungen:
				f.write(f"- {meldung}\n")
			f.write("\n")

		return pfad
