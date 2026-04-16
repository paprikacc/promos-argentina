"""
🕷️ Scrapers Package
Importación segura de scrapers
"""

import importlib
import os

# Lista de scrapers disponibles (nombre_archivo, NombreClase)
SCRAPERS_REGISTRY = [
    ('carrefour_scraper', 'CarrefourScraper'),
    ('jumbo_scraper', 'JumboScraper'),
    ('dia_scraper', 'DiaScraper'),
    ('coto_scraper', 'CotoScraper'),
    ('makro_scraper', 'MakroScraper'),
    ('modo_scraper', 'ModoScraper'),
    ('clash_scraper', 'ClashScraper'),
    ('promociones_scraper', 'PromocionesScraper'),
]

# Importar scrapers dinámicamente
_imported = []
_failed = []

for module_name, class_name in SCRAPERS_REGISTRY:
    try:
        module = importlib.import_module(f'.{module_name}', package='scrapers')
        scraper_class = getattr(module, class_name)
        globals()[class_name] = scraper_class
        _imported.append(class_name)
    except Exception as e:
        _failed.append((module_name, str(e)))

# Exportar todo lo que se pudo importar
__all__ = _imported

# Mostrar estado (solo si estamos debugueando)
if os.getenv('DEBUG_SCRAPERS') == 'true':
    print(f"✅ Scrapers importados: {len(_imported)}")
    for name in _imported:
        print(f"   - {name}")
    if _failed:
        print(f"❌ Scrapers fallidos: {len(_failed)}")
        for name, error in _failed:
            print(f"   - {name}: {error}")
