"""
🔧 Normalizador de Datos
Estandariza nombres de comercios, bancos y métodos de pago
"""

import json
import re
from pathlib import Path

class DataNormalizer:
    def __init__(self, config_path='config/settings.json'):
        self.config = self._load_config(config_path)
        self.comercios_map = self.config.get('comercios_normalizados', {})
        self.bancos_map = self.config.get('bancos_normalizados', {})
        self.metodos_map = self.config.get('metodos_pago_normalizados', {})
    
    def _load_config(self, config_path):
        """Carga el archivo de configuración"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"⚠️ Config no encontrado en {config_path}, usando valores por defecto")
            return {}
    
    def normalize_comercio(self, comercio):
        """Normaliza el nombre del comercio"""
        if not comercio:
            return "Desconocido"
        
        comercio_lower = comercio.strip().lower()
        
        # Buscar en mapeo
        for key, variations in self.comercios_map.items():
            for variation in variations:
                if variation.lower() == comercio_lower:
                    return variations[0]  # Retornar versión normalizada
        
        # Si no está en el mapeo, capitalizar correctamente
        return comercio.strip().title()
    
    def normalize_banco(self, banco):
        """Normaliza el nombre del banco"""
        if not banco:
            return "Todos los bancos"
        
        banco_lower = banco.strip().lower()
        
        # Buscar en mapeo
        for key, normalized in self.bancos_map.items():
            if key in banco_lower:
                return normalized
        
        # Capitalizar si no está en el mapeo
        return banco.strip().title()
    
    def normalize_metodo_pago(self, metodos):
        """Normaliza métodos de pago"""
        if not metodos:
            return ["No especificado"]
        
        if isinstance(metodos, str):
            metodos = [metodos]
        
        normalized = []
        
        for metodo in metodos:
            metodo_lower = metodo.strip().lower()
            found = False
            
            for key, normalized_name in self.metodos_map.items():
                if key in metodo_lower:
                    if normalized_name not in normalized:
                        normalized.append(normalized_name)
                    found = True
                    break
            
            if not found and metodo.strip():
                normalized.append(metodo.strip().title())
        
        return normalized if normalized else ["No especificado"]
    
    def normalize_beneficio(self, beneficio):
        """Normaliza el texto del beneficio"""
        if not beneficio:
            return ""
        
        # Limpiar espacios extras
        beneficio = ' '.join(beneficio.split())
        
        # Normalizar porcentajes
        beneficio = re.sub(r'(\d+)\s*%', r'\1%', beneficio)
        
        # Normalizar montos
        beneficio = re.sub(r'\$\s*', r'$', beneficio)
        
        return beneficio.strip()
    
    def normalize_tope(self, tope):
        """Normaliza el tope de reintegro"""
        if not tope or tope == "Sin tope":
            return None
        
        # Extraer números y formatear
        numbers = re.findall(r'\d+', str(tope).replace('.', '').replace(',', ''))
        if numbers:
            amount = ''.join(numbers)
            # Formatear con puntos de miles
            formatted = f"${int(amount):,}".replace(',', '.')
            return formatted
        
        return tope
    
    def normalize_dias(self, dias):
        """Normaliza los días de la semana"""
        if not dias:
            return []
        
        dias_correctos = {
            'lunes': 'Lunes',
            'martes': 'Martes',
            'miércoles': 'Miércoles',
            'miercoles': 'Miércoles',
            'jueves': 'Jueves',
            'viernes': 'Viernes',
            'sábado': 'Sábado',
            'sabado': 'Sábado',
            'domingo': 'Domingo'
        }
        
        normalized = []
        for dia in dias:
            dia_lower = dia.strip().lower()
            if dia_lower in dias_correctos:
                normalized_dia = dias_correctos[dia_lower]
                if normalized_dia not in normalized:
                    normalized.append(normalized_dia)
        
        # Ordenar por día de la semana
        orden_dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        normalized.sort(key=lambda x: orden_dias.index(x) if x in orden_dias else 7)
        
        return normalized
    
    def normalize_promo(self, promo):
        """Normaliza una promoción completa"""
        normalized = {
            'id': promo.get('id', ''),
            'comercio': self.normalize_comercio(promo.get('comercio', '')),
            'banco': self.normalize_banco(promo.get('banco', '')),
            'metodo_pago': self.normalize_metodo_pago(promo.get('metodo_pago', [])),
            'beneficio': self.normalize_beneficio(promo.get('beneficio', '')),
            'descripcion': promo.get('descripcion', '').strip(),
            'tope': self.normalize_tope(promo.get('tope')),
            'dias': self.normalize_dias(promo.get('dias', [])),
            'vigencia': promo.get('vigencia', '').strip(),
            'url': promo.get('url', ''),
            'actualizado': promo.get('actualizado', ''),
            'fuente': promo.get('fuente', '')
        }
        
        return normalized
