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

https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/data/promos.json

### **Promociones Destacadas** (Top ofertas - Score ≥70)

https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/data/last-update.jsondata/promos_destacadas.json


### **Versión CSV**

https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/data/promos.csv


### **Estadísticas**

https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/data/stats.json


### **Novedades del Día**

https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/data/cambios.json


### **Última Actualización** (Metadata)


---

## 📱 Ejemplos de Uso

### **JavaScript / React Native**

```javascript
// Obtener todas las promociones
const fetchPromos = async () => {
  const response = await fetch(
    'https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/data/promos.json'
  );
  const data = await response.json();
  return data.promociones; // Array de promociones
};

// Filtrar por comercio
const getPromosByComercio = (promos, comercio) => {
  return promos.filter(p => p.comercio.toLowerCase() === comercio.toLowerCase());
};

// Filtrar por banco
const getPromosByBanco = (promos, banco) => {
  return promos.filter(p => p.banco.toLowerCase().includes(banco.toLowerCase()));
};

// Filtrar por día de la semana
const getPromosForToday = (promos) => {
  const dias = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado'];
  const hoy = dias[new Date().getDay()];
  
  return promos.filter(p => 
    p.dias.length === 0 || // Todos los días
    p.dias.includes(hoy)
  );
};

// Obtener solo destacadas
const getDestacadas = async () => {
  const response = await fetch(
    'https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/data/promos_destacadas.json'
  );
  const data = await response.json();
  return data.promociones;
};

flutter / dart

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
    );
  }
}

Future<List<Promo>> fetchPromos() async {
  final response = await http.get(
    Uri.parse('https://raw.githubusercontent.com/TU-USUARIO/promos-argentina/main/data/promos.json'),
  );

  if (response.statusCode == 200) {
    final data = json.decode(response.body);
    return (data['promociones'] as List)
        .map((p) => Promo.fromJson(p))
        .toList();
  }
  throw Exception('Error al cargar promociones');
}

// Filtrar por score
List<Promo> getTopPromos(List<Promo> promos, int minScore) {
  return promos.where((p) => p.score >= minScore).toList()
    ..sort((a, b) => b.score.compareTo(a.score));
}




