"""
🛡️ Detector de Fraude y Promociones Sospechosas
Filtra ofertas que parecen demasiado buenas para ser verdad
"""

import re

class FraudDetector:
    def __init__(self, config):
        self.config = config.get('fraud_detection', {})
        self.descuento_max = self.config.get('descuento_max_sospechoso', 90)
        self.palabras_sospechosas = self.config.get('palabras_sospechosas', [])
    
    def check_descuento_excesivo(self, promo):
        """Verifica descuentos excesivos"""
        beneficio = promo.get('beneficio', '')
        match = re.search(r'(\d+)%', beneficio)
        
        if match:
            descuento = int(match.group(1))
            if descuento >= self.descuento_max:
                return True, f"Descuento sospechoso: {descuento}%"
        
        return False, None
    
    def check_palabras_sospechosas(self, promo):
        """Verifica palabras clave sospechosas"""
        texto = f"{promo.get('beneficio', '')} {promo.get('descripcion', '')}".lower()
        
        for palabra in self.palabras_sospechosas:
            if palabra.lower() in texto:
                return True, f"Contiene palabra sospechosa: {palabra}"
        
        return False, None
    
    def check_datos_incompletos(self, promo):
        """Verifica si faltan datos críticos"""
        issues = []
        
        if not promo.get('comercio') or promo['comercio'] == 'Desconocido':
            issues.append("comercio desconocido")
        
        if not promo.get('beneficio'):
            issues.append("sin beneficio especificado")
        
        if promo.get('metodo_pago') == ['No especificado'] and promo.get('banco') == 'Todos los bancos':
            issues.append("sin método de pago ni banco")
        
        if issues:
            return True, f"Datos incompletos: {', '.join(issues)}"
        
        return False, None
    
    def check_beneficio_vago(self, promo):
        """Verifica si el beneficio es demasiado vago"""
        beneficio = promo.get('beneficio', '')
        
        palabras_vagas = ['descuento', 'promoción', 'oferta', 'beneficio']
        
        # Si el beneficio solo tiene palabras vagas sin números
        if len(beneficio) < 10 and not re.search(r'\d', beneficio):
            for palabra in palabras_vagas:
                if palabra in beneficio.lower():
                    return True, "Beneficio demasiado vago"
        
        return False, None
    
    def analyze(self, promo):
        """Analiza una promoción completa"""
        checks = [
            self.check_descuento_excesivo,
            self.check_palabras_sospechosas,
            self.check_datos_incompletos,
            self.check_beneficio_vago
        ]
        
        flags = []
        
        for check in checks:
            is_suspicious, reason = check(promo)
            if is_suspicious:
                flags.append(reason)
        
        return {
            'sospechosa': len(flags) > 0,
            'confianza': 100 - (len(flags) * 25),  # Resta 25% por cada flag
            'flags': flags
        }
    
    def filter_promos(self, promos, min_confianza=50):
        """Filtra promociones sospechosas"""
        print(f"\n🛡️ Analizando {len(promos)} promociones...")
        
        valid_promos = []
        suspicious_promos = []
        
        for promo in promos:
            analysis = self.analyze(promo)
            promo_copy = promo.copy()
            promo_copy['confianza'] = analysis['confianza']
            promo_copy['flags_fraude'] = analysis['flags']
            
            if analysis['confianza'] >= min_confianza:
                valid_promos.append(promo_copy)
            else:
                suspicious_promos.append(promo_copy)
        
        print(f"   ✅ Válidas: {len(valid_promos)}")
        print(f"   ⚠️ Sospechosas: {len(suspicious_promos)}")
        
        if suspicious_promos:
            print(f"   📋 Razones de sospecha:")
            flag_counts = {}
            for promo in suspicious_promos:
                for flag in promo['flags_fraude']:
                    flag_counts[flag] = flag_counts.get(flag, 0) + 1
            
            for flag, count in flag_counts.items():
                print(f"      - {flag}: {count}")
        
        return valid_promos
