from .base_scraper import BaseScraper
from datetime import datetime

class ModoScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "MODO (Multi-comercio)"
        self.url = "https://www.modo.com.ar/promos"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="networkidle")
            page.wait_for_timeout(3000)
            
            # Scroll para cargar más
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(1000)
            
            promos = page.query_selector_all('.promo-card, article, [class*="promo"]')
            
            for promo_elem in promos:
                try:
                    text = promo_elem.inner_text()
                    
                    # Filtrar solo supermercados
                    if not any(word in text.lower() for word in ['supermercado', 'coto', 'carrefour', 'jumbo', 'día', 'disco']):
                        continue
                    
                    titulo = promo_elem.query_selector('h3, h4, .titulo')
                    titulo_text = titulo.inner_text() if titulo else text.split('\n')[0]
                    
                    # Extraer comercio específico
                    comercio = self.comercio_name
                    for super_name in ['Coto', 'Carrefour', 'Jumbo', 'Día', 'Disco', 'Walmart']:
                        if super_name.lower() in text.lower():
                            comercio = super_name
                            break
                    
                    banco = 'Banco Galicia'  # MODO es de Galicia
                    metodos = ['MODO']
                    descuento = self.extract_percentage(text)
                    beneficio = descuento if descuento else titulo_text[:100]
                    tope = self.extract_tope(text)
                    dias = self.normalize_dias(text)
                    
                    promo = {
                        'id': self.create_promo_id(comercio, beneficio, 'MODO'),
                        'comercio': comercio,
                        'banco': banco,
                        'metodo_pago': metodos,
                        'beneficio': beneficio,
                        'descripcion': text[:200],
                        'tope': tope,
                        'dias': dias,
                        'vigencia': 'Ver app MODO',
                        'url': self.url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'modo'
                    }
                    
                    self.promos.append(promo)
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
