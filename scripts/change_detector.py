"""
🔔 Detector de Cambios
Identifica nuevas promociones y cambios significativos
"""

import json
from pathlib import Path
from datetime import datetime

class ChangeDetector:
    def __init__(self, history_dir='data/history'):
        self.history_dir = Path(history_dir)
        self.history_dir.mkdir(parents=True, exist_ok=True)
        self.previous_data = self._load_previous()
    
    def _load_previous(self):
        """Carga los datos del scraping anterior"""
        try:
            # Buscar el archivo más reciente
            files = sorted(self.history_dir.glob('*.json'), reverse=True)
            if files:
                with open(files[0], 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"⚠️ No se pudo cargar historial anterior: {e}")
        
        return {'promociones': []}
    
    def _save_current(self, promos):
        """Guarda el snapshot actual"""
        filename = self.history_dir / f"{datetime.now().strftime('%Y-%m-%d')}.json"
        
        data = {
            'fecha': datetime.now().isoformat(),
            'total': len(promos),
            'promociones': promos
        }
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"⚠️ Error guardando historial: {e}")
    
    def detect_changes(self, current_promos):
        """Detecta cambios entre scraping actual y anterior"""
        previous_promos = self.previous_data.get('promociones', [])
        
        # Crear sets de IDs
        previous_ids = {p['id'] for p in previous_promos}
        current_ids = {p['id'] for p in current_promos}
        
        # Detectar cambios
        new_promos = [p for p in current_promos if p['id'] not in previous_ids]
        removed_promos = [p for p in previous_promos if p['id'] not in current_ids]
        
        # Detectar modificaciones
        modified_promos = []
        for current in current_promos:
            if current['id'] in previous_ids:
                previous = next((p for p in previous_promos if p['id'] == current['id']), None)
                if previous:
                    # Comparar campos clave
                    if (current.get('beneficio') != previous.get('beneficio') or
                        current.get('tope') != previous.get('tope') or
                        current.get('vigencia') != previous.get('vigencia')):
                        modified_promos.append({
                            'promo': current,
                            'cambios': self._get_changes(previous, current)
                        })
        
        changes = {
            'nuevas': new_promos,
            'eliminadas': removed_promos,
            'modificadas': modified_promos,
            'total_nuevas': len(new_promos),
            'total_eliminadas': len(removed_promos),
            'total_modificadas': len(modified_promos)
        }
        
        # Guardar snapshot actual
        self._save_current(current_promos)
        
        return changes
    
    def _get_changes(self, old, new):
        """Obtiene los cambios específicos entre dos promos"""
        changes = []
        
        fields = ['beneficio', 'tope', 'vigencia', 'dias', 'metodo_pago']
        
        for field in fields:
            old_value = old.get(field)
            new_value = new.get(field)
            
            if old_value != new_value:
                changes.append({
                    'campo': field,
                    'anterior': old_value,
                    'actual': new_value
                })
        
        return changes
    
    def print_summary(self, changes):
        """Imprime resumen de cambios"""
        print("\n🔔 DETECTOR DE CAMBIOS")
        print("=" * 70)
        
        if changes['total_nuevas'] > 0:
            print(f"✨ Nuevas promociones: {changes['total_nuevas']}")
            for promo in changes['nuevas'][:5]:  # Mostrar primeras 5
                print(f"   • {promo['comercio']}: {promo['beneficio']}")
            if changes['total_nuevas'] > 5:
                print(f"   ... y {changes['total_nuevas'] - 5} más")
        
        if changes['total_eliminadas'] > 0:
            print(f"\n❌ Promociones expiradas: {changes['total_eliminadas']}")
        
        if changes['total_modificadas'] > 0:
            print(f"\n📝 Promociones modificadas: {changes['total_modificadas']}")
            for mod in changes['modificadas'][:3]:
                print(f"   • {mod['promo']['comercio']}: {len(mod['cambios'])} cambios")
        
        if changes['total_nuevas'] == 0 and changes['total_eliminadas'] == 0 and changes['total_modificadas'] == 0:
            print("ℹ️ No se detectaron cambios desde la última ejecución")
        
        print("=" * 70)
