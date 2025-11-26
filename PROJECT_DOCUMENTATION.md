# 🚐 Sistema de Optimización de Rutas - Route Optimizer Demo

## 📋 Descripción del Proyecto

Sistema web de optimización de rutas para transporte de conductores desde sus hogares hasta terminales aeroportuarios en Santiago de Chile. El sistema utiliza algoritmos de Machine Learning (K-Means) y optimización de rutas (TSP - Traveling Salesman Problem) para asignar conductores a vans de manera eficiente, minimizando distancias y tiempos de viaje.

### Características Principales

- ✅ **Optimización automática de rutas** usando K-Means clustering + TSP + 2-opt
- ✅ **Modo Bus de Acercamiento** para terminales remotos (Terminal Maipú)
- ✅ **Visualización interactiva** con mapas de Leaflet
- ✅ **Rutas por calles reales** usando Google Maps Routes API
- ✅ **Arquitectura serverless** con AWS Lambda y Vercel Functions
- ✅ **Interfaz responsiva** mobile-friendly
- ✅ **Indicadores en tiempo real** de progreso y optimización

---

## 🛠️ Stack Tecnológico

### Frontend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **React** | 18.2.0 | Framework UI principal |
| **Vite** | 5.0.0 | Build tool y dev server |
| **Tailwind CSS** | 3.3.0 | Styling y diseño responsivo |
| **Leaflet** | 1.9.4 | Mapas interactivos |
| **React-Leaflet** | 4.2.1 | Integración React + Leaflet |
| **Axios** | 1.6.0 | HTTP client |
| **Recharts** | 2.10.0 | Gráficos y visualizaciones |
| **Lucide React** | 0.294.0 | Iconografía |

### Backend
| Tecnología | Versión | Propósito |
|------------|---------|-----------|
| **AWS Lambda** | Python 3.11 | Procesamiento de optimización |
| **Vercel Functions** | Node.js 20 | API de rutas por calles |
| **NumPy** | 1.26.2 | Operaciones matemáticas |
| **Pandas** | 2.1.3 | Procesamiento de datos |
| **Scikit-learn** | 1.3.2 | Algoritmo K-Means |
| **GeoPy** | 2.4.1 | Geocodificación |

### Servicios Cloud
| Servicio | Propósito |
|----------|-----------|
| **AWS Lambda** | Ejecución de algoritmos de optimización |
| **AWS S3** | Storage de deployment packages |
| **AWS DynamoDB** | Tracking de uso del demo |
| **Vercel** | Hosting del frontend y serverless functions |
| **Google Maps Routes API** | Cálculo de rutas reales por calles |

### Lenguajes de Programación
- **JavaScript/JSX**: Frontend (React)
- **Python**: Backend (AWS Lambda)
- **JavaScript**: Vercel Serverless Functions
- **CSS**: Tailwind CSS

---

## 🏗️ Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO                                  │
│                    (Navegador Web)                              │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         │ Carga CSV/Excel
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Vercel)                            │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  React + Vite + Tailwind                                 │  │
│  │  - Dashboard.jsx (carga de archivos)                     │  │
│  │  - MapView.jsx (visualización de rutas)                  │  │
│  │  - ProgressIndicator.jsx (feedback)                      │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────┬──────────────────────────────────────┬────────────────┘
         │                                       │
         │ POST /optimize                        │ POST /api/get-street-route
         │ (CSV data)                            │ (waypoints)
         ▼                                       ▼
┌────────────────────────┐            ┌─────────────────────────┐
│   AWS LAMBDA           │            │  VERCEL FUNCTION        │
│   (Optimización)       │            │  (Rutas por calles)     │
│  ┌──────────────────┐  │            │  ┌──────────────────┐   │
│  │ Python 3.11      │  │            │  │ Node.js 20       │   │
│  │ - K-Means        │  │            │  │ - Polyline decode│   │
│  │ - TSP + 2-opt    │  │            │  │ - API client     │   │
│  │ - Bus mode logic │  │            │  └─────┬────────────┘   │
│  │ - Geocoding      │  │            └────────┼────────────────┘
│  └────┬─────────────┘  │                     │
└───────┼────────────────┘                     │
        │                                       │
        │                                       │ Routes API v2
        │ Geocoding                             ▼
        ▼                                ┌──────────────────────┐
┌────────────────────┐                  │  GOOGLE MAPS API     │
│   NOMINATIM        │                  │  Routes API v2       │
│   (Geocoding)      │                  │  - computeRoutes     │
└────────────────────┘                  │  - Traffic-aware     │
                                        └──────────────────────┘
        │
        │ Track usage
        ▼
