"""Cerebro principal - Ejecuta todos los scrapers dinamicamente"""
import sys
import os
import time
from datetime import datetime
from pathlib import Path

ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.utils import (
    ensure_directories, save_json, save_csv, load_config,
    log_message, generate_stats, print_stats
)
from scripts.normalizer import DataNormalizer
from scripts.deduplicator import PromoDeduplicator
from scripts.data_cleaner import DataCleaner
from scripts.cache_manager import CacheManager
from scripts.promo_scorer import PromoScorer
from scripts.fraud_detector import FraudDetector
from scripts.change_detector import ChangeDetector

import scrapers
SCRAPER_CLASSES = [getattr(scrapers, name) for name in scrapers.__all__]
print(f"🚀 {len(SCRAPER_CLASSES)} scrapers a ejecutar: {scrapers.__all__}\n")


class Orchestrator:
    def __init__(self):
        self.config = load_config()
        self.normalizer = DataNormalizer()
        self.deduplicator = PromoDeduplicator()
        self.cleaner = DataCleaner(self.config)
        self.cache = CacheManager(self.config)
        self.scorer = PromoScorer(self.config)
        self.fraud = FraudDetector(self.config)
        self.changes = ChangeDetector()
        self.promos = []
        self.errors = []
        self.t0 = None
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.use_cache = os.getenv('USE_CACHE', 'true').lower() == 'true'

    def run(self):
        self.t0 = time.time()
        print("=" * 70)
        print("🛒 SISTEMA DE SCRAPING DE PROMOCIONES ARGENTINA")
        print("=" * 70)
        print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  Modo: {'Headless' if self.headless else 'Con interfaz'}")
        print("=" * 70 + "\n")
        ensure_directories()

        print("🚀 FASE 1: EXTRACCION DE DATOS")
        print("=" * 70)
        for cls in SCRAPER_CLASSES:
            try:
                scraper = cls(self.headless)
                nombre = scraper.comercio_name
                print(f"\n──────────────────────────────────────────────────────────────────────")
                print(f"🔍 Scrapeando: {nombre}")
                print(f"──────────────────────────────────────────────────────────────────────")
                resultado = scraper.run()
                if resultado:
                    self.promos.extend(resultado)
                else:
                    print(f"   ⚠️ No se encontraron promociones")
                time.sleep(2)
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:200]}")
                self.errors.append(str(e))

        print(f"\n======================================================================")
        print(f"📊 Total extraido: {len(self.promos)} promociones brutas")
        print(f"======================================================================")

        print("\n🔧 FASE 2: NORMALIZACION DE DATOS")
        print("=" * 70)
        norm = []
        for p in self.promos:
            try:
                norm.append(self.normalizer.normalize_promo(p))
            except:
                pass
        self.promos = norm
        print(f"   ✅ {len(self.promos)} promociones normalizadas")

        print("\n🔄 FASE 3: DEDUPLICACION")
        print("=" * 70)
        self.promos = self.deduplicator.deduplicate(self.promos)

        print("\n🧹 FASE 4: LIMPIEZA Y VALIDACION")
        print("=" * 70)
        self.promos = self.cleaner.clean_all(self.promos)

        print("\n🛡️ FASE 5: DETECCION DE FRAUDE")
        print("=" * 70)
        self.promos = self.fraud.filter_promos(self.promos, min_confianza=50)

        print("\n⭐ FASE 6: SCORING")
        print("=" * 70)
        self.promos = self.scorer.score_all(self.promos)

        print("\n🔔 FASE 7: CAMBIOS")
        print("=" * 70)
        ch = self.changes.detect_changes(self.promos)
        save_json(ch, 'data/cambios.json')

        print("\n💾 FASE 8: GUARDANDO DATOS")
        print("=" * 70)
        save_json({
            'ultima_actualizacion': datetime.now().isoformat(),
            'total_promociones': len(self.promos),
            'promociones': self.promos
        }, 'data/promos.json')

        dest = self.scorer.get_destacadas(self.promos)
        save_json({
            'ultima_actualizacion': datetime.now().isoformat(),
            'total_destacadas': len(dest),
            'promociones': dest
        }, 'data/promos_destacadas.json')

        save_csv(self.promos, 'data/promos.csv')
        stats = generate_stats(self.promos)
        save_json(stats, 'data/stats.json')
        save_json({
            'fecha': datetime.now().isoformat(),
            'total_promociones': len(self.promos),
            'total_destacadas': len(dest),
            'estadisticas': stats,
            'errores': self.errors,
            'tiempo_ejecucion': f"{time.time() - self.t0:.2f}s"
        }, 'data/last-update.json')
        print_stats(stats)

        elapsed = time.time() - self.t0
        print(f"\n======================================================================")
        print(f"✅ PROCESO COMPLETADO")
        print(f"======================================================================")
        print(f"⏱️  Tiempo: {elapsed:.2f}s | 📊 Promos: {len(self.promos)} | ❌ Errores: {len(self.errors)}")
        print(f"======================================================================")


def main():
    orch = Orchestrator()
    orch.run()
    sys.exit(0)


if __name__ == "__main__":
    main()
