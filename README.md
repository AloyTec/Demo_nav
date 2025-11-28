# 🚀 Sistema de Optimización de Rutas

## Prototipo Demo - Propuesta Técnica

Sistema inteligente para optimizar rutas de transporte de conductores usando algoritmos de Machine Learning e Inteligencia Artificial.

---

## 📋 Características Principales

### ✅ **Procesamiento Automático**
- Carga de archivos Excel/CSV mediante drag & drop
- Validación automática de datos
- Geocodificación de direcciones
- Procesamiento en < 2 minutos

### ✅ **Motor de Optimización IA**
- Algoritmo de clustering (K-Means)
- Optimización de rutas (TSP)
- Balanceo automático de carga
- Minimización de distancias

### ✅ **Visualización Interactiva**
- Mapa con rutas coloreadas por van
- Marcadores numerados por orden de recogida
- Tooltips informativos
- Vista de satélite disponible

### ✅ **Dashboard de KPIs**
- Métricas en tiempo real
- Gráficos comparativos
- Análisis de eficiencia
- Reportes visuales

### ✅ **Editor Manual**
- Drag & drop para reasignar conductores
- Recálculo automático de rutas
- Historial de cambios
- Validación en tiempo real

---

## 🛠️ Stack Tecnológico

### Frontend
- **React 18** - Framework UI moderno
- **Vite** - Build tool ultrarrápido
- **Tailwind CSS** - Styling utility-first
- **Leaflet** - Mapas interactivos
- **Recharts** - Gráficos y visualizaciones
- **Axios** - Cliente HTTP

### Backend
- **AWS Lambda** - Serverless compute (Python 3.11+)
- **Pandas** - Procesamiento de datos
- **Scikit-learn** - Algoritmos ML (K-Means clustering)
- **Google Maps API** - Geocodificación y rutas
- **NumPy** - Cálculos numéricos
- **DynamoDB** - Tracking de uso

---

## 🚀 Instalación y Ejecución

### Prerequisitos
- Node.js 18+
- npm o yarn
- Cuenta AWS (para el backend Lambda)
- Google Maps API Key

### 1. Instalar dependencias del Frontend

```bash
npm install
```

### 2. Configurar Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```bash
VITE_API_URL=https://your-lambda-url.lambda-url.us-east-1.on.aws
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
```

### 3. Ejecutar el Frontend (Puerto 3000)

```bash
npm run dev
```

Abre tu navegador en: **http://localhost:3000**

### 4. Backend (AWS Lambda)

El backend está desplegado en AWS Lambda. Para actualizar:

```bash
# Ver DEPLOY_INSTRUCTIONS.md para instrucciones completas
aws lambda update-function-code \
  --function-name route-optimizer-lambda \
  --zip-file fileb://lambda-function-updated.zip \
  --region us-east-1
```

---

## 📊 Uso del Sistema

### Paso 1: Cargar Datos
1. Arrastra un archivo Excel o haz clic en "Seleccionar Archivo"
2. El sistema validará y geocodificará automáticamente
3. El algoritmo optimizará las rutas

### Paso 2: Visualizar Rutas
- Ve al tab "Mapa de Rutas"
- Explora las rutas coloreadas
- Haz clic en los marcadores para ver detalles
- Revisa la leyenda con métricas por van

### Paso 3: Analizar KPIs
- Ve al tab "KPIs y Métricas"
- Revisa gráficos de distribución
- Compara optimización vs manual
- Analiza reducción de distancias

### Paso 4: Editar Manualmente (Opcional)
- Ve al tab "Editor Manual"
- Arrastra conductores entre vans
- Observa el recálculo automático
- Revisa el historial de cambios

---

## 📁 Formato del Archivo Excel

El archivo debe contener las siguientes columnas:

| Columna | Descripción | Requerido |
|---------|-------------|-----------|
| `Nombre` | Nombre del conductor | ✅ Sí |
| `Dirección` | Dirección completa | ✅ Sí |
| `Terminal` | Terminal de destino | ⚪ Opcional |
| `Hora` | Hora de recogida | ⚪ Opcional |

### Ejemplo:

```
Nombre,Dirección,Terminal,Hora
Juan Pérez,Av. Insurgentes Sur 1234,Terminal A,08:00
María González,Calle Reforma 567,Terminal A,08:00
```

Un archivo de ejemplo está disponible en: `data/ejemplo_conductores.csv`

---

## 🎯 Resultados Esperados

### ✅ Optimización Matemática Demostrable
- Clustering óptimo usando K-Means
- Rutas optimizadas con algoritmo TSP
- Balanceo perfecto de carga

### ✅ Reducción de Costos
- **10-15% menos kilómetros** recorridos
- Menor consumo de combustible
- Menor tiempo de operación

### ✅ Balance Perfecto
- Distribución equitativa entre vans
- Capacidad óptima utilizada
- Sin sobrecarga de vehículos

---

## 🧪 Algoritmos Utilizados

### 1. K-Means Clustering
```python
# Agrupa conductores geográficamente
kmeans = KMeans(n_clusters=num_vans, random_state=42)
labels = kmeans.fit_predict(coordinates)
```

### 2. TSP Greedy (Traveling Salesman Problem)
```python
# Optimiza el orden de recogida
def optimize_route_tsp(drivers):
    route = [drivers[0]]
    while remaining:
        nearest = min(remaining, key=distance_func)
        route.append(nearest)
    return route
