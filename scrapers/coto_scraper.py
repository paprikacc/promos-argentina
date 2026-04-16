from .base_scraper import BaseScraper
from datetime import datetime

class CotoScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Coto"
        self.url = "https://www.cotodigital.com.ar/promociones"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="load", timeout=30000)
            page.wait_for_timeout(5000)  # Esperar carga completa
            
            # Intentar hacer clic en sección de bancos si existe
            try:
                banco_tab = page.query_selector('a[href*="banco"], button:has-text("Bancos")')
                if banco_tab:
                    banco_tab.click()
                    page.wait_for_timeout(2000)
            except:
                pass
            
            promos = page.query_selector_all('.promo, .promocion, article, [class*="card"]')
            
            for promo_elem in promos:
                try:
                    text = promo_elem.inner_text()
                    
                    # Filtrar promociones bancarias
                    if not any(word in text.lower() for word in ['visa', 'mastercard', 'banco', 'tarjeta', '%']):
                        continue
                    
                    titulo = promo_elem.query_selector('h3, h4, h5, .titulo')
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
                        'vigencia': 'Ver detalles',
                        'url': self.url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'coto_oficial'
                    }
                    
                    self.promos.append(promo)
                    
                except Exception as e:
                    continue
        
        except Exception as e:
            print(f"  ❌ Error: {e}")