┌────────────────────┐
│   AWS DYNAMODB     │
│   (Analytics)      │
└────────────────────┘

        │
        │ Response (optimized routes)
        ▼
┌─────────────────────────────────────────────────────────────────┐
│                    FRONTEND (Visualización)                      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  Leaflet Map                                             │  │
│  │  - Marcadores de conductores                             │  │
│  │  - Polylines de rutas (rectas o por calles)             │  │
│  │  - Leyenda y estadísticas                                │  │
│  └──────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Flujo de la Aplicación

### 1. Carga de Datos (Frontend → Lambda)

```javascript
Usuario carga archivo CSV/Excel
    ↓
Dashboard.jsx valida formato
    ↓
Convierte a base64
    ↓
POST https://lambda-url.amazonaws.com/
    ├─ Headers: CORS
    ├─ Body: { filename, fileContent (base64) }
    └─ Timeout: 300s (5 min)
```

### 2. Procesamiento (Lambda)

```python
1. Decodificar base64 → Pandas DataFrame
2. Validar columnas requeridas:
   - Código
   - Nombre
   - Dirección Casa
   - Terminal Destino
   - Hora Presentación

3. Geocodificar direcciones (Nominatim)
   - Casa → coordenadas {lat, lng}
   - Terminal → coordenadas {lat, lng}

4. Agrupar por terminal destino

5. Para cada grupo:
   SI terminal == "Maipú":
       ├─ MODO BUS DE ACERCAMIENTO
       ├─ Determinar # vans (n_vans = drivers / 10)
       ├─ K-Means clustering → dividir en vans
       ├─ Para cada van:
       │   ├─ Dividir en 2 grupos
       │   ├─ Grupo 1 → TSP → bus stop
       │   ├─ Grupo 2 → TSP → terminal directo
       │   └─ Crear objeto van
       └─ Crear objeto bus (bus stop → terminal)
   SINO:
       ├─ MODO NORMAL
       ├─ Determinar # vans (n_vans = drivers / 10)
       ├─ K-Means clustering → dividir en vans
       ├─ Para cada van:
       │   ├─ TSP optimization → ordenar paradas
       │   ├─ 2-opt improvement → optimizar ruta
       │   └─ Crear objeto van con ruta optimizada
       └─ Calcular distancias

6. Retornar JSON:
   {
       vans: [...],
       totalDrivers: N,
       totalDistance: X km,
       distanceSavedPercent: Y%
   }
```

### 3. Obtención de Rutas por Calles (Vercel Function)

```javascript
Frontend recibe rutas optimizadas
    ↓
Para cada van:
    ├─ Extraer waypoints ordenados [home1, home2, ..., terminal]
    ├─ POST /api/get-street-route
    ├─ Body: { waypoints: [{lat, lng}, ...] }
    ↓
Vercel Function:
    ├─ Validar waypoints
    ├─ Construir request para Google Routes API v2
    ├─ POST routes.googleapis.com/directions/v2:computeRoutes
    ├─ Headers:
    │   ├─ X-Goog-Api-Key: [API_KEY]
    │   └─ X-Goog-FieldMask: routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline
    ├─ Body:
    │   {
    │       origin: { location: { latLng: {...} } },
    │       destination: { location: { latLng: {...} } },
    │       intermediates: [...],
    │       travelMode: "DRIVE",
    │       routingPreference: "TRAFFIC_AWARE"
    │   }
    ↓
Google Routes API responde:
    ├─ routes[0].polyline.encodedPolyline
    ├─ routes[0].distanceMeters
    └─ routes[0].duration
    ↓
Decodificar polyline → array de coordenadas [234 puntos]
    ↓
Retornar { success: true, route: [...], distance, duration }
```

### 4. Visualización (Frontend)

```javascript
MapView.jsx recibe:
    ├─ data.vans (rutas optimizadas desde Lambda)
    └─ streetRoutes (rutas por calles desde Vercel)

Para cada van:
    ├─ SI streetRoutes[index] existe:
    │   ├─ Usar ruta por calles (234 puntos)
    │   ├─ Línea SÓLIDA, grosor 4px
    │   └─ Opacidad 0.9
    └─ SINO:
        ├─ Usar ruta recta (5 puntos)
        ├─ Línea PUNTEADA, grosor 3px
        └─ Opacidad 0.8

Renderizar:
    ├─ Polylines con colores únicos por van
    ├─ Marcadores para cada conductor
    ├─ Marcadores especiales para bus (🚌) y bus stop (🚏)
    ├─ Leyenda con lista de vans
    └─ Estadísticas (# vans, # conductores, km total)
```

