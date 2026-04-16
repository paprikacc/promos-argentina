"""
🧠 CEREBRO PRINCIPAL
Versión robusta con manejo de errores
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import time

# Agregar directorio raíz al path
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

# Importar utilidades
from scripts.utils import (
    ensure_directories,
    save_json,
    save_csv,
    load_config,
    log_message,
    generate_stats,
    print_stats
)

# Importar módulos de procesamiento
from scripts.normalizer import DataNormalizer
from scripts.deduplicator import PromoDeduplicator
from scripts.data_cleaner import DataCleaner
from scripts.cache_manager import CacheManager
from scripts.promo_scorer import PromoScorer
from scripts.fraud_detector import FraudDetector
from scripts.change_detector import ChangeDetector

# Importar scrapers disponibles
try:
    import scrapers
    SCRAPER_CLASSES = []
    
    for name in scrapers.__all__:
        cls = getattr(scrapers, name)
        SCRAPER_CLASSES.append(cls)
    
    print(f"✅ {len(SCRAPER_CLASSES)} scrapers importados: {scrapers.__all__}")
    
except Exception as e:
    print(f"❌ Error importando scrapers: {e}")
    SCRAPER_CLASSES = []


class PromoScraperOrchestrator:
    """Orquestador del sistema de scraping"""
    
    def __init__(self):
        self.config = load_config()
        self.normalizer = DataNormalizer()
        self.deduplicator = PromoDeduplicator()
        self.cleaner = DataCleaner(self.config)
        self.cache_manager = CacheManager(self.config)
        self.scorer = PromoScorer(self.config)
        self.fraud_detector = FraudDetector(self.config)
        self.change_detector = ChangeDetector()
        self.all_promos = []
        self.errors = []
        self.start_time = None
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
        self.use_cache = os.getenv('USE_CACHE', 'true').lower() == 'true'
    
    def initialize(self):
        """Inicializa el sistema"""
        print("=" * 70)
        print("🛒 SISTEMA DE SCRAPING DE PROMOCIONES")
        print("=" * 70)
        print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  Modo: {'Headless' if self.headless else 'Con interfaz'}")
        print(f"💾 Cache: {'Habilitado' if self.use_cache else 'Deshabilitado'}")
        print("=" * 70 + "\n")
        
        ensure_directories()
        log_message("Iniciando proceso de scraping")
        self.start_time = time.time()
    
    def run_scraper(self, scraper_class):
        """Ejecuta un scraper individual"""
        try:
            scraper = scraper_class(self.headless)
            comercio = scraper.comercio_name
        except Exception as e:
            print(f"   ❌ Error instanciando {scraper_class.__name__}: {e}")
            self.errors.append(f"Error en {scraper_class.__name__}: {e}")
            return []
        
        # Intentar obtener del cache
        if self.use_cache:
            cached_data = self.cache_manager.get(comercio)
            if cached_data:
                return cached_data
        
        # Scrapear
        try:
            print(f"\n🔍 Scrapeando: {comercio}")
            promos = scraper.run()
            
            if promos:
                if self.use_cache:
                    self.cache_manager.set(comercio, promos)
                log_message(f"✅ {comercio}: {len(promos)} promociones")
                return promos
            else:
                print(f"   ⚠️ Sin promociones")
                log_message(f"⚠️ {comercio}: Sin promociones")
                return []
                
        except Exception as e:
            error_msg = f"Error en {comercio}: {str(e)}"
            print(f"   ❌ {error_msg}")
            log_message(f"❌ {error_msg}")
            self.errors.append(error_msg)
            return []
    
    def run_all_scrapers(self):
        """Ejecuta todos los scrapers disponibles"""
        print("\n🚀 FASE 1: EXTRACCIÓN DE DATOS")
        print("=" * 70)
        
        if not SCRAPER_CLASSES:
            print("⚠️ No hay scrapers disponibles!")
            log_message("ERROR: No hay scrapers disponibles")
            return
        
        for scraper_class in SCRAPER_CLASSES:
            try:
                promos = self.run_scraper(scraper_class)
                self.all_promos.extend(promos)
                time.sleep(2)  # Delay entre scrapers
            except Exception as e:
                print(f"   ❌ Error crítico: {e}")
                self.errors.append(str(e))
        
        print(f"\n📊 Total extraído: {len(self.all_promos)} promociones")
        log_message(f"Total extraído: {len(self.all_promos)}")
    
    def normalize_data(self):
        """Normaliza todos los datos"""
        print("\n🔧 FASE 2: NORMALIZACIÓN")
        normalized = []
        for promo in self.all_promos:
            try:
                normalized.append(self.normalizer.normalize_promo(promo))
            except Exception as e:
                print(f"   ⚠️ Error normalizando: {e}")
        self.all_promos = normalized
        print(f"   ✅ {len(self.all_promos)} normalizadas")
    
    def deduplicate_data(self):
        """Elimina duplicados"""
        print("\n🔄 FASE 3: DEDUPLICACIÓN")
        self.all_promos = self.deduplicator.deduplicate(self.all_promos)
    
    def clean_data(self):
        """Limpia datos"""
        print("\n🧹 FASE 4: LIMPIEZA")
        self.all_promos = self.cleaner.clean_all(self.all_promos)
    
    def detect_fraud(self):
        """Detecta fraude"""
        print("\n🛡️ FASE 5: DETECCIÓN DE FRAUDE")
        self.all_promos = self.fraud_detector.filter_promos(self.all_promos, min_confianza=50)
    
    def score_promos(self):
        """Asigna scores"""
        print("\n⭐ FASE 6: SCORING")
        self.all_promos = self.scorer.score_all(self.all_promos)
        destacadas = [p for p in self.all_promos if p.get('destacada', False)]
        print(f"   ⭐ {len(destacadas)} destacadas")
    
    def detect_changes(self):
        """Detecta cambios"""
        print("\n🔔 FASE 7: CAMBIOS")
        changes = self.change_detector.detect_changes(self.all_promos)
        save_json(changes, 'data/cambios.json')
        return changes
    
    def save_data(self, changes):
        """Guarda datos"""
        print("\n💾 FASE 8: GUARDANDO")
        
        output_data = {
            'ultima_actualizacion': datetime.now().isoformat(),
            'total_promociones': len(self.all_promos),
            'promociones': self.all_promos
        }
        save_json(output_data, 'data/promos.json')
        
        destacadas = self.scorer.get_destacadas(self.all_promos)
        save_json({
            'ultima_actualizacion': datetime.now().isoformat(),
            'total_destacadas': len(destacadas),
            'promociones': destacadas
        }, 'data/promos_destacadas.json')
        
        save_csv(self.all_promos, 'data/promos.csv')
        
        stats = generate_stats(self.all_promos)
        save_json(stats, 'data/stats.json')
        
        metadata = {
            'fecha': datetime.now().isoformat(),
            'total_promociones': len(self.all_promos),
            'total_destacadas': len(destacadas),
            'estadisticas': stats,
            'errores': self.errors,
            'tiempo_ejecucion': f"{time.time() - self.start_time:.2f}s"
        }
        save_json(metadata, 'data/last-update.json')
        
        print_stats(stats)
    
    def finalize(self):
        """Finaliza el proceso"""
        elapsed = time.time() - self.start_time
        print(f"\n✅ COMPLETADO en {elapsed:.2f}s")
        print(f"📊 {len(self.all_promos)} promociones")
        if self.errors:
            print(f"⚠️ {len(self.errors)} errores")
    
    def run(self):
        """Ejecuta todo el proceso"""
        try:
            self.initialize()
            self.run_all_scrapers()
            self.normalize_data()
            self.deduplicate_data()
            self.clean_data()
            self.detect_fraud()
            self.score_promos()
            changes = self.detect_changes()
            self.save_data(changes)
            self.finalize()
            return True
        except Exception as e:
            print(f"\n❌ Error crítico: {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    orchestrator = PromoScraperOrchestrator()
    success = orchestrator.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
