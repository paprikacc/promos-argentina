"""
🔄 Deduplicador Inteligente
Elimina promociones duplicadas usando múltiples estrategias
"""

import hashlib
from difflib import SequenceMatcher

class PromoDeduplicator:
    def __init__(self, similarity_threshold=0.85):
        self.similarity_threshold = similarity_threshold
    
    def create_signature(self, promo):
        """Crea una firma única para comparación"""
        # Normalizar para comparación
        comercio = promo.get('comercio', '').lower().strip()
        banco = promo.get('banco', '').lower().strip()
        beneficio = promo.get('beneficio', '').lower().strip()
        metodos = ''.join(sorted(promo.get('metodo_pago', []))).lower()
        dias = ''.join(sorted(promo.get('dias', []))).lower()
        
        signature = f"{comercio}|{banco}|{beneficio}|{metodos}|{dias}"
        return hashlib.md5(signature.encode()).hexdigest()
    
    def similarity_ratio(self, str1, str2):
        """Calcula similitud entre dos strings"""
        return SequenceMatcher(None, str1.lower(), str2.lower()).ratio()
    
    def are_similar(self, promo1, promo2):
        """Determina si dos promos son similares"""
        # Mismo comercio
        if promo1.get('comercio') != promo2.get('comercio'):
            return False
        
        # Mismo banco
        if promo1.get('banco') != promo2.get('banco'):
            return False
        
        # Similitud en beneficio
        beneficio_similarity = self.similarity_ratio(
            promo1.get('beneficio', ''),
            promo2.get('beneficio', '')
        )
        
        if beneficio_similarity < self.similarity_threshold:
            return False
        
        # Métodos de pago coinciden
        metodos1 = set(promo1.get('metodo_pago', []))
        metodos2 = set(promo2.get('metodo_pago', []))
        
        if metodos1 and metodos2:
            metodos_similarity = len(metodos1 & metodos2) / len(metodos1 | metodos2)
            if metodos_similarity < 0.5:
                return False
        
        return True
    
    def merge_promos(self, promo1, promo2):
        """Fusiona dos promociones similares, manteniendo la más completa"""
        merged = promo1.copy()
        
        # Tomar descripción más larga
        if len(promo2.get('descripcion', '')) > len(merged.get('descripcion', '')):
            merged['descripcion'] = promo2['descripcion']
        
        # Combinar métodos de pago
        metodos1 = set(merged.get('metodo_pago', []))
        metodos2 = set(promo2.get('metodo_pago', []))
        merged['metodo_pago'] = sorted(list(metodos1 | metodos2))
        
        # Combinar días
        dias1 = set(merged.get('dias', []))
        dias2 = set(promo2.get('dias', []))
        merged['dias'] = sorted(list(dias1 | dias2))
        
        # Usar tope si uno lo tiene
        if not merged.get('tope') and promo2.get('tope'):
            merged['tope'] = promo2['tope']
        
        # Usar vigencia más específica (la más larga)
        if len(promo2.get('vigencia', '')) > len(merged.get('vigencia', '')):
            merged['vigencia'] = promo2['vigencia']
        
        # Actualizar fuente
        if promo2.get('fuente') not in merged.get('fuente', ''):
            merged['fuente'] = f"{merged.get('fuente', '')}, {promo2.get('fuente', '')}".strip(', ')
        
        return merged
    
    def deduplicate_by_signature(self, promos):
        """Elimina duplicados exactos por firma"""
        seen = {}
        unique = []
        
        for promo in promos:
            signature = self.create_signature(promo)
            
            if signature not in seen:
                seen[signature] = promo
                unique.append(promo)
            else:
                # Fusionar con la existente
                seen[signature] = self.merge_promos(seen[signature], promo)
        
        return unique
    
    def deduplicate_by_similarity(self, promos):
        """Elimina duplicados similares"""
        unique = []
        
        for promo in promos:
            is_duplicate = False
            
            for i, unique_promo in enumerate(unique):
                if self.are_similar(promo, unique_promo):
                    # Fusionar
                    unique[i] = self.merge_promos(unique_promo, promo)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique.append(promo)
        
        return unique
    
    def deduplicate(self, promos):
        """Proceso completo de deduplicación"""
        print(f"📊 Deduplicación: {len(promos)} promociones iniciales")
        
        # Primera pasada: duplicados exactos
        step1 = self.deduplicate_by_signature(promos)
        print(f"   → Después de eliminar exactos: {len(step1)}")
        
        # Segunda pasada: duplicados similares
        step2 = self.deduplicate_by_similarity(step1)
        print(f"   → Después de eliminar similares: {len(step2)}")
        
        removed = len(promos) - len(step2)
        print(f"   ✅ {removed} duplicados eliminados")
        
        return step2