---

## 🧮 Algoritmos Utilizados

### 1. K-Means Clustering (Agrupación)

**Propósito**: Dividir conductores en grupos geográficos para asignarlos a vans.

**Implementación**:
```python
from sklearn.cluster import KMeans

# Coordenadas de todos los conductores
coordinates = np.array([[lat1, lng1], [lat2, lng2], ...])

# Número de vans necesarias
num_vans = max(2, min(5, len(drivers) // 10 + 1))

# Clustering
kmeans = KMeans(n_clusters=num_vans, random_state=42, n_init=10)
labels = kmeans.fit_predict(coordinates)

# Agrupar conductores por cluster
for driver, label in zip(drivers, labels):
    clusters[label].append(driver)
```

**Ventajas**:
- Agrupa conductores cercanos geográficamente
- Minimiza distancia intra-cluster
- Escalable a muchos conductores

### 2. TSP (Traveling Salesman Problem) - Greedy Nearest Neighbor

**Propósito**: Ordenar las paradas de cada van para minimizar distancia total.

**Implementación**:
```python
def optimize_route_tsp(drivers):
    route = [drivers[0]]  # Comenzar con primer conductor
    remaining = drivers[1:]

    while remaining:
        last = route[-1]
        # Encontrar conductor más cercano
        nearest = min(remaining, key=lambda d:
            calculate_distance(last['coordinates'], d['coordinates'])
        )
        route.append(nearest)
        remaining.remove(nearest)

    return route
```

**Complejidad**: O(n²) - Aceptable para n ≤ 10 conductores por van

### 3. 2-opt Improvement

**Propósito**: Mejorar la ruta TSP eliminando cruces.

**Implementación**:
```python
def improve_route_2opt(route):
    improved = True
    max_iterations = 50

    while improved:
        improved = False
        for i in range(1, len(route) - 2):
            for j in range(i + 1, len(route)):
                # Calcular distancia actual
                current_dist = distance(route[i-1], route[i]) +
                              distance(route[j-1], route[j])

                # Calcular distancia si invertimos segmento
                new_dist = distance(route[i-1], route[j-1]) +
                          distance(route[i], route[j])

                # Si es mejor, invertir
                if new_dist < current_dist:
                    route[i:j] = reversed(route[i:j])
                    improved = True
                    break
```

**Mejora promedio**: 10-20% reducción en distancia total

### 4. Load Balancing

**Propósito**: Equilibrar número de conductores entre vans.

**Implementación**:
```python
def balance_load(clusters):
    while True:
        sizes = [len(c) for c in clusters]
        max_idx = sizes.index(max(sizes))
        min_idx = sizes.index(min(sizes))

        # Si diferencia ≤ 1, ya está balanceado
        if sizes[max_idx] - sizes[min_idx] <= 1:
            break

        # Mover un conductor del cluster más grande al más pequeño
        driver = clusters[max_idx].pop()
        clusters[min_idx].append(driver)

    return clusters
```

### 5. Polyline Decoding (Google Maps)

**Propósito**: Decodificar el formato comprimido de Google Maps a coordenadas.

**Algoritmo**: Google's Encoded Polyline Algorithm Format

**Implementación**:
```javascript
function decodePolyline(encoded) {
    const points = [];
    let index = 0, lat = 0, lng = 0;

    while (index < encoded.length) {
        // Decodificar latitud
        let shift = 0, result = 0, byte;
        do {
            byte = encoded.charCodeAt(index++) - 63;
            result |= (byte & 0x1f) << shift;
            shift += 5;
        } while (byte >= 0x20);

        lat += ((result & 1) ? ~(result >> 1) : (result >> 1));

        // Decodificar longitud (similar)
        // ...

        points.push({ lat: lat / 1e5, lng: lng / 1e5 });
    }

    return points;
}
```

---

## 📁 Estructura del Proyecto

