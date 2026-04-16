from .base_scraper import BaseScraper
from datetime import datetime

class DiaScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Día"
        self.url = "https://diaonline.supermercadosdia.com.ar/medios-de-pago-y-promociones"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="networkidle")
            page.wait_for_timeout(3000)  # Esperar 3 segundos para JS
            
            # Scroll para cargar contenido lazy
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            
            promo_elements = page.query_selector_all('.promocion, .promo, article, [class*="card"]')
            
            for elem in promo_elements:
                try:
                    text = elem.inner_text()
                    
                    # Filtrar solo promociones bancarias
                    if not any(keyword in text.lower() for keyword in ['visa', 'mastercard', 'banco', 'descuento', '%']):
                        continue
                    
                    titulo = elem.query_selector('h3, h4, strong')
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
                        'vigencia': 'Consultar vigencia',
                        'url': self.url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'dia_oficial'
                    }
                    
                    self.promos.append(promo)
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
