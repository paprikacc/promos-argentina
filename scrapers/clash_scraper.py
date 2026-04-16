from .base_scraper import BaseScraper
from datetime import datetime

class ClashScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Clash (Multi-comercio)"
        self.url = "https://promos.clash.com.ar/supermercados/"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="load", timeout=60000)
            page.wait_for_timeout(6000)
            
            for _ in range(5):
                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(1200)
            
            promo_cards = page.query_selector_all('''
                article, .card, .promo, [class*="promo"], [class*="card"],
                [class*="offer"], [class*="benefit"], .item, div[class],
                section, main > div > div
            ''')
            
            print(f"   📦 Encontrados {len(promo_cards)} elementos")
            
            for card in promo_cards:
                try:
                    text = card.inner_text()
                    if not text or len(text) < 20:
                        continue
                    
                    text_lower = text.lower()
                    if not any(k in text_lower for k in ['%', 'descuento', 'banco', 'super', 'carrefour', 'jumbo', 'coto', 'dia']):
                        continue
                    
                    descuento = self.extract_percentage(text)
                    if not descuento:
                        continue
                    
                    comercio = self.extract_comercio_especifico(text)
                    banco = self.extract_banco(text)
                    metodos = self.extract_metodo_pago(text)
                    tope = self.extract_tope(text)
                    dias = self.normalize_dias(text)
                    
                    promo = {
                        'id': self.create_promo_id(comercio, descuento, str(metodos)),
                        'comercio': comercio,
                        'banco': banco,
                        'metodo_pago': metodos,
                        'beneficio': descuento,
                        'descripcion': text[:300],
                        'tope': tope,
                        'dias': dias,
                        'vigencia': 'Consultar vigencia',
                        'url': self.url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'clash'
                    }
                    self.promos.append(promo)
                except:
                    continue
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:150]}")
    
    def extract_comercio_especifico(self, text):
        comercios = {
            'carrefour': 'Carrefour', 'jumbo': 'Jumbo', 'coto': 'Coto',
            'día': 'Día', 'dia': 'Día', 'disco': 'Disco', 'walmart': 'Walmart',
            'vea': 'Vea', 'makro': 'Makro', 'vital': 'Vital'
        }
        text_lower = text.lower()
        for key, value in comercios.items():
            if key in text_lower:
                return value
        return 'Supermercados'
