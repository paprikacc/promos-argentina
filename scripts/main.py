"""
🧠 CEREBRO PRINCIPAL DEL PROYECTO
Coordina todos los scrapers, limpia datos y genera archivos finales
"""

import sys
import os
from datetime import datetime
from pathlib import Path
import time

# Agregar directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Importar módulos propios
from scripts.normalizer import DataNormalizer
from scripts.deduplicator import PromoDeduplicator
from scripts.data_cleaner import DataCleaner
from scripts.utils import (
    ensure_directories,
    save_json,
    save_csv,
    load_config,
    log_message,
    generate_stats,
    print_stats
)

# Importar scrapers
from scrapers import (
    CarrefourScraper,
    JumboScraper,
    DiaScraper,
    CotoScraper,
    MakroScraper,
    ModoScraper
)

class PromoScraperOrchestrator:
    """Orquestador principal del sistema de scraping"""
    
    def __init__(self):
        self.config = load_config()
        self.normalizer = DataNormalizer()
        self.deduplicator = PromoDeduplicator()
        self.cleaner = DataCleaner(self.config)
        self.all_promos = []
        self.errors = []
        self.start_time = None
        self.headless = os.getenv('HEADLESS', 'true').lower() == 'true'
    
    def initialize(self):
        """Inicializa el sistema"""
        print("=" * 70)
        print("🛒 SISTEMA DE SCRAPING DE PROMOCIONES ARGENTINA")
        print("=" * 70)
        print(f"⏰ Inicio: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🖥️  Modo: {'Headless' if self.headless else 'Con interfaz'}")
        print("=" * 70 + "\n")
        
        ensure_directories()
        log_message("="*50)
        log_message("Iniciando proceso de scraping")
        self.start_time = time.time()
    
    def get_scrapers(self):
        """Retorna lista de scrapers a ejecutar"""
        return [
            CarrefourScraper(self.headless),
            JumboScraper(self.headless),
            DiaScraper(self.headless),
            CotoScraper(self.headless),
            MakroScraper(self.headless),
            ModoScraper(self.headless)
        ]
    
    def run_scraper(self, scraper):
        """Ejecuta un scraper individual con manejo de errores"""
        comercio = scraper.comercio_name
        retry_attempts = self.config.get('scraping', {}).get('retry_attempts', 3)
        
        for attempt in range(retry_attempts):
            try:
                print(f"\n{'─' * 70}")
                print(f"🔍 Scrapeando: {comercio} (Intento {attempt + 1}/{retry_attempts})")
                print(f"{'─' * 70}")
                
                promos = scraper.run()
                
                if promos:
                    log_message(f"✅ {comercio}: {len(promos)} promociones extraídas")
                    return promos
                else:
                    print(f"   ⚠️ No se encontraron promociones")
                    log_message(f"⚠️ {comercio}: Sin promociones")
                    return []
                
            except Exception as e:
                error_msg = f"Error en {comercio} (intento {attempt + 1}): {str(e)}"
                print(f"   ❌ {error_msg}")
                log_message(f"❌ {error_msg}")
                
                if attempt < retry_attempts - 1:
                    wait_time = 5 * (attempt + 1)
                    print(f"   ⏳ Esperando {wait_time}s antes de reintentar...")
                    time.sleep(wait_time)
                else:
                    self.errors.append(error_msg)
                    return []
        
        return []
    
    def run_all_scrapers(self):
        """Ejecuta todos los scrapers"""
        print("\n🚀 FASE 1: EXTRACCIÓN DE DATOS")
        print("=" * 70)
        
        scrapers = self.get_scrapers()
        delay = self.config.get('scraping', {}).get('delay_between_scrapers', 2000) / 1000
        
        for i, scraper in enumerate(scrapers):
            promos = self.run_scraper(scraper)
            self.all_promos.extend(promos)
            
            # Delay entre scrapers (excepto el último)
            if i < len(scrapers) - 1:
                print(f"\n⏳ Esperando {delay}s antes del siguiente scraper...")
                time.sleep(delay)
        
        print(f"\n{'=' * 70}")
        print(f"📊 Total extraído: {len(self.all_promos)} promociones brutas")
        print(f"{'=' * 70}")
        log_message(f"Total extraído: {len(self.all_promos)} promociones")
    
    def normalize_data(self):
        """Normaliza todos los datos"""
        print("\n🔧 FASE 2: NORMALIZACIÓN DE DATOS")
        print("=" * 70)
        
        normalized_promos = []
        
        for promo in self.all_promos:
            try:
                normalized = self.normalizer.normalize_promo(promo)
                normalized_promos.append(normalized)
            except Exception as e:
                print(f"   ⚠️ Error normalizando promo: {e}")
                log_message(f"Error normalizando promo: {e}")
        
        self.all_promos = normalized_promos
        print(f"   ✅ {len(self.all_promos)} promociones normalizadas")
        log_message(f"Normalizadas: {len(self.all_promos)}")
    
    def deduplicate_data(self):
        """Elimina duplicados"""
        print("\n🔄 FASE 3: DEDUPLICACIÓN")
        print("=" * 70)
        
        self.all_promos = self.deduplicator.deduplicate(self.all_promos)
        log_message(f"Después de deduplicar: {len(self.all_promos)}")
    
    def clean_data(self):
        """Limpia y valida datos"""
        print("\n🧹 FASE 4: LIMPIEZA Y VALIDACIÓN")
        print("=" * 70)
        
        self.all_promos = self.cleaner.clean_all(self.all_promos)
        log_message(f"Después de limpiar: {len(self.all_promos)}")
    
    def save_data(self):
        """Guarda los datos en archivos"""
        print("\n💾 FASE 5: GUARDANDO DATOS")
        print("=" * 70)
        
        # Preparar datos para JSON principal
        output_data = {
            'ultima_actualizacion': datetime.now().isoformat(),
            'total_promociones': len(self.all_promos),
            'promociones': self.all_promos
        }
        
        # Guardar JSON principal
        save_json(output_data, 'data/promos.json')
        
        # Guardar CSV
        save_csv(self.all_promos, 'data/promos.csv')
        
        # Generar y guardar estadísticas
        stats = generate_stats(self.all_promos)
        
        # Guardar metadata
        metadata = {
            'fecha': datetime.now().isoformat(),
            'total_promociones': len(self.all_promos),
            'estadisticas': stats,
            'errores': self.errors,
            'tiempo_ejecucion': f"{time.time() - self.start_time:.2f}s",
            'fuentes': [
                'Carrefour',
                'Jumbo',
                'Día',
                'Coto',
                'Makro',
                'MODO'
            ]
        }
        save_json(metadata, 'data/last-update.json')
        
        # Guardar estadísticas detalladas
        save_json(stats, 'data/stats.json')
        
        print("\n")
        print_stats(stats)
        
        log_message(f"Datos guardados exitosamente: {len(self.all_promos)} promociones")
    
    def finalize(self):
        """Finaliza el proceso"""
        elapsed_time = time.time() - self.start_time
        
        print("\n" + "=" * 70)
        print("✅ PROCESO COMPLETADO")
        print("=" * 70)
        print(f"⏱️  Tiempo total: {elapsed_time:.2f} segundos")
        print(f"📊 Promociones finales: {len(self.all_promos)}")
        print(f"❌ Errores: {len(self.errors)}")
        
        if self.errors:
            print("\n⚠️  Errores encontrados:")
            for error in self.errors:
                print(f"   • {error}")
        
        print("\n🎉 Sistema listo para usar!")
        print(f"📁 Archivos generados en: ./data/")
        print("=" * 70)
        
        log_message(f"Proceso completado en {elapsed_time:.2f}s")
        log_message(f"Total final: {len(self.all_promos)} promociones")
        log_message("="*50)
    
    def run(self):
        """Ejecuta el proceso completo"""
        try:
            self.initialize()
            self.run_all_scrapers()
            self.normalize_data()
            self.deduplicate_data()
            self.clean_data()
            self.save_data()
            self.finalize()
            return True
        except KeyboardInterrupt:
            print("\n\n⚠️ Proceso interrumpido por el usuario")
            log_message("Proceso interrumpido por el usuario")
            return False
        except Exception as e:
            print(f"\n\n❌ Error crítico: {e}")
            log_message(f"Error crítico: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """Punto de entrada principal"""
    orchestrator = PromoScraperOrchestrator()
    success = orchestrator.run()
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
