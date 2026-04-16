"""
⭐ Sistema de Scoring de Promociones
Evalúa y prioriza las mejores ofertas
"""

import re
from datetime import datetime, timedelta

class PromoScorer:
    def __init__(self, config):
        self.config = config.get('scoring', {})
        self.pesos = self.config.get('pesos', {})
        self.umbral_destacada = self.config.get('umbral_destacada', 70)
    
    def extract_discount_value(self, beneficio):
        """Extrae el valor numérico del descuento"""
        if not beneficio:
            return 0
        
        # Buscar porcentaje
        match = re.search(r'(\d+)%', beneficio)
        if match:
            return int(match.group(1))
        
        # Buscar "2x1", "3x2", etc
        match = re.search(r'(\d+)x(\d+)', beneficio.lower())
        if match:
            get = int(match.group(1))
            pay = int(match.group(2))
            if pay > 0:
                return int(((get - pay) / get) * 100)
        
        return 0
    
    def score_descuento(self, promo):
        """Puntaje por descuento"""
        descuento = self.extract_discount_value(promo.get('beneficio', ''))
        
        if descuento >= 50:
            return self.pesos.get('descuento_alto', 40)
        elif descuento >= 30:
            return self.pesos.get('descuento_alto', 40) * 0.7
        elif descuento >= 20:
            return self.pesos.get('descuento_alto', 40) * 0.5
        elif descuento >= 10:
            return self.pesos.get('descuento_alto', 40) * 0.3
        else:
            return 0
    
    def score_tope(self, promo):
        """Puntaje por tope"""
        tope = promo.get('tope')
        
        # Sin tope es mejor
        if not tope or tope == "Sin tope":
            return self.pesos.get('sin_tope', 25)
        
        # Extraer valor del tope
        try:
            tope_value = int(re.sub(r'[^\d]', '', str(tope)))
            
            if tope_value >= 10000:
                return self.pesos.get('sin_tope', 25) * 0.7
            elif tope_value >= 5000:
                return self.pesos.get('sin_tope', 25) * 0.5
            else:
                return self.pesos.get('sin_tope', 25) * 0.3
        except:
            return self.pesos.get('sin_tope', 25) * 0.3
    
    def score_dias(self, promo):
        """Puntaje por disponibilidad de días"""
        dias = promo.get('dias', [])
        
        # Todos los días es mejor
        if not dias or len(dias) >= 7:
            return self.pesos.get('todos_los_dias', 15)
        
        # Más días = mejor
        if len(dias) >= 5:
            return self.pesos.get('todos_los_dias', 15) * 0.8
        elif len(dias) >= 3:
            return self.pesos.get('todos_los_dias', 15) * 0.5
        else:
            return self.pesos.get('todos_los_dias', 15) * 0.3
    
    def score_metodos_pago(self, promo):
        """Puntaje por múltiples métodos de pago"""
        metodos = promo.get('metodo_pago', [])
        
        if not metodos:
            return 0
        
        count = len(metodos)
        
        if count >= 4:
            return self.pesos.get('metodos_multiples', 10)
        elif count >= 3:
            return self.pesos.get('metodos_multiples', 10) * 0.7
        elif count >= 2:
            return self.pesos.get('metodos_multiples', 10) * 0.5
        else:
            return self.pesos.get('metodos_multiples', 10) * 0.3
    
    def score_vigencia(self, promo):
        """Puntaje por vigencia larga"""
        vigencia = promo.get('vigencia', '')
        
        if not vigencia or 'vigencia' in vigencia.lower():
            return self.pesos.get('vigencia_larga', 10) * 0.5
        
        # Intentar extraer fecha
        try:
            # Buscar patrones de fecha
            match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', vigencia)
            if match:
                day, month, year = match.groups()
                if len(year) == 2:
                    year = '20' + year
                
                end_date = datetime(int(year), int(month), int(day))
                days_remaining = (end_date - datetime.now()).days
                
                if days_remaining > 30:
                    return self.pesos.get('vigencia_larga', 10)
                elif days_remaining > 14:
                    return self.pesos.get('vigencia_larga', 10) * 0.7
                elif days_remaining > 7:
                    return self.pesos.get('vigencia_larga', 10) * 0.5
                else:
                    return self.pesos.get('vigencia_larga', 10) * 0.2
        except:
            pass
        
        return self.pesos.get('vigencia_larga', 10) * 0.5
    
    def calculate_score(self, promo):
        """Calcula el score total de una promoción"""
        score = 0
        
        score += self.score_descuento(promo)
        score += self.score_tope(promo)
        score += self.score_dias(promo)
        score += self.score_metodos_pago(promo)
        score += self.score_vigencia(promo)
        
        # Normalizar a 100
        return min(100, round(score, 2))
    
    def score_all(self, promos):
        """Calcula scores para todas las promociones"""
        scored_promos = []
        
        for promo in promos:
            promo_copy = promo.copy()
            promo_copy['score'] = self.calculate_score(promo)
            promo_copy['destacada'] = promo_copy['score'] >= self.umbral_destacada
            scored_promos.append(promo_copy)
        
        # Ordenar por score
        scored_promos.sort(key=lambda x: x['score'], reverse=True)
        
        return scored_promos
    
    def get_top_promos(self, promos, limit=20):
        """Obtiene las mejores promociones"""
        scored = self.score_all(promos)
        return scored[:limit]
    
    def get_destacadas(self, promos):
        """Obtiene solo las promociones destacadas"""
        scored = self.score_all(promos)
        return [p for p in scored if p['destacada']]
