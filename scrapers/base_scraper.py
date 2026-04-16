"""
🏗️ Base Scraper
Clase base con funcionalidad común para todos los scrapers
"""

from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout
from abc import ABC, abstractmethod
from datetime import datetime
import hashlib
import re
from pathlib import Path

class BaseScraper(ABC):
    """Clase base para todos los scrapers"""
    
    def __init__(self, headless=True):
        self.headless = headless
        self.promos = []
        self.comercio_name = "Desconocido"
        self.debug_dir = Path('debug_screenshots')
        self.debug_dir.mkdir(parents=True, exist_ok=True)
    
    def create_promo_id(self, comercio, beneficio, metodo_pago):
        unique_string = f"{comercio}_{beneficio}_{metodo_pago}".lower()
        return hashlib.md5(unique_string.encode()).hexdigest()[:12]
    
    def normalize_dias(self, text):
        dias_map = {
            'lun': 'Lunes', 'mar': 'Martes', 'mie': 'Miércoles', 'mié': 'Miércoles',
            'jue': 'Jueves', 'vie': 'Viernes', 'sab': 'Sábado', 'sáb': 'Sábado', 'dom': 'Domingo'
        }
        text_lower = text.lower()
        dias = []
        for key, value in dias_map.items():
            if key in text_lower or value.lower() in text_lower:
                dias.append(value)
        if not dias:
            if any(p in text_lower for p in ['todos los días', 'todos los dias', 'toda la semana']):
                return []
        seen = set()
        return [d for d in dias if not (d in seen or seen.add(d))]
    
    def extract_percentage(self, text):
        match = re.search(r'(\d+)%', text)
        return f"{match.group(1)}%" if match else None
    
    def extract_tope(self, text):
        patterns = [
            r'\$\s*(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)',
            r'hasta\s+\$?\s*(\d{1,3}(?:\.\d{3})*)',
            r'tope\s+(?:de\s+)?\$?\s*(\d{1,3}(?:\.\d{3})*)',
            r'máximo\s+\$?\s*(\d{1,3}(?:\.\d{3})*)'
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return f"${match.group(1)}"
        if any(p in text.lower() for p in ['sin tope', 'sin límite']):
            return None
        return None
    
    def extract_metodo_pago(self, text):
        text_lower = text.lower()
        metodos = []
        metodos_map = {
            'visa': 'Visa', 'mastercard': 'Mastercard', 'master card': 'Mastercard',
            'american express': 'American Express', 'amex': 'American Express',
            'cabal': 'Cabal', 'naranja': 'Naranja', 'modo': 'MODO',
            'mercado pago': 'Mercado Pago', 'mercadopago': 'Mercado Pago',
            'cuenta dni': 'Cuenta DNI', 'cuentadni': 'Cuenta DNI',
            'debito': 'Débito', 'débito': 'Débito', 'credito': 'Crédito', 'crédito': 'Crédito'
        }
        for key, value in metodos_map.items():
            if key in text_lower and value not in metodos:
                metodos.append(value)
        return metodos if metodos else ['No especificado']
    
    def extract_banco(self, text):
        bancos = {
            'galicia': 'Banco Galicia', 'santander': 'Banco Santander', 'bbva': 'BBVA',
            'macro': 'Banco Macro', 'nacion': 'Banco Nación', 'nación': 'Banco Nación',
            'provincia': 'Banco Provincia', 'icbc': 'ICBC', 'hsbc': 'HSBC',
            'ciudad': 'Banco Ciudad', 'supervielle': 'Banco Supervielle'
        }
        text_lower = text.lower()
        for key, value in bancos.items():
            if key in text_lower:
                return value
        return 'Todos los bancos'
    
    @abstractmethod
    def scrape(self, page):
        pass
    
    def _save_debug_screenshot(self, page, reason="unknown"):
        """Guarda captura de pantalla si algo falla para depurar"""
        try:
            filename = self.debug_dir / f"{self.comercio_name.lower().replace(' ', '_')}_{reason}.png"
            page.screenshot(path=str(filename), full_page=True)
            print(f"   📸 Debug screenshot guardado: {filename}")
        except Exception as e:
            print(f"   ⚠️ No se pudo guardar screenshot: {e}")
    
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
                page.set_default_timeout(45000)  # 45 segundos
                
                # Ejecutar el scraping específico
                self.scrape(page)
                
                # Si no encontró nada, tomar screenshot para debug
                if not self.promos:
                    print(f"   ⚠️ No se encontraron promos. Tomando screenshot...")
                    self._save_debug_screenshot(page, "no_promos_found")
                
                browser.close()
            
            print(f"✅ {self.comercio_name}: {len(self.promos)} promociones extraídas")
            
        except Exception as e:
            print(f"❌ Error en {self.comercio_name}: {str(e)[:200]}")
        
        return self.promos
