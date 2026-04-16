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
