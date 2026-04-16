import sys
import os
import json
import csv
from datetime import datetime

# Agregar el directorio padre al path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers import (
    CarrefourScraper,
    JumboScraper,
    DiaScraper,
    CotoScraper,
    MakroScraper,
    ModoScraper
)

def main():
    print("=" * 60)
    print("🛒 INICIANDO SCRAPING DE PROMOCIONES")
    print("=" * 60)
    
    headless = os.getenv('HEADLESS', 'true').lower() == 'true'
    
    # Lista de scrapers
    scrapers = [
        CarrefourScraper(headless),
        JumboScraper(headless),
        DiaScraper(headless),
        CotoScraper(headless),
        MakroScraper(headless),
        ModoScraper(headless)
    ]
    
    all_promos = []
    errores = []
    
    # Ejecutar cada scraper
    for scraper in scrapers:
        try:
            promos = scraper.run()
            all_promos.extend(promos)
        except Exception as e:
            error_msg = f"Error en {scraper.comercio_name}: {str(e)}"
            print(f"❌ {error_msg}")
            errores.append(error_msg)
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN FINAL")
    print("=" * 60)
    print(f"✅ Total de promociones: {len(all_promos)}")
    print(f"❌ Scrapers con errores: {len(errores)}")
    
    # Eliminar duplicados por ID
    unique_promos = {promo['id']: promo for promo in all_promos}.values()
    unique_promos_list = list(unique_promos)
    
    print(f"🔄 Promociones únicas: {len(unique_promos_list)}")
    
    # Guardar JSON
    save_json(unique_promos_list)
    
    # Guardar CSV
    save_csv(unique_promos_list)
    
    # Guardar metadata
    save_metadata(len(unique_promos_list), errores)
    
    print("\n✅ Proceso completado exitosamente!")

def save_json(promos):
    """Guarda las promociones en JSON"""
    data = {
        'ultima_actualizacion': datetime.now().isoformat(),
        'total_promociones': len(promos),
        'promociones': promos
    }
    
    os.makedirs('data', exist_ok=True)
    
    with open('data/promos.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"💾 JSON guardado: data/promos.json")

def save_csv(promos):
    """Guarda las promociones en CSV"""
    if not promos:
        return
    
    os.makedirs('data', exist_ok=True)
    
    # Convertir arrays a strings para CSV
    csv_promos = []
    for promo in promos:
        csv_promo = promo.copy()
        csv_promo['metodo_pago'] = ', '.join(promo['metodo_pago'])
        csv_promo['dias'] = ', '.join(promo['dias']) if promo['dias'] else 'Todos'
        csv_promos.append(csv_promo)
    
    keys = csv_promos[0].keys()
    
    with open('data/promos.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(csv_promos)
    
    print(f"💾 CSV guardado: data/promos.csv")

def save_metadata(total, errores):
    """Guarda metadata de la actualización"""
    metadata = {
        'fecha': datetime.now().isoformat(),
        'total_promociones': total,
        'errores': errores,
        'fuentes': [
            'Carrefour',
            'Jumbo',
            'Día',
            'Coto',
            'Makro',
            'MODO'
        ]
    }
    
    with open('data/last-update.json', 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    
    print(f"💾 Metadata guardada: data/last-update.json")

if __name__ == "__main__":
    main()
