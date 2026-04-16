"""
🕷️ Clash Scraper
Extrae promociones de https://promos.clash.com.ar/supermercados/
"""

from .base_scraper import BaseScraper
from datetime import datetime

class ClashScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Clash (Multi-comercio)"
        self.url = "https://promos.clash.com.ar/supermercados/"
    
    def scrape(self, page):
        try:
            page.goto(self.url, wait_until="domcontentloaded")
            
            # Esperar a que carguen las promociones
            page.wait_for_selector('article, .promo, .card, [class*="promo"]', timeout=15000)
            
            # Scroll para cargar más contenido
            for _ in range(3):
                page.evaluate("window.scrollBy(0, 1000)")
                page.wait_for_timeout(1000)
            
            # Intentar varios selectores posibles
            promo_cards = page.query_selector_all('article, .promo-card, .card, .promo-item, [class*="promo-"]')
            
            print(f"   📦 Encontrados {len(promo_cards)} elementos potenciales")
            
            for card in promo_cards:
                try:
                    # Obtener todo el texto del elemento
                    full_text = card.inner_text()
                    
                    # Filtrar solo si contiene información de supermercados
                    if not any(keyword in full_text.lower() for keyword in ['supermercado', 'carrefour', 'jumbo', 'coto', 'día', 'disco', 'walmart', '%', 'descuento']):
                        continue
                    
                    # Extraer elementos específicos
                    titulo_elem = card.query_selector('h1, h2, h3, h4, .title, .titulo, [class*="title"]')
                    titulo_text = titulo_elem.inner_text() if titulo_elem else ''
                    
                    descripcion_elem = card.query_selector('p, .description, .descripcion, .detalle, [class*="desc"]')
                    descripcion_text = descripcion_elem.inner_text() if descripcion_elem else ''
                    
                    # Si no hay título ni descripción, usar el texto completo
                    if not titulo_text and not descripcion_text:
                        lines = full_text.split('\n')
                        titulo_text = lines[0] if lines else ''
                        descripcion_text = ' '.join(lines[1:]) if len(lines) > 1 else ''
                    
                    # Combinar todo el texto para análisis
                    combined_text = f"{titulo_text} {descripcion_text} {full_text}"
                    
                    # Intentar extraer comercio específico
                    comercio = self.extract_comercio_especifico(combined_text)
                    
                    # Extraer banco
                    banco = self.extract_banco(combined_text)
                    
                    # Extraer métodos de pago
                    metodos = self.extract_metodo_pago(combined_text)
                    
                    # Extraer beneficio
                    descuento = self.extract_percentage(combined_text)
                    beneficio = descuento if descuento else titulo_text[:100] if titulo_text else 'Promoción'
                    
                    # Si no hay beneficio válido, skip
                    if not beneficio or beneficio == 'Promoción':
                        continue
                    
                    # Extraer tope
                    tope = self.extract_tope(combined_text)
                    
                    # Extraer días
                    dias = self.normalize_dias(combined_text)
                    
                    # Extraer vigencia
                    vigencia = self.extract_vigencia(combined_text)
                    
                    # Intentar obtener enlace
                    link_elem = card.query_selector('a[href]')
                    promo_url = link_elem.get_attribute('href') if link_elem else self.url
                    if promo_url and not promo_url.startswith('http'):
                        promo_url = f"https://promos.clash.com.ar{promo_url}"
                    
                    promo = {
                        'id': self.create_promo_id(comercio, beneficio, str(metodos)),
                        'comercio': comercio,
                        'banco': banco,
                        'metodo_pago': metodos,
                        'beneficio': beneficio,
                        'descripcion': descripcion_text[:300] if descripcion_text else titulo_text[:300],
                        'tope': tope,
                        'dias': dias,
                        'vigencia': vigencia,
                        'url': promo_url,
                        'actualizado': datetime.now().isoformat(),
                        'fuente': 'clash'
                    }
                    
                    self.promos.append(promo)
                    
                except Exception as e:
                    print(f"  ⚠️ Error procesando elemento: {str(e)[:100]}")
                    continue
        
        except Exception as e:
            print(f"  ❌ Error en scraping: {e}")
    
    def extract_comercio_especifico(self, text):
        """Extrae el comercio específico del texto"""
        comercios = {
            'carrefour express': 'Carrefour Express',
            'carrefour': 'Carrefour',
            'jumbo': 'Jumbo',
            'coto': 'Coto',
            'día': 'Día',
            'dia': 'Día',
            'disco': 'Disco',
            'walmart': 'Walmart',
            'la anonima': 'La Anónima',
            'vea': 'Vea',
            'libertad': 'Libertad',
            'makro': 'Makro',
            'vital': 'Vital'
        }
        
        text_lower = text.lower()
        for key, value in comercios.items():
            if key in text_lower:
                return value
        
        return 'Supermercados'
    
    def extract_vigencia(self, text):
        """Extrae información de vigencia"""
        import re
        
        # Buscar patrones de fecha
        patterns = [
            r'hasta\s+el?\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'válido?\s+hasta\s+(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'vigencia:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',
            r'vence:?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"Hasta {match.group(1)}"
        
        # Buscar referencias temporales
        if 'todo el mes' in text.lower():
            return 'Todo el mes'
        if 'toda la semana' in text.lower():
            return 'Toda la semana'
        
        return 'Consultar vigencia'
