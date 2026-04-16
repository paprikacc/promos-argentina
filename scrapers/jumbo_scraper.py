from .base_scraper import BaseScraper
from datetime import datetime

class JumboScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Jumbo"
        self.url = "https://www.jumbo.com.ar/descuentos-del-dia"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="load", timeout=60000)
            page.wait_for_timeout(8000)
            
            for _ in range(6):
                page.evaluate("window.scrollBy(0, 800)")
                page.wait_for_timeout(1500)
            
            promo_cards = page.query_selector_all('''
                article, .card, .promo, [class*="promo"], [class*="discount"],
                [class*="benefit"], [class*="offer"], .item, .product,
                [class*="card"], [class*="grid"] > div
            ''')
            
            print(f"   📦 Encontrados {len(promo_cards)} elementos")
            
            for card in promo_cards:
                try:
                    text = card.inner_text()
                    if not text or len(text) < 15:
                        continue
                    if not any(k in text.lower() for k in ['%', 'descuento', 'banco', 'visa', 'mastercard']):
                        continue
                    
                    descuento = self.extract_percentage(text)
                    if not descuento:
                        continue
                    
                    banco = self.extract_banco(text)
                    metodos = self.extract_metodo_pago(text)
                    tope = self.extract_tope(text)
                    dias = self.normalize_dias(text)
                    
                    promo = {
                        'id': self.create_promo_id(self.comercio_name, descuento, str(metodos)),
                        'comercio': self.comercio_name,
                        'banco': banco,
                        'metodo_pago': metodos,
                        'beneficio': descuento,
                        'descripcion': text[:300],
                        'tope': tope,
                        'dias': dias,
                        'vigencia': 'Ver condiciones',
                        'url': self.url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'jumbo_oficial'
                    }
                    self.promos.append(promo)
                except:
                    continue
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:150]}")
