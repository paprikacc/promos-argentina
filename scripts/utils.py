"""
🛠️ Utilidades
Funciones auxiliares para el proyecto
"""

import json
import csv
import os
from datetime import datetime
from pathlib import Path

def ensure_directories():
    """Asegura que existan los directorios necesarios"""
    dirs = ['data', 'logs', 'config']
    for dir_name in dirs:
        Path(dir_name).mkdir(exist_ok=True)

def save_json(data, filename):
    """Guarda datos en JSON"""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print(f"   💾 JSON guardado: {filename}")
        return True
    except Exception as e:
        print(f"   ❌ Error guardando JSON: {e}")
        return False

def save_csv(promos, filename):
    """Guarda promociones en CSV"""
    if not promos:
        print("   ⚠️ No hay datos para guardar en CSV")
        return False
    
    try:
        # Preparar datos para CSV (convertir arrays a strings)
        csv_data = []
        for promo in promos:
            csv_promo = promo.copy()
            csv_promo['metodo_pago'] = ', '.join(promo['metodo_pago'])
            csv_promo['dias'] = ', '.join(promo['dias']) if promo['dias'] else 'Todos los días'
            csv_data.append(csv_promo)
        
        # Escribir CSV
        keys = csv_data[0].keys()
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=keys)
            writer.writeheader()
            writer.writerows(csv_data)
        
        print(f"   💾 CSV guardado: {filename}")
        return True
    except Exception as e:
        print(f"   ❌ Error guardando CSV: {e}")
        return False

def load_config(config_path='config/settings.json'):
    """Carga configuración"""
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"⚠️ Archivo de configuración no encontrado: {config_path}")
        return {}
    except json.JSONDecodeError as e:
        print(f"❌ Error parseando JSON: {e}")
        return {}

def log_message(message, log_file='logs/scraping.log'):
    """Registra mensaje en log"""
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_entry = f"[{timestamp}] {message}\n"
    
    try:
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    except Exception as e:
        print(f"Error escribiendo log: {e}")

def generate_stats(promos):
    """Genera estadísticas de las promociones"""
    stats = {
        'total': len(promos),
        'por_comercio': {},
        'por_banco': {},
        'por_metodo_pago': {},
        'por_dia': {},
        'con_tope': 0,
        'sin_tope': 0
    }
    
    for promo in promos:
        # Por comercio
        comercio = promo['comercio']
        stats['por_comercio'][comercio] = stats['por_comercio'].get(comercio, 0) + 1
        
        # Por banco
        banco = promo['banco']
        stats['por_banco'][banco] = stats['por_banco'].get(banco, 0) + 1
        
        # Por método de pago
        for metodo in promo['metodo_pago']:
            stats['por_metodo_pago'][metodo] = stats['por_metodo_pago'].get(metodo, 0) + 1
        
        # Por día
        if promo['dias']:
            for dia in promo['dias']:
                stats['por_dia'][dia] = stats['por_dia'].get(dia, 0) + 1
        else:
            stats['por_dia']['Todos los días'] = stats['por_dia'].get('Todos los días', 0) + 1
        
        # Topes
        if promo['tope']:
            stats['con_tope'] += 1
        else:
            stats['sin_tope'] += 1
    
    return stats

def print_stats(stats):
    """Imprime estadísticas formateadas"""
    print("\n" + "=" * 60)
    print("📊 ESTADÍSTICAS DE PROMOCIONES")
    print("=" * 60)
    print(f"Total de promociones: {stats['total']}")
    
    print("\n🏪 Por Comercio:")
    for comercio, count in sorted(stats['por_comercio'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {comercio}: {count}")
    
    print("\n🏦 Por Banco:")
    for banco, count in sorted(stats['por_banco'].items(), key=lambda x: x[1], reverse=True)[:10]:
        print(f"   • {banco}: {count}")
    
    print("\n💳 Por Método de Pago:")
    for metodo, count in sorted(stats['por_metodo_pago'].items(), key=lambda x: x[1], reverse=True):
        print(f"   • {metodo}: {count}")
    
    print("\n📅 Por Día:")
    dias_orden = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo', 'Todos los días']
    for dia in dias_orden:
        if dia in stats['por_dia']:
            print(f"   • {dia}: {stats['por_dia'][dia]}")
    
    print(f"\n💰 Topes:")
    print(f"   • Con tope: {stats['con_tope']}")
    print(f"   • Sin tope: {stats['sin_tope']}")
    print("=" * 60)
