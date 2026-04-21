"""
🧠 CEREBRO PRINCIPAL
Versión dinámica: ejecuta todos los scrapers importados automáticamente
"""

import sys
import os
import time
from datetime import datetime
from pathlib import Path

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

# Importar scrapers dinámicamente
try:
    import scrapers
    SCRAPER_CLASSES = [getattr(scrapers, name) for name in scrapers.__all__]
    print(f"✅ {len(SCRAPER_CLASSES)} scrapers listos para ejecutar: {scrapers.__all__}\n")
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
        self.max_retries = self.config.get('scraping', {}).get('retry_attempts', 3)
    
    def initialize(self):
        """Inicializa el sistema"""
        print("=" * 70)
        print("🛒 SISTEMA DE SCRAPING DE PROMOCIONES ARGENTINA")
        print("=" * 70)
        print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  Modo: {'Headless' if self.headless else 'Con interfaz'}")
        print(f"💾 Cache: {'Habilitado' if self.use_cache else 'Deshabilitado'}")
        print("=" * 70 + "\n")
        
        ensure_directories()
        log_message("Iniciando proceso de scraping")
        self.start_time = time.time()
    
    def run_scraper_with_retry(self, scraper_class):
        """Ejecuta un scraper individual con reintentos"""
        scraper_name = scraper_class.__name__
        
        try:
            scraper = scraper_class(self.headless)
            comercio = scraper.comercio_name
        except Exception as e:
            print(f"   ❌ Error instanciando {scraper_name}: {e}")
            self.errors.append(f"Error en {scraper_name}: {e}")
            return []
        
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"\n──────────────────────────────────────────────────────────────────────")
                print(f"🔍 Scrapeando: {comercio} (Intento {attempt}/{self.max_retries})")
                print(f"──────────────────────────────────────────────────────────────────────")
                
                # Intentar obtener del cache primero (solo en primer intento)
                if attempt == 1 and self.use_cache:
                    cached_data = self.cache_manager.get(comercio)
                    if cached_data:
                        print(f"   💾 Datos obtenidos del cache")
                        return cached_data
                
                # Ejecutar scraper
                promos = scraper.run()
                
                if promos:
                    if self.use_cache:
                        self.cache_manager.set(comercio, promos)
                    log_message(f"✅ {comercio}: {len(promos)} promociones")
                    return promos
                else:
                    print(f"   ⚠️ No se encontraron promociones")
                    if attempt < self.max_retries:
                        print(f"   ⏳ Reintentando en 3 segundos...")
                        time.sleep(3)
                        
            except Exception as e:
                error_msg = f"Error en {comercio}: {str(e)[:200]}"
                print(f"   ❌ {error_msg}")
                log_message(f"❌ {error_msg}")
                self.errors.append(error_msg)
                if attempt < self.max_retries:
                    print(f"   ⏳ Reintentando en 5 segundos...")
                    time.sleep(5)
        
        log_message(f"❌ {comercio}: Falló después de {self.max_retries} intentos")
        return []
    
    def run_all_scrapers(self):
        """Ejecuta TODOS los scrapers importados automáticamente"""
        print("\n🚀 FASE 1: EXTRACCIÓN DE DATOS")
        print("=" * 70)
        
        if not SCRAPER_CLASSES:
            print("⚠️ No hay scrapers disponibles!")
            log_message("ERROR: No hay scrapers disponibles")
            return
        
        for scraper_class in SCRAPER_CLASSES:
            try:
                promos = self.run_scraper_with_retry(scraper_class)
                self.all_promos.extend(promos)
                delay = self.config.get('scraping', {}).get('delay_between_scrapers', 2000) / 1000
                print(f"\n⏳ Esperando {delay}s antes del siguiente scraper...")
                time.sleep(delay)
            except Exception as e:
                print(f"   ❌ Error crítico: {e}")
                self.errors.append(str(e))
        
        print(f"\n======================================================================")
        print(f"📊 Total extraído: {len(self.all_promos)} promociones brutas")
        print(f"======================================================================")
        log_message(f"Total extraído: {len(self.all_promos)}")
    
    def normalize_data(self):
        """Normaliza todos los datos"""
        print("\n🔧 FASE 2: NORMALIZACIÓN DE DATOS")
        print("=" * 70)
        normalized = []
        for promo in self.all_promos:
            try:
                normalized.append(self.normalizer.normalize_promo(promo))
            except Exception as e:
                pass
        self.all_promos = normalized
        print(f"   ✅ {len(self.all_promos)} promociones normalizadas")
    
    def deduplicate_data(self):
        """Elimina duplicados"""
        print("\n🔄 FASE 3: DEDUPLICACIÓN")
        print("=" * 70)
        self.all_promos = self.deduplicator.deduplicate(self.all_promos)
    
    def clean_data(self):
        """Limpia datos"""
        print("\n🧹 FASE 4: LIMPIEZA Y VALIDACIÓN")
        print("=" * 70)
        self.all_promos = self.cleaner.clean_all(self.all_promos)
    
    def detect_fraud(self):
        """Detecta fraude"""
        print("\n🛡️ FASE 5: DETECCIÓN DE FRAUDE")
        print("=" * 70)
        self.all_promos = self.fraud_detector.filter_promos(self.all_promos, min_confianza=50)
    
    def score_promos(self):
        """Asigna scores"""
        print("\n⭐ FASE 6: SCORING")
        print("=" * 70)
        self.all_promos = self.scorer.score_all(self.all_promos)
    
    def detect_changes(self):
        """Detecta cambios"""
        print("\n🔔 FASE 7: CAMBIOS")
        print("=" * 70)
        changes = self.change_detector.detect_changes(self.all_promos)
        save_json(changes, 'data/cambios.json')
        return changes
    
    def save_data(self, changes):
        """Guarda datos"""
        print("\n💾 FASE 5: GUARDANDO DATOS")
        print("=" * 70)
        
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
        print(f"\n======================================================================")
        print(f"✅ PROCESO COMPLETADO")
        print(f"======================================================================")
        print(f"⏱️  Tiempo total: {elapsed:.2f} segundos")
        print(f"📊 Promociones finales: {len(self.all_promos)}")
        print(f"❌ Errores: {len(self.errors)}")
        print(f"\n🎉 Sistema listo para usar!")
        print(f"📁 Archivos generados en: ./data/")
        print(f"======================================================================")
    
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
