# 🛒 Promociones Argentina - API Automática

[![Actualización Diaria](https://github.com/paprikacc/promos-argentina/actions/workflows/update-promos.yml/badge.svg)](https://github.com/paprikacc/promos-argentina/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

> Sistema automatizado de extracción, normalización y publicación de promociones bancarias en supermercados de Argentina. **Actualización diaria automática** mediante GitHub Actions.

---

## 📊 Características

✅ **8 Fuentes de Datos** - Carrefour, Jumbo, Día, Coto, Makro, MODO, Clash, Promociones.com.ar  
✅ **Actualización Automática** - Todos los días a las 6:00 AM (hora Argentina)  
✅ **Deduplicación Inteligente** - Elimina promociones duplicadas  
✅ **Sistema de Scoring** - Identifica las mejores ofertas (score 0-100)  
✅ **Detección de Fraude** - Filtra promociones sospechosas  
✅ **Detector de Cambios** - Identifica nuevas promos y modificaciones  
✅ **Múltiples Formatos** - JSON, CSV, con estadísticas  
✅ **Cache Inteligente** - Evita scraping innecesario  
✅ **Histórico** - Guarda snapshots diarios (retención 30 días)  

---

## 🏪 Comercios Incluidos

| Comercio | Sitio Oficial | Estado |
|----------|--------------|--------|
| **Carrefour** | ✅ Oficial | Activo |
| **Jumbo** | ✅ Oficial | Activo |
| **Día** | ✅ Oficial | Activo |
| **Coto** | ✅ Oficial | Activo |
| **Makro** | ✅ Oficial | Activo |
| **MODO** | ✅ Multi-comercio | Activo |
| **Clash Promos** | 🌐 Agregador | Activo |
| **Promociones.com.ar** | 🌐 Agregador | Activo |

---

## 💳 Métodos de Pago Soportados

- 💳 Visa / Mastercard / American Express
- 📱 MODO
- 💰 Mercado Pago
- 🆔 Cuenta DNI
- 🏦 Todas las principales entidades bancarias argentinas

---

## 🔗 URLs de Acceso Directo (para tu App)

### **JSON Principal** (Todas las promociones)

https://raw.githubusercontent.com/paprikacc//promos-argentina/main/data/promos.json

### **Promociones Destacadas** (Top ofertas - Score ≥70)

https://raw.githubusercontent.com/paprikacc/promos-argentina/main/                                     https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data/last-update.jsondata/promos_destacadas.json


### **Versión CSV**

https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data/promos.csv


### **Estadísticas**

https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data/stats.json


### **Novedades del Día**

https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data/cambios.json


### **Última Actualización** (Metadata)


---

## 📱 Ejemplos de Uso


---

## 📱 Ejemplos de Integración

### **JavaScript / React Native / Next.js**

```javascript
// Hook personalizado para React
import { useState, useEffect } from 'react';

const PROMOS_URL = 'https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data/promos.json';

export function usePromos() {
  const [promos, setPromos] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetch(PROMOS_URL)
      .then(res => res.json())
      .then(data => {
        setPromos(data.promociones);
        setLoading(false);
      })
      .catch(err => {
        setError(err);
        setLoading(false);
      });
  }, []);

  return { promos, loading, error };
}

// Funciones de filtrado
export const filtrarPorComercio = (promos, comercio) => {
  return promos.filter(p => 
    p.comercio.toLowerCase() === comercio.toLowerCase()
  );
};

export const filtrarPorBanco = (promos, banco) => {
  return promos.filter(p => 
    p.banco.toLowerCase().includes(banco.toLowerCase())
  );
};

export const filtrarPorDia = (promos, dia) => {
  return promos.filter(p => 
    p.dias.length === 0 || // Todos los días
    p.dias.includes(dia)
  );
};

export const promosValidasHoy = (promos) => {
  const dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
  const hoy = dias[new Date().getDay()];
  return filtrarPorDia(promos, hoy);
};

export const topPromos = (promos, limit = 10) => {
  return [...promos]
    .sort((a, b) => (b.score || 0) - (a.score || 0))
    .slice(0, limit);
};

// Ejemplo de uso en componente
function PromosList() {
  const { promos, loading, error } = usePromos();

  if (loading) return <div>Cargando promociones...</div>;
  if (error) return <div>Error: {error.message}</div>;

  const hoy = promosValidasHoy(promos);
  const mejores = topPromos(hoy, 5);

  return (
    <div>
      <h2>Top 5 Ofertas de Hoy</h2>
      {mejores.map(promo => (
        <div key={promo.id}>
          <h3>{promo.comercio}</h3>
          <p>{promo.beneficio}</p>
          <span>Score: {promo.score}</span>
        </div>
      ))}

    </div>
  );
}
**Flutter / Dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class Promo {
  final String id;
  final String comercio;
  final String banco;
  final List<String> metodoPago;
  final String beneficio;
  final String? tope;
  final List<String> dias;
  final int score;
  final bool destacada;
  final String descripcion;

  Promo({
    required this.id,
    required this.comercio,
    required this.banco,
    required this.metodoPago,
    required this.beneficio,
    this.tope,
    required this.dias,
    required this.score,
    required this.destacada,
    required this.descripcion,
  });

  factory Promo.fromJson(Map<String, dynamic> json) {
    return Promo(
      id: json['id'],
      comercio: json['comercio'],
      banco: json['banco'],
      metodoPago: List<String>.from(json['metodo_pago']),
      beneficio: json['beneficio'],
      tope: json['tope'],
      dias: List<String>.from(json['dias']),
      score: json['score'] ?? 0,
      destacada: json['destacada'] ?? false,
      descripcion: json['descripcion'] ?? '',
    );
  }
}

class PromosService {
  static const String baseUrl = 
    'https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data';

  Future<List<Promo>> fetchPromos() async {
    final response = await http.get(Uri.parse('$baseUrl/promos.json'));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data['promociones'] as List)
          .map((p) => Promo.fromJson(p))
          .toList();
    } else {
      throw Exception('Error al cargar promociones');
    }
  }

  Future<List<Promo>> fetchDestacadas() async {
    final response = await http.get(Uri.parse('$baseUrl/promos_destacadas.json'));

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      return (data['promociones'] as List)
          .map((p) => Promo.fromJson(p))
          .toList();
    } else {
      throw Exception('Error al cargar destacadas');
    }
  }

  List<Promo> filtrarPorComercio(List<Promo> promos, String comercio) {
    return promos.where((p) => 
      p.comercio.toLowerCase() == comercio.toLowerCase()
    ).toList();
  }

  List<Promo> promosValidasHoy(List<Promo> promos) {
    final dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 
                  'Jueves', 'Viernes', 'Sábado'];
    final hoy = dias[DateTime.now().weekday % 7];
    
    return promos.where((p) => 
      p.dias.isEmpty || p.dias.contains(hoy)
    ).toList();
  }

  List<Promo> topPromos(List<Promo> promos, {int limit = 10}) {
    final sorted = List<Promo>.from(promos)
      ..sort((a, b) => b.score.compareTo(a.score));
    return sorted.take(limit).toList();
  }
}

// Ejemplo de uso en Widget
class PromosPage extends StatefulWidget {
  @override
  _PromosPageState createState() => _PromosPageState();
}

class _PromosPageState extends State<PromosPage> {
  final PromosService _service = PromosService();
  late Future<List<Promo>> _promosFuture;

  @override
  void initState() {
    super.initState();
    _promosFuture = _service.fetchPromos();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('Promociones')),
      body: FutureBuilder<List<Promo>>(
        future: _promosFuture,
        builder: (context, snapshot) {
          if (snapshot.hasData) {
            final promos = _service.promosValidasHoy(snapshot.data!);
            final top = _service.topPromos(promos, limit: 5);
            
            return ListView.builder(
              itemCount: top.length,
              itemBuilder: (context, index) {
                final promo = top[index];
                return ListTile(
                  title: Text(promo.comercio),
                  subtitle: Text(promo.beneficio),
                  trailing: Chip(
                    label: Text('${promo.score}'),
                    backgroundColor: promo.destacada ? Colors.green : Colors.grey,
                  ),
                );
              },
            );
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          }
          return Center(child: CircularProgressIndicator());
        },
      ),
    );
  }
}
** Python / Django / Flask
import requests
from datetime import datetime
from typing import List, Dict, Optional

class PromosAPI:
    BASE_URL = "https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data"
    
    @staticmethod
    def obtener_promos() -> List[Dict]:
        """Obtiene todas las promociones"""
        response = requests.get(f"{PromosAPI.BASE_URL}/promos.json")
        response.raise_for_status()
        data = response.json()
        return data['promociones']
    
    @staticmethod
    def obtener_destacadas() -> List[Dict]:
        """Obtiene solo promociones destacadas"""
        response = requests.get(f"{PromosAPI.BASE_URL}/promos_destacadas.json")
        response.raise_for_status()
        data = response.json()
        return data['promociones']
    
    @staticmethod
    def obtener_stats() -> Dict:
        """Obtiene estadísticas"""
        response = requests.get(f"{PromosAPI.BASE_URL}/stats.json")
        response.raise_for_status()
        return response.json()
    
    @staticmethod
    def filtrar_por_comercio(promos: List[Dict], comercio: str) -> List[Dict]:
        """Filtra promociones por comercio"""
        return [p for p in promos if comercio.lower() in p['comercio'].lower()]
    
    @staticmethod
    def filtrar_por_banco(promos: List[Dict], banco: str) -> List[Dict]:
        """Filtra por banco"""
        return [p for p in promos if banco.lower() in p['banco'].lower()]
    
    @staticmethod
    def filtrar_por_metodo_pago(promos: List[Dict], metodo: str) -> List[Dict]:
        """Filtra por método de pago"""
        return [p for p in promos if metodo in p['metodo_pago']]
    
    @staticmethod
    def promos_validas_hoy(promos: List[Dict]) -> List[Dict]:
        """Obtiene promociones válidas para hoy"""
        dias = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
        hoy = dias[datetime.now().weekday()]
        
        return [p for p in promos if not p['dias'] or hoy in p['dias']]
    
    @staticmethod
    def top_promos(promos: List[Dict], limit: int = 10) -> List[Dict]:
        """Obtiene las mejores promociones por score"""
        sorted_promos = sorted(promos, key=lambda x: x.get('score', 0), reverse=True)
        return sorted_promos[:limit]
    
    @staticmethod
    def buscar(promos: List[Dict], query: str) -> List[Dict]:
        """Búsqueda de texto en beneficio y descripción"""
        query_lower = query.lower()
        return [
            p for p in promos 
            if query_lower in p['beneficio'].lower() 
            or query_lower in p['descripcion'].lower()
        ]

# Ejemplo de uso en Django View
from django.http import JsonResponse
from django.views import View

class PromosView(View):
    def get(self, request):
        api = PromosAPI()
        
        # Obtener parámetros
        comercio = request.GET.get('comercio')
        banco = request.GET.get('banco')
        destacadas_only = request.GET.get('destacadas') == 'true'
        
        # Obtener promos
        if destacadas_only:
            promos = api.obtener_destacadas()
        else:
            promos = api.obtener_promos()
        
        # Aplicar filtros
        if comercio:
            promos = api.filtrar_por_comercio(promos, comercio)
        
        if banco:
            promos = api.filtrar_por_banco(promos, banco)
        
        # Solo válidas hoy
        promos = api.promos_validas_hoy(promos)
        
        return JsonResponse({
            'total': len(promos),
            'promociones': promos
        })

# Ejemplo de uso en script
if __name__ == "__main__":
    api = PromosAPI()
    
    # Obtener todas las promos
    promos = api.obtener_promos()
    print(f"📊 Total de promociones: {len(promos)}")
    
    # Top 5 ofertas
    top_5 = api.top_promos(promos, 5)
    print("\n⭐ Top 5 Ofertas:")
    for i, promo in enumerate(top_5, 1):
        print(f"{i}. {promo['comercio']}: {promo['beneficio']} (Score: {promo['score']})")
    
    # Promos de Carrefour válidas hoy
    carrefour_hoy = api.filtrar_por_comercio(
        api.promos_validas_hoy(promos), 
        'Carrefour'
    )
    print(f"\n🛒 Carrefour hoy: {len(carrefour_hoy)} promociones")
    
    # Estadísticas
    stats = api.obtener_stats()
    print(f"\n📊 Estadísticas:")
    print(f"   - Total general: {stats['total']}")
    print(f"   - Con tope: {stats['con_tope']}")
    print(f"   - Sin tope: {stats['sin_tope']}")
** Estructura del JSON
data/promos.json
{
  "ultima_actualizacion": "2024-01-15T09:00:00.123456",
  "total_promociones": 247,
  "promociones": [
    {
      "id": "a3f7b2c91d4e",
      "comercio": "Carrefour",
      "banco": "Banco Galicia",
      "metodo_pago": ["Visa", "Mastercard"],
      "beneficio": "20%",
      "descripcion": "20% de descuento en compras superiores a $10.000 con tarjetas Visa y Mastercard del Banco Galicia",
      "tope": "$5.000",
      "dias": ["Lunes", "Martes", "Miércoles"],
      "vigencia": "Hasta 31/01/2024",
      "url": "https://www.carrefour.com.ar/descuentos-bancarios",
      "actualizado": "2024-01-15T09:00:00",
      "fuente": "carrefour_oficial",
      "score": 85,
      "destacada": true,
      "confianza": 100,
      "flags_fraude": []
    }
  ]
}
**Documentación de Campos
Campo	Tipo	Descripción	Ejemplo
id	string	Hash único MD5 (12 chars) para evitar duplicados	"a3f7b2c91d4e"
comercio	string	Nombre normalizado del supermercado	"Carrefour"
banco	string	Banco emisor (normalizado)	"Banco Galicia"
metodo_pago	array<string>	Métodos de pago aceptados	["Visa", "Mastercard"]
beneficio	string	Descuento principal	"20%", "3x2"
descripcion	string	Descripción completa (max 300 chars)	"20% de descuento..."
tope	string | null	Tope de reintegro formateado	"$5.000" o null
dias	array<string>	Días válidos ([] = todos los días)	["Lunes", "Martes"] o []
vigencia	string	Fecha de vencimiento o descripción	"Hasta 31/01/2024"
url	string	URL de la fuente original	"https://..."
actualizado	string	ISO 8601 timestamp	"2024-01-15T09:00:00"
fuente	string	Identificador de la fuente	"carrefour_oficial"
score	number	Puntuación de calidad (0-100)	85
destacada	boolean	true si score ≥ 70	true
confianza	number	Nivel de confianza anti-fraude (0-100)	100
flags_fraude	array<string>	Alertas de fraude detectadas	[] o ["Descuento sospechoso"]

**Arquitectura del Sistema

┌──────────────────────────────────────────────────────────────┐
│                       🌐 FUENTES WEB                         │
│  Carrefour │ Jumbo │ Día │ Coto │ Makro │ MODO │ Clash      │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│              🕷️ SCRAPERS (Playwright + BS4)                  │
│  • Navegación automatizada con Chromium headless             │
│  • Manejo de JavaScript y contenido dinámico                 │
│  • Retry logic y timeouts configurables                      │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│                  🧠 CEREBRO PRINCIPAL (main.py)              │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FASE 1: 💾 Cache Manager                              │ │
│  │  → Verifica si hay datos frescos (TTL: 6h)            │ │
│  │  → Evita scraping innecesario                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FASE 2: 🔧 Normalizer                                 │ │
│  │  → Estandariza nombres de comercios                   │ │
│  │  → Normaliza bancos y métodos de pago                 │ │
│  │  → Formatea topes y beneficios                        │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FASE 3: 🔄 Deduplicator                               │ │
│  │  → Elimina duplicados exactos (por hash)              │ │
│  │  → Detecta duplicados similares (85% similitud)       │ │
│  │  → Fusiona información complementaria                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FASE 4: 🧹 Data Cleaner                               │ │
│  │  → Valida campos obligatorios                         │ │
│  │  → Limpia caracteres especiales                       │ │
│  │  → Filtra palabras clave inválidas                    │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FASE 5: 🛡️ Fraud Detector                             │ │
│  │  → Detecta descuentos excesivos (>90%)                │ │
│  │  → Identifica palabras sospechosas                    │ │
│  │  → Asigna nivel de confianza (0-100)                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FASE 6: ⭐ Promo Scorer                                │ │
│  │  → Evalúa descuento (peso: 40%)                       │ │
│  │  → Evalúa tope (peso: 25%)                            │ │
│  │  → Evalúa disponibilidad de días (peso: 15%)          │ │
│  │  → Evalúa métodos de pago (peso: 10%)                 │ │
│  │  → Evalúa vigencia (peso: 10%)                        │ │
│  │  → Score final: 0-100                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FASE 7: 🔔 Change Detector                            │ │
│  │  → Compara con snapshot anterior                      │ │
│  │  → Detecta nuevas promociones                         │ │
│  │  → Identifica promociones eliminadas                  │ │
│  │  → Rastrea modificaciones                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                         ↓                                    │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ FASE 8: 💾 Export                                     │ │
│  │  → promos.json (todas)                                │ │
│  │  → promos_destacadas.json (score ≥70)                 │ │
│  │  → promos.csv (formato tabular)                       │ │
│  │  → stats.json (estadísticas)                          │ │
│  │  → cambios.json (changelog)                           │ │
│  │  → history/YYYY-MM-DD.json (snapshot)                 │ │
│  └────────────────────────────────────────────────────────┘ │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│              📊 DATA/ (GitHub Repository)                    │
│  • Acceso público mediante URLs raw                          │
│  • Actualización automática diaria (GitHub Actions)          │
│  • Versionado con Git                                        │
└────────────┬─────────────────────────────────────────────────┘
             │
             ▼
┌──────────────────────────────────────────────────────────────┐
│                   📱 TU APLICACIÓN                           │
│  • Fetch simple vía HTTP                                     │
│  • Sin necesidad de backend                                  │
│  • Datos siempre actualizados                                │
└──────────────────────────────────────────────────────────────┘
**Instalación y Uso Local
Prerequisitos
Python 3.11 o superior
pip (gestor de paquetes de Python)
Git
**Instalación Paso a Paso
# 1. Clonar el repositorio
git clone https://github.com/paprika/promos-argentina.git
cd promos-argentina

# 2. Crear entorno virtual (recomendado)
python -m venv venv

# 3. Activar entorno virtual
# En Linux/Mac:
source venv/bin/activate
# En Windows:
venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Instalar navegador Playwright
playwright install chromium
playwright install-deps chromium

# 6. Verificar instalación
python -c "import playwright; print('✅ Playwright instalado correctamente')"

# 7. Ejecutar scraping
python scripts/main.py

# 8. Verificar archivos generados
ls -lh data/
** Variables de Entorno (Opcional)

Crea un archivo .env en la raíz del proyecto:
# .env
HEADLESS=true          # false para ver el navegador en acción
USE_CACHE=true         # false para forzar scraping completo

** Configuración Avanzada
Edita config/settings.json para personalizar:
{
  "scraping": {
    "timeout": 30000,           // Timeout en ms
    "retry_attempts": 3,        // Reintentos por scraper
    "delay_between_scrapers": 2000  // Delay entre scrapers
  },
  "cache": {
    "enabled": true,
    "ttl_hours": 6              // Tiempo de vida del cache
  },
  "scoring": {
    "umbral_destacada": 70      // Score mínimo para destacadas
  }
}
GitHub Actions - Automatización
Configuración de Ejecución Automática
El sistema se ejecuta automáticamente todos los días a las 6:00 AM (hora Argentina) mediante GitHub Actions.

Configurar Permisos (IMPORTANTE)
Ve a tu repositorio en GitHub
Settings → Actions → General
En "Workflow permissions":
✅ Selecciona "Read and write permissions"
✅ Marca "Allow GitHub Actions to create and approve pull requests"
Click en "Save"
Ejecutar Manualmente
Ve a la pestaña Actions
Selecciona "Actualizar Promociones Diarias"
Click en "Run workflow"
Selecciona opciones:
force_scrape: true para ignorar cache
Click en "Run workflow" (botón verde)
Monitoreo de Ejecuciones
✅ Verde: Ejecución exitosa
❌ Rojo: Error en el scraping
🟡 Amarillo: En progreso
Ver detalles: Click en cualquier ejecución → Ver logs completos

📊 Estadísticas y Análisis
Archivo stats.json
{
  "total": 247,
  "por_comercio": {
    "Carrefour": 45,
    "Jumbo": 38,
    "Coto": 35,
    "Día": 32,
    "Makro": 28,
    "MODO": 24,
    "Supermercados": 45
  },
  "por_banco": {
    "Banco Galicia": 67,
    "Banco Santander": 42,
    "BBVA": 35,
    "Banco Macro": 28,
    "Banco Nación": 25
  },
  "por_metodo_pago": {
    "Visa": 156,
    "Mastercard": 143,
    "MODO": 38,
    "Mercado Pago": 32,
    "American Express": 18,
    "Débito": 89,
    "Crédito": 158
  },
  "por_dia": {
    "Lunes": 89,
    "Martes": 92,
    "Miércoles": 87,
    "Jueves": 85,
    "Viernes": 78,
    "Sábado": 56,
    "Domingo": 43,
    "Todos los días": 47
  },
  "con_tope": 189,
  "sin_tope": 58
}
** Análisis de Tendencias
import requests
import pandas as pd
import matplotlib.pyplot as plt

# Cargar estadísticas
stats = requests.get(
    'https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data/stats.json'
).json()

# Crear DataFrame de comercios
df_comercios = pd.DataFrame(
    list(stats['por_comercio'].items()),
    columns=['Comercio', 'Promociones']
).sort_values('Promociones', ascending=False)

# Visualizar
df_comercios.plot(kind='bar', x='Comercio', y='Promociones', 
                  title='Promociones por Comercio')
plt.tight_layout()
plt.show()

🤝 Contribuir
¡Las contribuciones son bienvenidas! Aquí hay algunas formas de contribuir:

Agregar un Nuevo Comercio
Fork el repositorio
Crea un nuevo scraper en scrapers/:
# scrapers/nuevo_comercio_scraper.py
from .base_scraper import BaseScraper
from datetime import datetime

class NuevoComercioScraper(BaseScraper):
    def __init__(self, headless=True):
        super().__init__(headless)
        self.comercio_name = "Nuevo Comercio"
        self.url = "https://..."
    
    def scrape(self, page):
        # Tu implementación aquí
        pass
Actualiza scrapers/__init__.py:
from .nuevo_comercio_scraper import NuevoComercioScraper

__all__ = [
    # ... otros scrapers
    'NuevoComercioScraper'
]
Actualiza scripts/main.py:
from scrapers import (
    # ... otros
    NuevoComercioScraper
)

def get_scrapers(self):
    return [
        # ... otros
        NuevoComercioScraper(self.headless)
    ]
ommit y crea un Pull Request
Reportar Bugs
🐛 Usa GitHub Issues
Incluye:
Descripción del error
Pasos para reproducir
Logs relevantes
Versión de Python
Sugerir Mejoras
💡 Abre un Discussion
Describe tu idea detalladamente
⚠️ Disclaimer Legal
Términos de Uso
Este proyecto:

✅ Extrae información pública de sitios web
✅ Respeta los robots.txt de cada sitio
✅ Implementa delays para no saturar servidores
✅ Se actualiza máximo 1 vez al día
Responsabilidades
⚖️ No nos hacemos responsables por cambios en las promociones
🔍 Verifica siempre las condiciones en el sitio oficial antes de comprar
📜 No garantizamos la exactitud de los datos
🤖 Uso educativo y de referencia
Privacidad
🔒 No recopilamos datos personales
🔒 No almacenamos información de usuarios
🔒 No usamos cookies ni tracking
📄 Licencia
Este proyecto está bajo la licencia MIT. Ver LICENSE para más detalles.
MIT License - Uso libre con atribución

📞 Soporte y Contacto
<div align="center">
Canal	Link
🐛 Reportar Bugs	GitHub Issues
💡 Sugerencias	GitHub Discussions
📧 Email	paprikacasacreativa@gmail.com
</div>

🌟 Agradecimientos
Playwright - Automatización de navegadores web
BeautifulSoup - Parsing de HTML
Python - Lenguaje de programación
GitHub Actions - CI/CD gratuito
Todos los comercios que publican sus promociones públicamente
📈 Roadmap
v1.0 (Actual) ✅
 Scraping de 8 fuentes
 Sistema de scoring
 Detección de fraude
 Deduplicación inteligente
 GitHub Actions automation
v1.1 (Próximo) 🚧
 Sistema de notificaciones (Telegram/Email)
 Filtro por ubicación geográfica
 Historial de precios y tendencias
 API REST con FastAPI
v2.0 (Futuro) 🔮
 Dashboard web interactivo
 Predicción de mejores días para comprar (ML)
 App móvil nativa (Flutter)
 Sistema de alertas personalizadas
 Integración con Google Sheets
📊 Badges y Stats
<div align="center">
GitHub stars
GitHub forks
GitHub watchers

GitHub last commit
GitHub issues
GitHub pull requests

</div>
🎓 Casos de Uso
1. Aplicación Móvil de Ahorro
Usuario abre app → Fetch promos.json → Filtra por ubicación
→ Muestra ofertas del día → Usuario ahorra $$
2. Bot de Telegram/Discord
Bot: /promos Carrefour → Fetch API → Filtra → Envía mensaje
Usuario: ¡Gracias! Voy a aprovechar el 30%
3. Dashboard Empresarial
Empresa → Analiza tendencias de precios → stats.json
→ Toma decisiones de compra basadas en datos
4. Investigación Académica
Estudiante → Descarga histórico → Analiza con Pandas
→ Paper sobre "Comportamiento de Promociones en Argentina"
<div align="center">
🚀 ¡Comienza Ahora!
# Prueba la API en 1 línea
curl https://raw.githubusercontent.com/paprikacc/promos-argentina/main/data/promos.json
Hecho con ❤️ en Argentina 🇦🇷

Si este proyecto te ayudó, considera darle una ⭐

⬆ Volver arriba

</div> ```