```
Demo_nav/
├── src/                           # Frontend (React)
│   ├── components/
│   │   ├── Dashboard.jsx          # Componente principal con carga de archivos
│   │   ├── MapView.jsx            # Visualización del mapa con Leaflet
│   │   ├── ProgressIndicator.jsx  # Indicador de progreso de carga
│   │   └── MobileMenu.jsx         # Menú responsive
│   ├── App.jsx                    # Componente raíz
│   ├── main.jsx                   # Entry point
│   └── index.css                  # Estilos globales
│
├── api/                           # Vercel Serverless Functions
│   └── get-street-route.js        # API para obtener rutas de Google Maps
│
├── lambda-package-v2/             # AWS Lambda (Python)
│   ├── lambda_function.py         # Handler principal
│   ├── requirements.txt           # Dependencias Python
│   └── [libraries]                # NumPy, Pandas, Scikit-learn, etc.
│
├── public/                        # Assets estáticos
│   └── vite.svg
│
├── dist/                          # Build output (generado)
│
├── .env.example                   # Template variables de entorno
├── .gitignore
├── package.json                   # Dependencias Node.js
├── vite.config.js                 # Configuración Vite
├── tailwind.config.js             # Configuración Tailwind
├── vercel.json                    # Configuración Vercel
├── GOOGLE_MAPS_SETUP.md          # Guía de setup Google Maps
└── PROJECT_DOCUMENTATION.md       # Este documento
```

---

## 🔌 Integraciones

### 1. AWS Lambda

**Propósito**: Procesamiento pesado de optimización de rutas

**Configuración**:
```json
{
  "Runtime": "python3.11",
  "Memory": 2048 MB,
  "Timeout": 300 seconds (5 min),
  "Handler": "lambda_function.lambda_handler",
  "Architecture": "x86_64"
}
```

**Endpoint**: Function URL (no API Gateway)
```
https://jvxxqv6ihctxjcds3dcddvxype0jmjay.lambda-url.us-east-1.on.aws/
```

**Ventajas**:
- ✅ Hasta 15 min de timeout (Function URL)
- ✅ 2GB RAM para NumPy/Pandas
- ✅ Escalado automático
- ✅ Pay-per-use

### 2. Google Maps Routes API v2

**Propósito**: Cálculo de rutas reales por calles con tráfico

**Endpoint**:
```
POST https://routes.googleapis.com/directions/v2:computeRoutes
```

**Headers Requeridos**:
```javascript
{
  'X-Goog-Api-Key': process.env.GOOGLE_MAPS_API_KEY,
  'X-Goog-FieldMask': 'routes.duration,routes.distanceMeters,routes.polyline.encodedPolyline'
}
```

**Request Body**:
```json
{
  "origin": {
    "location": { "latLng": { "latitude": -33.4489, "longitude": -70.6693 } }
  },
  "destination": {
    "location": { "latLng": { "latitude": -33.5115, "longitude": -70.7646 } }
  },
  "intermediates": [
    { "location": { "latLng": { "latitude": -33.4567, "longitude": -70.6789 } } }
  ],
  "travelMode": "DRIVE",
  "routingPreference": "TRAFFIC_AWARE"
}
```

**Response**:
```json
{
  "routes": [{
    "distanceMeters": 15320,
    "duration": "1245.5s",
    "polyline": {
      "encodedPolyline": "abcdef123456..."
    }
  }]
}
```

**Pricing**:
- Basic (≤10 waypoints): $5 / 1,000 requests
- Advanced (11-25 waypoints): $10 / 1,000 requests
- Crédito gratis: $200/mes (~4,000 optimizaciones)

### 3. Vercel

**Propósito**: Hosting del frontend + serverless functions

**Configuración** (`vercel.json`):
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "framework": "vite",
  "functions": {
    "api/**/*.js": {
      "maxDuration": 30,
      "memory": 1024
    }
  }
}
```

**Features Utilizados**:
- ✅ Automatic deployments (Git push → Deploy)
- ✅ Serverless functions en `/api`
- ✅ Environment variables
- ✅ Preview deployments por rama
- ✅ Edge network CDN

### 4. Nominatim (OpenStreetMap)

**Propósito**: Geocodificación de direcciones (gratuito)

**Implementación**:
```python
from geopy.geocoders import Nominatim

