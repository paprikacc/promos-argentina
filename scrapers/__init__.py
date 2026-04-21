"""
🕷️ Scrapers Package
Importación segura de scrapers con reporte de errores
"""

import importlib
import sys

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

_imported = []
_failed = []

for module_name, class_name in SCRAPERS_REGISTRY:
    try:
        module = importlib.import_module(f'.{module_name}', package='scrapers')
        scraper_class = getattr(module, class_name)
        globals()[class_name] = scraper_class
        _imported.append(class_name)
    except Exception as e:
        error_msg = str(e)
        _failed.append((module_name, class_name, error_msg))
        # IMPRIMIR EL ERROR PARA VERLO EN LOS LOGS
        print(f"❌ Error importando {class_name} ({module_name}): {error_msg}")

__all__ = _imported

# Siempre mostrar resumen
print(f"\n📋 RESUMEN DE SCRAPERS:")
print(f"   ✅ Importados: {len(_imported)}/{len(SCRAPERS_REGISTRY)}")
for name in _imported:
    print(f"      ✅ {name}")

if _failed:
    print(f"   ❌ Fallidos: {len(_failed)}/{len(SCRAPERS_REGISTRY)}")
    for module_name, class_name, error in _failed:
        print(f"      ❌ {class_name} ({module_name}): {error[:200]}")
print()
