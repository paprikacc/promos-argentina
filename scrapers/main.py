# Importar scrapers
from scrapers import (
    CarrefourScraper,
    JumboScraper,
    DiaScraper,
    CotoScraper,
    MakroScraper,
    ModoScraper,
    ClashScraper,           # ⭐ NUEVO
    PromocionesScraper      # ⭐ NUEVO
)

# ...

def get_scrapers(self):
    """Retorna lista de scrapers a ejecutar"""
    return [
        CarrefourScraper(self.headless),
        JumboScraper(self.headless),
        DiaScraper(self.headless),
        CotoScraper(self.headless),
        MakroScraper(self.headless),
        ModoScraper(self.headless),
        ClashScraper(self.headless),          # ⭐ NUEVO
        PromocionesScraper(self.headless)     # ⭐ NUEVO
    ]
