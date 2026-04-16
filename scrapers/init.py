"""
🕷️ Scrapers Package
Exporta todos los scrapers disponibles
"""

from .carrefour_scraper import CarrefourScraper
from .jumbo_scraper import JumboScraper
from .dia_scraper import DiaScraper
from .coto_scraper import CotoScraper
from .makro_scraper import MakroScraper
from .modo_scraper import ModoScraper
from .clash_scraper import ClashScraper
from .promociones_scraper import PromocionesScraper

__all__ = [
    'CarrefourScraper',
    'JumboScraper',
    'DiaScraper',
    'CotoScraper',
    'MakroScraper',
    'ModoScraper',
    'ClashScraper',
    'PromocionesScraper'
]