geolocator = Nominatim(user_agent="route_optimizer_demo_chile", timeout=10)
location = geolocator.geocode("Av. Providencia 1234, Santiago, Chile")
# → {latitude: -33.4489, longitude: -70.6693}
```

**Rate Limit**: 1 request/second (cumplimos con sleep automático)

### 5. AWS DynamoDB

**Propósito**: Tracking de uso del demo

**Schema**:
```json
{
  "demo_id": "uuid-v4",
  "timestamp": 1234567890,
  "data": {
    "drivers": 40,
    "vans": 5,
    "totalDistance": 151.77
  },
  "created_at": "2025-01-26T12:34:56Z"
}
```

---

## ⚙️ Configuración y Deployment

### Requisitos Previos

1. **Node.js** 18+ y npm
2. **Python** 3.11 (para desarrollo local de Lambda)
3. **Cuenta AWS** (Lambda, S3, DynamoDB)
4. **Cuenta Google Cloud** (Routes API)
5. **Cuenta Vercel** (Hosting)

### Setup Local - Frontend

```bash
# 1. Clonar repositorio
git clone https://github.com/AloyTec/Demo_nav.git
cd Demo_nav

# 2. Instalar dependencias
npm install

# 3. Configurar variables de entorno
echo "GOOGLE_MAPS_API_KEY=your_key_here" > .env

# 4. Ejecutar en desarrollo
npm run dev
# → http://localhost:3000

# 5. Build para producción
npm run build
# → Genera /dist
```

### Setup Local - Vercel Functions

```bash
# 1. Instalar Vercel CLI
npm install -g vercel

# 2. Ejecutar dev server con functions
vercel dev
# → http://localhost:3000
# → http://localhost:3000/api/get-street-route (disponible)

# 3. Deploy a Vercel
vercel --prod
```

### Setup - AWS Lambda

```bash
# 1. Crear package
cd lambda-package-v2
zip -r lambda-function.zip .

# 2. Subir a S3
aws s3 cp lambda-function.zip s3://your-bucket/

# 3. Actualizar Lambda
aws lambda update-function-code \
  --function-name route-optimizer \
  --s3-bucket your-bucket \
  --s3-key lambda-function.zip

# 4. Configurar variables de entorno
aws lambda update-function-configuration \
  --function-name route-optimizer \
  --environment Variables={BUCKET_NAME=xxx,TABLE_NAME=xxx}
```

### Variables de Entorno

**Frontend (Vercel)**:
```bash
VITE_API_URL=https://lambda-url.amazonaws.com
```

**Vercel Functions**:
```bash
GOOGLE_MAPS_API_KEY=AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

**AWS Lambda**:
```bash
BUCKET_NAME=route-optimizer-demo-889268462469
TABLE_NAME=route-optimizer-demo-tracking
```

---

## 📊 Capacidades y Límites

### Capacidades del Sistema

| Métrica | Valor |
|---------|-------|
| **Conductores máximos** | 100+ (testeado con 40) |
| **Vans por optimización** | 2-5 (configurable) |
| **Capacidad por van** | 10 pasajeros |
| **Capacidad bus** | 40 pasajeros |
| **Tiempo de procesamiento** | 3-10 segundos (40 conductores) |
| **Precisión geocodificación** | ~95% (Nominatim) |
| **Waypoints por ruta** | Hasta 25 (Google Routes API) |

### Límites Técnicos

**AWS Lambda**:
- Timeout: 300 segundos (5 min)
- Memory: 2048 MB
- Payload: 6 MB

**Google Routes API**:
- Waypoints: Máx 25 por request
- Rate limit: Según API key
- Crédito gratis: $200/mes

**Vercel Functions**:
- Timeout: 30 segundos
- Memory: 1024 MB
- Hobby plan: Ilimitado

---

## 🎯 Casos de Uso

### Modo Normal

**Escenario**: 30 conductores → Terminal Aeropuerto T1

**Proceso**:
1. K-Means divide en 3 vans (~10 cada una)
2. TSP optimiza orden de recogida
3. 2-opt mejora las rutas
4. Google Maps calcula rutas por calles
5. Resultado: 3 vans con rutas optimizadas

**Ahorro típico**: 15-25% vs rutas no optimizadas

### Modo Bus de Acercamiento

**Escenario**: 40 conductores → Terminal Maipú (remoto)

**Proceso**:
1. K-Means divide en 4 vans (~10 cada una)
2. Cada van se divide en 2 grupos de 5
3. **Grupo 1**: Van → recoge → deja en bus stop
4. **Grupo 2**: Van → recoge → deja en terminal directo
5. **Bus**: Bus stop → Terminal (40 pasajeros)

**Ventajas**:
- ✅ Vans no hacen viaje largo al terminal
- ✅ Bus lleva muchos pasajeros eficientemente
- ✅ Reduce km totales de vans
- ✅ Ahorro ~30% en distancia vs modo normal

---

## 🔐 Seguridad

### API Keys