```

### 3. Load Balancing
```python
# Balancea la carga entre vans
def balance_load(clusters):
    while max(sizes) - min(sizes) > 1:
        move_driver(largest, smallest)
```

---

## 📈 Módulos del Sistema

### MÓDULO 1: Procesamiento de Datos
- ✅ Carga automática de Excel
- ✅ Validación de formato
- ✅ Geocodificación de direcciones
- ✅ Normalización de datos

### MÓDULO 2: Motor de Optimización (IA)
- ✅ Algoritmo de clustering
- ✅ Minimización de distancias
- ✅ Aplicación de restricciones
- ✅ Balanceo automático

### MÓDULO 3: Visualización y Control
- ✅ Mapa interactivo
- ✅ Editor manual
- ✅ Gestión de recursos
- ✅ Recálculo dinámico

### MÓDULO 4: Dashboard & Reportes
- ✅ KPIs en tiempo real
- ✅ Gráficos comparativos
- ✅ Análisis de tendencias
- ✅ Métricas de eficiencia

---

## 🎨 Capturas del Sistema

### Dashboard Principal
- Interfaz de carga drag & drop
- Validación en tiempo real
- Procesamiento automático

### Mapa de Rutas
- Rutas coloreadas por van
- Marcadores numerados
- Tooltips informativos
- Leyenda con métricas

### KPIs y Métricas
- Gráficos de distribución
- Comparativa manual vs optimizado
- Métricas de eficiencia
- Resumen ejecutivo

### Editor Manual
- Drag & drop de conductores
- Historial de cambios
- Recálculo automático
- Validación de restricciones

---

## 🔧 Configuración Avanzada

### Ajustar número de vans
En `lambda_function_updated.py`, línea 479:
```python
num_vans = max(2, min(5, len(drivers) // 10 + 1))
```

### Ajustar capacidad de vans
En `lambda_function_updated.py`, línea 31:
```python
VAN_CAPACITY = 10  # Capacidad máxima por van
BUS_CAPACITY = 40  # Capacidad del bus de acercamiento
```

### Cambiar centro del mapa
En `src/components/MapView.jsx`, línea 18:
```javascript
const [center, setCenter] = useState([19.4326, -99.1332]); // CDMX
```

---

## 📝 Notas Técnicas

### Geocodificación
- Utiliza Google Maps Geocoding API (production)
- Geocodificación en paralelo con ThreadPoolExecutor (10 workers)
- Múltiples estrategias de fallback para direcciones ambiguas
- Coordenadas conocidas predefinidas para terminales comunes

### Optimización
- Tiempo promedio: < 2 minutos
- Escala hasta 100+ conductores
- Puede ajustarse número de vans automáticamente

### Mapas
- Proveedor: OpenStreetMap
- Sin costo de uso
- Alternativamente puede usar Google Maps API

---

## 🚀 Próximos Pasos (Versión Completa)

- [ ] Autenticación de usuarios
- [ ] Base de datos persistente
- [ ] Exportación de reportes PDF
- [ ] Integración con Google Maps API
- [ ] Notificaciones en tiempo real
- [ ] App móvil para conductores
- [ ] Historial de rutas
- [ ] Análisis predictivo con ML

---

## 📞 Soporte

Para dudas o demo personalizada:
- 📧 Email: contacto@routeoptimizer.com
- 📱 WhatsApp: +52 55 1234 5678

---

## 📄 Licencia

Prototipo demo para propuesta técnica.
© 2025 Route Optimizer. Todos los derechos reservados.

---

**¡Gracias por considerar nuestra propuesta!** 🎉
