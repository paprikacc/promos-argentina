"""
💾 Sistema de Cache Inteligente
Evita re-scrapear datos recientes y mejora performance
"""

import json
import hashlib
from datetime import datetime, timedelta
from pathlib import Path

class CacheManager:
    def __init__(self, config, cache_file='data/cache/cache.json'):
        self.config = config.get('cache', {})
        self.cache_file = cache_file
        self.enabled = self.config.get('enabled', True)
        self.ttl_hours = self.config.get('ttl_hours', 6)
        self.cache = self._load_cache()
    
    def _load_cache(self):
        """Carga el cache desde archivo"""
        if not self.enabled:
            return {}
        
        try:
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)
            if Path(self.cache_file).exists():
                with open(self.cache_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ Error cargando cache: {e}")
        
        return {}
    
    def _save_cache(self):
        """Guarda el cache en archivo"""
        if not self.enabled:
            return
        
        try:
            Path(self.cache_file).parent.mkdir(parents=True, exist_ok=True)
            with open(self.cache_file, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error guardando cache: {e}")
    
    def _create_key(self, scraper_name):
        """Crea una clave única para el scraper"""
        return hashlib.md5(scraper_name.encode()).hexdigest()
    
    def _is_valid(self, cache_entry):
        """Verifica si una entrada de cache es válida"""
        try:
            cached_time = datetime.fromisoformat(cache_entry['timestamp'])
            age = datetime.now() - cached_time
            max_age = timedelta(hours=self.ttl_hours)
            return age < max_age
        except:
            return False
    
    def get(self, scraper_name):
        """Obtiene datos del cache si están frescos"""
        if not self.enabled:
            return None
        
        key = self._create_key(scraper_name)
        
        if key in self.cache:
            entry = self.cache[key]
            if self._is_valid(entry):
                age_minutes = (datetime.now() - datetime.fromisoformat(entry['timestamp'])).seconds // 60
                print(f"   ✅ Cache HIT para {scraper_name} ({age_minutes} min)")
                return entry['data']
            else:
                print(f"   ⏰ Cache expirado para {scraper_name}")
                del self.cache[key]
        
        print(f"   ❌ Cache MISS para {scraper_name}")
        return None
    
    def set(self, scraper_name, data):
        """Guarda datos en cache"""
        if not self.enabled:
            return
        
        key = self._create_key(scraper_name)
        self.cache[key] = {
            'timestamp': datetime.now().isoformat(),
            'scraper': scraper_name,
            'count': len(data),
            'data': data
        }
        self._save_cache()
    
    def clear(self, scraper_name=None):
        """Limpia el cache (todo o de un scraper específico)"""
        if scraper_name:
            key = self._create_key(scraper_name)
            if key in self.cache:
                del self.cache[key]
                self._save_cache()
                print(f"   🗑️ Cache limpiado para {scraper_name}")
        else:
            self.cache = {}
            self._save_cache()
            print("   🗑️ Todo el cache limpiado")
    
    def get_stats(self):
        """Obtiene estadísticas del cache"""
        total = len(self.cache)
        valid = sum(1 for entry in self.cache.values() if self._is_valid(entry))
        expired = total - valid
        
        return {
            'total_entries': total,
            'valid_entries': valid,
            'expired_entries': expired,
            'ttl_hours': self.ttl_hours
        }
