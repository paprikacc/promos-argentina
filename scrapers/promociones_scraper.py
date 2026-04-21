from .base_scraper import BaseScraper
from datetime import datetime
import re

class PromocionesScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Promociones.com.ar (Multi-comercio)"
        self.url = "https://www.promociones.com.ar/category/supermercados/"
    
    def scrape(self, page):
        try:
            print(f"   🌐 Cargando: {self.url}")
            page.goto(self.url, wait_until="load", timeout=60000)
            page.wait_for_timeout(8000)
            
            # Scroll intensivo
            for i in range(8):
                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(1500)
            
            # DEBUG: Imprimir todo el texto de la página
            body_text = page.evaluate("() => document.body?.innerText || ''")
            print(f"   📝 TEXTO DE LA PÁGINA (primeros 1000 chars):")
            print(f"   {body_text[:1000]}")
            print(f"   --- FIN TEXTO ---")
            
            # Buscar todos los elementos posibles
            all_elements = page.query_selector_all('div, article, section, li, a, span, p, h1, h2, h3, h4')
            print(f"   📦 Total elementos en página: {len(all_elements)}")
            
            # Buscar elementos con texto que contenga números
            elementos_con_datos = []
            for el in all_elements:
                try:
                    text = el.inner_text()
                    if text and len(text) > 5 and len(text) < 500:
                        has_number = re.search(r'\d+', text)
                        if has_number:
                            elementos_con_datos.append((el, text))
                except:
                    continue
            
            print(f"   📊 Elementos con números: {len(elementos_con_datos)}")
            
            # Mostrar los primeros 20 elementos
            for i, (el, text) in enumerate(elementos_con_datos[:20]):
                print(f"   [{i}] {text[:150]}")
            
            # Buscar promociones con filtros relajados
            for card, text in elementos_con_datos:
                try:
                    text_lower = text.lower()
                    
                    palabras_clave = ['%', 'descuento', 'banco', 'super', 'carrefour', 'jumbo', 
                                     'coto', 'dia', 'día', 'makro', 'off', 'ahorro', 'promo',
                                     'reintegro', 'cashback', 'beneficio', 'oferta']
                    
                    if not any(k in text_lower for k in palabras_clave):
                        continue
                    
                    descuento = self.extract_percentage(text)
                    
                    if not descuento:
                        match_2x1 = re.search(r'(\d)\s*[xX]\s*(\d)', text)
                        if match_2x1:
                            descuento = f"{match_2x1.group(0)} oferta"
                        else:
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
                        'fuente': 'promociones.com.ar'
                    }
                    self.promos.append(promo)
                    
                except:
                    continue
            
            print(f"   ✅ Promos extraídas: {len(self.promos)}")
        
        except Exception as e:
            print(f"  ❌ Error: {str(e)[:200]}")
    
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
