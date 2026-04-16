from .base_scraper import BaseScraper
from datetime import datetime

class JumboScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Jumbo"
        self.url = "https://www.jumbo.com.ar/descuentos-del-dia"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="domcontentloaded")
            
            # Esperar las promociones
            page.wait_for_selector('[class*="promo"], [class*="discount"], article', timeout=10000)
            
            # Intentar con diferentes selectores
            promo_cards = page.query_selector_all('article, .promo-card, [data-testid*="promo"]')
            
            for card in promo_cards:
                try:
                    text_content = card.inner_text()
                    
                    # Extraer título
                    titulo = card.query_selector('h2, h3, h4, [class*="title"]')
                    titulo_text = titulo.inner_text() if titulo else text_content.split('\n')[0]
                    
                    # Banco
                    banco = self.extract_banco(text_content)
                    
                    # Métodos de pago
                    metodos = self.extract_metodo_pago(text_content)
                    
                    # Beneficio
                    descuento = self.extract_percentage(text_content)
                    beneficio = descuento if descuento else titulo_text[:100]
                    
                    # Tope
                    tope = self.extract_tope(text_content)
                    
                    # Días
                    dias = self.normalize_dias(text_content)
                    
                    promo = {
                        'id': self.create_promo_id(self.comercio_name, beneficio, str(metodos)),
                        'comercio': self.comercio_name,
                        'banco': banco,
                        'metodo_pago': metodos,
                        'beneficio': beneficio,
                        'descripcion': text_content[:200],
                        'tope': tope,
                        'dias': dias,
                        'vigencia': 'Ver condiciones',
                        'url': self.url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'jumbo_oficial'
                    }
                    
                    self.promos.append(promo)
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