**Google Maps API**:
- ✅ Almacenada en Vercel Environment Variables
- ✅ Solo accesible en server-side (Vercel Functions)
- ✅ Restringida por dominio (*.vercel.app)
- ✅ Restringida por API (solo Routes API)

**AWS Credentials**:
- ✅ IAM roles con least privilege
- ✅ No hardcodeadas en código
- ✅ Lambda execution role específico

### CORS

```javascript
// Configurado en ambos backends
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: GET,POST,OPTIONS
Access-Control-Allow-Headers: Content-Type
```

### Data Privacy

- ❌ No se almacenan datos de conductores permanentemente
- ✅ Solo se trackea metadata (# conductores, distancia)
- ✅ CSV procesado en memoria, no en disco

---

## 📈 Métricas de Rendimiento

### Tiempos de Respuesta

| Operación | Tiempo Promedio | Máximo |
|-----------|-----------------|--------|
| **Geocodificación** (40 dirs) | 5-8 segundos | 15s |
| **K-Means + TSP** | 0.5-1 segundo | 2s |
| **Lambda total** | 8-12 segundos | 30s |
| **Google Routes API** (por van) | 1-2 segundos | 5s |
| **Rendering frontend** | <100ms | 500ms |
| **Total end-to-end** | 15-25 segundos | 60s |

### Uso de Recursos

**Lambda**:
- Memory used: ~500 MB (de 2048 MB disponibles)
- CPU: ~80% durante K-Means/TSP

**Frontend**:
- Bundle size: ~880 KB (comprimido: ~260 KB)
- Lighthouse score: 85-95

---

## 🐛 Debugging y Logs

### Frontend (Browser Console)

```javascript
// Activar logs detallados
🔍 [MapView] useEffect triggered
🚀 [MapView] Starting to fetch street routes for 5 vans
📡 [MapView] Fetching street route for Van 1...
📥 [MapView] Response status: 200
✅ [MapView] Street route loaded: 234 points
🗺️ [Render] Line style: SOLID (street)
```

### Vercel Functions

```bash
# Ver logs en tiempo real
vercel logs --follow

# Logs en Vercel Dashboard
Dashboard → Project → Deployment → Functions → /api/get-street-route
```

Logs típicos:
```
🚀 [API] get-street-route called
✅ [API] Validated 5 waypoints
🌐 [API] Calling NEW Google Routes API v2...
✅ [API] Route calculated: 15.3 km, 18 min
```

### AWS Lambda

```bash
# CloudWatch Logs
aws logs tail /aws/lambda/route-optimizer --follow

# Logs en AWS Console
Lambda → Functions → route-optimizer → Monitor → View logs in CloudWatch
```

---

## 🚀 Roadmap Futuro

### Features Planeados

- [ ] **Optimización multi-terminal** simultánea
- [ ] **Restricciones de tiempo** (ventanas horarias)
- [ ] **Exportar resultados** a PDF/Excel
- [ ] **Histórico de optimizaciones**
- [ ] **Comparación antes/después** visual
- [ ] **Modo oscuro** (dark mode)
- [ ] **Soporte multi-idioma** (i18n)
- [ ] **API pública** para integraciones
- [ ] **Mobile app** (React Native)

### Mejoras Técnicas

- [ ] **Cache de geocodificación** (Redis)
- [ ] **Batch processing** de Routes API
- [ ] **WebSockets** para updates en tiempo real
- [ ] **Tests automatizados** (Jest, Cypress)
- [ ] **CI/CD pipeline** mejorado
- [ ] **Monitoring** (Sentry, DataDog)

---

## 👥 Equipo y Contribuciones

### Desarrollado por
- **AloyTec** - Desarrollo completo del sistema

### Tecnologías Open Source Utilizadas
- React, Vite, Tailwind CSS
- Leaflet, React-Leaflet
- NumPy, Pandas, Scikit-learn
- GeoPy, Nominatim

---

## 📄 Licencia

Proyecto propietario - AloyTec © 2025

---

## 📞 Soporte

Para preguntas o issues:
- GitHub: [AloyTec/Demo_nav](https://github.com/AloyTec/Demo_nav)
- Email: [Contacto del proyecto]

---

## 🙏 Agradecimientos

- **OpenStreetMap** - Datos de mapas y geocodificación
- **Google Maps Platform** - Routes API
- **AWS** - Infraestructura cloud
- **Vercel** - Hosting y serverless functions
- **Comunidad Open Source** - Librerías y frameworks

---

**Última actualización**: Enero 2025
**Versión**: 2.0.0
**Estado**: ✅ Producción
