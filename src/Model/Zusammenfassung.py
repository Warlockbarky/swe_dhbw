class zusammenfassung:
	def __init__(self, id: int = 0, inhalt: str = "", laenge: int | None = None):
		self.id = int(id)
		self.inhalt = str(inhalt)
		self.laenge = int(laenge) if laenge is not None else len(self.inhalt)

	def anzeigen(self) -> None:
		print(self.inhalt)
