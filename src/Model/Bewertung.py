from typing import Any


class bewertung:
	def __init__(
		self,
		score: float = 0.0,
		kriterium_liste: list[Any] | None = None,
		schwellwert: float = 0.0,
	):
		self.score = float(score)
		self.kriterium_liste = list(kriterium_liste) if kriterium_liste is not None else []
		self.schwellwert = float(schwellwert)

	def ist_ueber_schwellwert(self) -> bool:
		return self.score > self.schwellwert
