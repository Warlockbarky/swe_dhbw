from typing import Any


class Bewertung:
	def __init__(
		self,
		score: float = 0.0,
		kriteriumListe: list[Any] | None = None,
		schwellwert: float = 0.0,
	):
		self.score = float(score)
		self.kriteriumListe = list(kriteriumListe) if kriteriumListe is not None else []
		self.schwellwert = float(schwellwert)

	def istUeberSchwellwert(self) -> bool:
		return self.score > self.schwellwert
