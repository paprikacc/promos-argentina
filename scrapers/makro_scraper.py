from .base_scraper import BaseScraper
from datetime import datetime

class MakroScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Makro"
        self.url = "https://makro.com.ar/beneficios-bancarios/"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="networkidle")
            page.wait_for_selector('.beneficio, .promo, article', timeout=10000)
            
            promos = page.query_selector_all('.beneficio, .promo-item, article, .card')
            
            for promo_elem in promos:
                try:
                    text = promo_elem.inner_text()
                    
                    titulo = promo_elem.query_selector('h3, h4, .titulo')
                    titulo_text = titulo.inner_text() if titulo else text.split('\n')[0]
                    
                    banco = self.extract_banco(text)
                    metodos = self.extract_metodo_pago(text)
                    descuento = self.extract_percentage(text)
                    beneficio = descuento if descuento else titulo_text[:100]
                    tope = self.extract_tope(text)
                    dias = self.normalize_dias(text)
                    
                    promo = {
                        'id': self.create_promo_id(self.comercio_name, beneficio, str(metodos)),
                        'comercio': self.comercio_name,
                        'banco': banco,
                        'metodo_pago': metodos,
                        'beneficio': beneficio,
                        'descripcion': text[:200],
                        'tope': tope,
                        'dias': dias,
                        'vigencia': 'Consultar condiciones',
                        'url': self.url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'makro_oficial'
                    }
                    
                    self.promos.append(promo)
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
