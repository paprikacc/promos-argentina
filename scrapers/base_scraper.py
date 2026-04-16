"""
🏗️ Base Scraper
Clase base con funcionalidad común para todos los scrapers
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import re

class BaseScraper(ABC):
    """Clase base para todos los scrapers"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.promos = []
        self.comercio_name = "Desconocido"
    
    def create_promo_id(self, comercio, beneficio, metodo_pago):
        """Genera un ID único basado en hash"""
        unique_string = f"{comercio}_{beneficio}_{metodo_pago}".lower()
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def normalize_dias(self, text):
        """Normaliza y extrae días de la semana"""
        dias_map = {
            'lun': 'Lunes',
            'mar': 'Martes',
            'mie': 'Miércoles',
            'mié': 'Miércoles',
            'jue': 'Jueves',
            'vie': 'Viernes',
            'sab': 'Sábado',
            'sáb': 'Sábado',
            'dom': 'Domingo'
        }
        
        text_lower = text.lower()
        dias = []
        
        for key, value in dias_map.items():
            if key in text_lower or value.lower() in text_lower:
                dias.append(value)
        
        # Si no encuentra días específicos, verificar "todos los días"
        if not dias:
            if any(phrase in text_lower for phrase in ['todos los días', 'todos los dias', 'toda la semana', 'siempre']):
                return []  # Array vacío significa todos los días
        
        # Eliminar duplicados manteniendo orden
        seen = set()
        dias_unicos = []
        for dia in dias:
            if dia not in seen:
                seen.add(dia)
                dias_unicos.append(dia)
        
        return dias_unicos
    
    def extract_percentage(self, text):
        """Extrae el porcentaje de descuento"""
        match = re.search(r'(\d+)%', text)
        return f"{match.group(1)}%" if match else None
    
    def extract_tope(self, text):
        """Extrae el tope de reintegro"""
        # Buscar patrones como "$5000", "5.000", "hasta $X"
        patterns = [
            r'\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'hasta\s+\$?\s*(\d{1,3}(?:\.\d{3})*)',
            r'tope\s+(?:de\s+)?\$?\s*(\d{1,3}(?:\.\d{3})*)',
            r'máximo\s+\$?\s*(\d{1,3}(?:\.\d{3})*)',
            r'reintegro\s+(?:máximo\s+)?(?:de\s+)?\$?\s*(\d{1,3}(?:\.\d{3})*)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}"
        
        # Verificar si dice "sin tope"
        if any(phrase in text.lower() for phrase in ['sin tope', 'sin límite', 'sin limite']):
            return None
        
        return None
    
    def extract_metodo_pago(self, text):
        """Extrae métodos de pago"""
        text_lower = text.lower()
        metodos = []
        
        metodos_map = {
            'visa': 'Visa',
            'mastercard': 'Mastercard',
            'master card': 'Mastercard',
            'american express': 'American Express',
            'amex': 'American Express',
            'cabal': 'Cabal',
            'naranja': 'Naranja',
            'modo': 'MODO',
            'mercado pago': 'Mercado Pago',
            'mercadopago': 'Mercado Pago',
            'cuenta dni': 'Cuenta DNI',
            'cuentadni': 'Cuenta DNI',
            'debito': 'Débito',
            'débito': 'Débito',
            'credito': 'Crédito',
            'crédito': 'Crédito',
            'tarjeta': 'Tarjeta'
        }
        
        for key, value in metodos_map.items():
            if key in text_lower and value not in metodos:
                metodos.append(value)
        
        return metodos if metodos else ['No especificado']
    
    def extract_banco(self, text):
        """Extrae el banco de la promoción"""
        bancos = {
            'galicia': 'Banco Galicia',
            'santander': 'Banco Santander',
            'santander rio': 'Banco Santander',
            'bbva': 'BBVA',
            'macro': 'Banco Macro',
            'nacion': 'Banco Nación',
            'nación': 'Banco Nación',
            'provincia': 'Banco Provincia',
            'icbc': 'ICBC',
            'hsbc': 'HSBC',
            'ciudad': 'Banco Ciudad',
            'supervielle': 'Banco Supervielle',
            'patagonia': 'Banco Patagonia',
            'comafi': 'Banco Comafi',
            'itau': 'Banco Itaú',
            'itaú': 'Banco Itaú',
            'credicoop': 'Banco Credicoop',
            'frances': 'Banco Francés',
            'francés': 'Banco Francés',
            'industrial': 'Banco Industrial',
            'hipotecario': 'Banco Hipotecario'
        }
        
        text_lower = text.lower()
        for key, value in bancos.items():
            if key in text_lower:
                return value
        
        return 'Todos los bancos'
    
    @abstractmethod
    def scrape(self, page):
        """Método que debe implementar cada scraper"""
        pass
    
    def run(self):
        """Ejecuta el scraper con Playwright"""
        print(f"🔍 Iniciando scraping de {self.comercio_name}...")
        
        try:
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=self.headless)
                context = browser.new_context(
                    viewport={'width': 1920, 'height': 1080},
                    user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
                )
                page = context.new_page()
                page.set_default_timeout(30000)  # 30 segundos
                
                # Ejecutar el scraping específico
                self.scrape(page)
                
                browser.close()
            
            print(f"✅ {self.comercio_name}: {len(self.promos)} promociones extraídas")
            
        except Exception as e:
            print(f"❌ Error en {self.comercio_name}: {str(e)}")
        
        return self.promos
