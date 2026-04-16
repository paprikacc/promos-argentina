"""
🕷️ Promociones.com.ar Scraper
Extrae promociones de https://www.promociones.com.ar/category/supermercados/
"""

from .base_scraper import BaseScraper
from datetime import datetime

class PromocionesScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Promociones.com.ar (Multi-comercio)"
        self.url = "https://www.promociones.com.ar/category/supermercados/"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="domcontentloaded", timeout=40000)
            
            # Esperar las promociones
            page.wait_for_selector('article, .promo, .card, .post', timeout=15000)
            
            # Scroll
            for _ in range(4):
                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(1500)
            
            promos = page.query_selector_all('''
                article,
                .promo,
                .post,
                .card,
                [class*="post"],
                [class*="promo"]
            ''')
            
            print(f"   📦 Encontrados {len(promos)} elementos")
            
            for promo in promos:
                try:
                    text = promo.inner_text()
                    
                    # Filtrar
                    if not any(word in text.lower() for word in ['supermercado', 'banco', '%', 'descuento', 'visa', 'mastercard']):
                        continue
                    
                    titulo = promo.query_selector('h1, h2, h3, .title, .entry-title')
                    titulo_text = titulo.inner_text() if titulo else text.split('\n')[0]
                    
                    # Extraer comercio
                    comercio = self.extract_comercio_from_text(text)
                    
                    banco = self.extract_banco(text)
                    metodos = self.extract_metodo_pago(text)
                    descuento = self.extract_percentage(text)
                    beneficio = descuento if descuento else titulo_text[:100]
                    tope = self.extract_tope(text)
                    dias = self.normalize_dias(text)
                    
                    # Obtener enlace
                    link = promo.query_selector('a[href]')
                    promo_url = link.get_attribute('href') if link else self.url
                    
                    promo_obj = {
                        'id': self.create_promo_id(comercio, beneficio, str(metodos)),
                        'comercio': comercio,
                        'banco': banco,
                        'metodo_pago': metodos,
                        'beneficio': beneficio,
                        'descripcion': text[:300],
                        'tope': tope,
                        'dias': dias,
                        'vigencia': 'Consultar vigencia',
                        'url': promo_url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'promociones.com.ar'
                    }
                    
                    self.promos.append(promo_obj)
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    def extract_comercio_from_text(self, text):
        """Extrae el comercio del texto"""
        comercios = {
            'carrefour': 'Carrefour',
            'jumbo': 'Jumbo',
            'coto': 'Coto',
            'día': 'Día',
            'dia': 'Día',
            'disco': 'Disco',
            'walmart': 'Walmart',
            'vea': 'Vea',
            'makro': 'Makro',
            'vital': 'Vital'
        }
        
        text_lower = text.lower()
        for key, value in comercios.items():
            if key in text_lower:
                return value
        
        return 'Supermercados'
