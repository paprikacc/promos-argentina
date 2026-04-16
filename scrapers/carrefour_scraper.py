from .base_scraper import BaseScraper
from datetime import datetime

class CarrefourScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Carrefour"
        self.url = "https://www.carrefour.com.ar/descuentos-bancarios"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="networkidle")
            
            # Esperar a que carguen las promociones
            page.wait_for_selector('.promocion-item, .promo-card, [class*="promo"]', timeout=10000)
            
            # Ajustar selectores según la estructura real del sitio
            promo_cards = page.query_selector_all('.promocion-item, .promo-card, article')
            
            for card in promo_cards:
                try:
                    # Extraer información de cada tarjeta
                    titulo = card.query_selector('h3, h4, .titulo')
                    titulo_text = titulo.inner_text() if titulo else ''
                    
                    descripcion = card.query_selector('.descripcion, p, .detalle')
                    descripcion_text = descripcion.inner_text() if descripcion else ''
                    
                    full_text = f"{titulo_text} {descripcion_text}"
                    
                    # Extraer banco
                    banco_elem = card.query_selector('.banco, .entidad, img[alt*="banco"]')
                    banco = self.extract_banco(
                        banco_elem.get_attribute('alt') if banco_elem and banco_elem.tag_name == 'img' 
                        else banco_elem.inner_text() if banco_elem else full_text
                    )
                    
                    # Extraer métodos de pago
                    metodos = self.extract_metodo_pago(full_text)
                    
                    # Extraer beneficio
                    descuento = self.extract_percentage(full_text)
                    beneficio = descuento if descuento else titulo_text[:100]
                    
                    # Extraer tope
                    tope = self.extract_tope(full_text)
                    
                    # Extraer días
                    dias = self.normalize_dias(full_text)
                    
                    # Vigencia
                    vigencia_elem = card.query_selector('.vigencia, .fecha, time')
                    vigencia = vigencia_elem.inner_text() if vigencia_elem else 'Consultar vigencia'
                    
                    promo = {
                        'id': self.create_promo_id(self.comercio_name, beneficio, str(metodos)),
                        'comercio': self.comercio_name,
                        'banco': banco,
                        'metodo_pago': metodos,
                        'beneficio': beneficio,
                        'descripcion': descripcion_text[:200],
                        'tope': tope,
                        'dias': dias,
                        'vigencia': vigencia,
                        'url': self.url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'carrefour_oficial'
                    }
                    
                    self.promos.append(promo)
                    
                except Exception as e:
                    print(f"  ⚠️ Error procesando promo individual: {e}")
                    continue
        
        except Exception as e:
            print(f"  ❌ Error en scraping general: {e}")
