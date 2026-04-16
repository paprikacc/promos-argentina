"""
🧹 Limpiador de Datos
Valida y limpia los datos antes de guardar
"""

import re
from datetime import datetime

class DataCleaner:
    def __init__(self, config):
        self.palabras_invalidas = config.get('palabras_clave_invalidas', [])
    
    def is_valid_promo(self, promo):
        """Valida si una promoción es válida"""
        # Debe tener comercio
        if not promo.get('comercio') or promo.get('comercio') == 'Desconocido':
            return False, "Sin comercio"
        
        # Debe tener beneficio
        if not promo.get('beneficio'):
            return False, "Sin beneficio"
        
        # No debe contener palabras inválidas
        texto_completo = f"{promo.get('beneficio', '')} {promo.get('descripcion', '')}".lower()
        for palabra in self.palabras_invalidas:
            if palabra.lower() in texto_completo:
                return False, f"Contiene palabra inválida: {palabra}"
        
        # Debe tener al menos un método de pago válido
        metodos = promo.get('metodo_pago', [])
        if not metodos or metodos == ['No especificado']:
            # Permitir si tiene banco específico
            if promo.get('banco') == 'Todos los bancos':
                return False, "Sin método de pago ni banco específico"
        
        return True, "OK"
    
    def clean_description(self, text):
        """Limpia el texto de la descripción"""
        if not text:
            return ""
        
        # Eliminar múltiples espacios
        text = ' '.join(text.split())
        
        # Eliminar saltos de línea
        text = text.replace('\n', ' ').replace('\r', '')
        
        # Eliminar caracteres especiales extraños
        text = re.sub(r'[^\w\s\$%.,;:()\-]', '', text, flags=re.UNICODE)
        
        # Limitar longitud
        if len(text) > 300:
            text = text[:297] + '...'
        
        return text.strip()
    
    def validate_date(self, date_str):
        """Valida formato de fecha ISO"""
        try:
            datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return True
        except:
            return False
    
    def clean_promo(self, promo):
        """Limpia una promoción completa"""
        cleaned = promo.copy()
        
        # Limpiar descripción
        cleaned['descripcion'] = self.clean_description(promo.get('descripcion', ''))
        
        # Validar fecha
        if not self.validate_date(promo.get('actualizado', '')):
            cleaned['actualizado'] = datetime.now().isoformat()
        
        # Asegurar que tope sea None si no existe
        if not cleaned.get('tope'):
            cleaned['tope'] = None
        
        # Asegurar arrays
        if not isinstance(cleaned.get('metodo_pago'), list):
            cleaned['metodo_pago'] = [cleaned.get('metodo_pago', 'No especificado')]
        
        if not isinstance(cleaned.get('dias'), list):
            cleaned['dias'] = []
        
        return cleaned
    
    def clean_all(self, promos):
        """Limpia todas las promociones"""
        print(f"🧹 Limpiando {len(promos)} promociones...")
        
        valid_promos = []
        invalid_count = 0
        invalid_reasons = {}
        
        for promo in promos:
            is_valid, reason = self.is_valid_promo(promo)
            
            if is_valid:
                cleaned = self.clean_promo(promo)
                valid_promos.append(cleaned)
            else:
                invalid_count += 1
                invalid_reasons[reason] = invalid_reasons.get(reason, 0) + 1
        
        print(f"   ✅ {len(valid_promos)} promociones válidas")
        print(f"   ❌ {invalid_count} promociones inválidas")
        
        if invalid_reasons:
            print("   📋 Razones de invalidez:")
            for reason, count in invalid_reasons.items():
                print(f"      - {reason}: {count}")
        
        return valid_promos
