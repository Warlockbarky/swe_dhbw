class konfiguration:
    def __init__(self):
        self.pfad = ""
        self.dateiname=""
    #Braucht es speichere und lade gerade überhaupt?
    def speichere(self):
        print("speichere")
    def lade(self):
        print("lade")
    def set_pfad(self, pfad: str):
        self.pfad = pfad
    def set_dateiname(self, dateiname: str):
        self.dateiname = dateiname
    def get_pfad(self):
        return self.pfad
    def get_dateiname(self):
        return self.dateiname
