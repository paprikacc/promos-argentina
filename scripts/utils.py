"""Utilidades compartidas del sistema"""
import json
import csv
import os
from datetime import datetime
from pathlib import Path
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/scraping.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


def ensure_directories():
    """Crea los directorios necesarios si no existen"""
    dirs = ['data', 'data/cache', 'data/history', 'logs', 'config']
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)


def save_json(data, filepath):
    """Guarda datos en JSON minificado (sin espacios = mas rapido de descargar)"""
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, separators=(',', ':'))


def load_json(filepath):
    """Carga datos desde un archivo JSON"""
    if not Path(filepath).exists():
        return {}
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def load_config():
    """Carga la configuracion desde config/settings.json"""
    config_path = Path('config/settings.json')
    if config_path.exists():
        try:
            return load_json(str(config_path))
        except:
            pass
    return {
        "scraping": {"timeout": 30000, "retry_attempts": 3, "delay_between_scrapers": 2000},
        "cache": {"enabled": True, "ttl_hours": 6}
    }


def log_message(message):
    """Registra un mensaje en el log"""
    logger.info(message)


def save_csv(promos, filepath):
    """Guarda las promociones en formato CSV"""
    if not promos:
        return
    
    fieldnames = ['id', 'comercio', 'banco', 'metodo_pago', 'beneficio', 'descripcion', 
                  'tope', 'dias', 'vigencia', 'url', 'fuente', 'score', 'destacada']
    
    with open(filepath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        for promo in promos:
            row = promo.copy()
            if isinstance(row.get('metodo_pago'), list):
                row['metodo_pago'] = ', '.join(row['metodo_pago'])
            if isinstance(row.get('dias'), list):
                row['dias'] = ', '.join(row['dias'])
            writer.writerow(row)


def generate_stats(promos):
    """Genera estadisticas de las promociones"""
    stats = {
        'total': len(promos),
        'por_comercio': {},
        'por_banco': {},
        'por_metodo_pago': {},
        'por_dia': {},
        'con_tope': 0,
        'sin_tope': 0
    }
    
    for p in promos:
        # Por comercio
        c = p.get('comercio', 'Otro')
        stats['por_comercio'][c] = stats['por_comercio'].get(c, 0) + 1
        
        # Por banco
        b = p.get('banco', 'Otro')
        stats['por_banco'][b] = stats['por_banco'].get(b, 0) + 1
        
        # Por metodo de pago
        for m in p.get('metodo_pago', ['No especificado']):
            stats['por_metodo_pago'][m] = stats['por_metodo_pago'].get(m, 0) + 1
        
        # Por dia
        dias = p.get('dias', [])
        if not dias:
            stats['por_dia']['Todos los dias'] = stats['por_dia'].get('Todos los dias', 0) + 1
        else:
            for d in dias:
                stats['por_dia'][d] = stats['por_dia'].get(d, 0) + 1
        
        # Topes
        if p.get('tope'):
            stats['con_tope'] += 1
        else:
            stats['sin_tope'] += 1
    
    return stats


def print_stats(stats):
    """Imprime las estadisticas de forma legible"""
    print("\n" + "=" * 60)
    print("📊 ESTADISTICAS DE PROMOCIONES")
    print("=" * 60)
    print(f"Total de promociones: {stats['total']}\n")
    
    print("🏪 Por Comercio:")
    for k, v in sorted(stats['por_comercio'].items(), key=lambda x: -x[1]):
        print(f"   • {k}: {v}")
    
    print("\n🏦 Por Banco:")
    for k, v in sorted(stats['por_banco'].items(), key=lambda x: -x[1]):
        print(f"   • {k}: {v}")
    
    print("\n💳 Por Metodo de Pago:")
    for k, v in sorted(stats['por_metodo_pago'].items(), key=lambda x: -x[1]):
        print(f"   • {k}: {v}")
    
    print("\n📅 Por Dia:")
    for k, v in sorted(stats['por_dia'].items(), key=lambda x: -x[1]):
        print(f"   • {k}: {v}")
    
    print(f"\n💰 Topes:")
    print(f"   • Con tope: {stats['con_tope']}")
    print(f"   • Sin tope: {stats['sin_tope']}")
    print("=" * 60)
