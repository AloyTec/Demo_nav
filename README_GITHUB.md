# 🚐 Route Optimizer Demo

Sistema inteligente de optimización de rutas para transporte de conductores utilizando algoritmos de Machine Learning (K-Means clustering + TSP).

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![React](https://img.shields.io/badge/react-18.0+-61dafb.svg)

## 📋 Descripción

Aplicación web full-stack diseñada para optimizar rutas de transporte de conductores hacia terminales de buses. Reduce costos operativos, tiempo de viaje y mejora la eficiencia logística mediante inteligencia artificial.

### ✨ Características Principales

- 📊 **Carga de Datos**: Importación de archivos CSV con información de conductores
- 🤖 **Optimización IA**: Algoritmos K-Means + TSP para agrupar y optimizar rutas
- 🗺️ **Visualización Interactiva**: Mapa con Leaflet/OpenStreetMap mostrando rutas optimizadas
- 📈 **Dashboard de KPIs**: Métricas en tiempo real (ahorro de km, tiempo, costos)
- ✏️ **Editor Manual**: Ajuste de rutas mediante drag & drop
- 🎨 **Interfaz Moderna**: Diseño profesional con Tailwind CSS

## 🏗️ Arquitectura

### Frontend
- **React 18** + **Vite**
- **Tailwind CSS** para estilos
- **Leaflet** para mapas interactivos
- **Recharts** para gráficos y métricas
- **react-beautiful-dnd** para drag & drop

### Backend
- **AWS Lambda** (Python 3.11+) - Serverless compute
- **Scikit-learn** para clustering K-Means
- **Google Maps API** para geocodificación y rutas
- **Pandas** para procesamiento de datos
- **NumPy** para cálculos numéricos
- **DynamoDB** para tracking de uso

## 🚀 Instalación y Configuración

### Prerrequisitos

- Node.js 16+ y npm
- Python 3.9+
- Git

### 1. Clonar el Repositorio

```bash
git clone https://github.com/TU_USUARIO/route-optimizer-demo.git
cd route-optimizer-demo
```

### 2. Configurar Backend (Python)

```bash
cd backend
pip install -r requirements.txt
cd ..
```

### 3. Configurar Frontend (React)

```bash
npm install
```

### 4. Iniciar la Aplicación

**Configurar variables de entorno:**
```bash
# Crear archivo .env en la raíz
VITE_API_URL=https://your-lambda-url.lambda-url.us-east-1.on.aws
```

**Iniciar Frontend:**
```bash
npm run dev
```
El frontend estará disponible en `http://localhost:3000`

**Backend (AWS Lambda):**
El backend ya está desplegado en AWS Lambda. Ver `DEPLOY_INSTRUCTIONS.md` para actualizar.

### 5. Abrir en el Navegador

Visita [http://localhost:3000](http://localhost:3000)

## 📊 Uso del Sistema

### Paso 1: Preparar Archivo CSV

El archivo debe tener las siguientes columnas:

| Código | Nombre | Dirección Casa | Terminal Destino | Hora Presentación |
|--------|--------|----------------|------------------|-------------------|
| SC001 | Juan Pérez | Av. Principal 123 | Terminal T1 | 06:00 |

**Ejemplos incluidos:**
- `data/conductores_completo.csv` - 30 conductores (Ciudad de México)
- `data/conductores_santiago_chile.csv` - 40 conductores (Santiago de Chile)
- `data/conductores_50.csv` - 50 conductores
- `data/conductores_pequeno.csv` - 10 conductores

### Paso 2: Cargar Datos

1. Haz clic en **"Carga de Datos"**
2. Arrastra el archivo CSV o usa el botón "Seleccionar Archivo"
3. Espera a que se procesen los datos

### Paso 3: Ver Resultados

- **Mapa de Rutas**: Visualiza las rutas optimizadas con diferentes colores
- **KPIs y Métricas**: Revisa ahorro de km, tiempo y costos
- **Editor Manual**: Ajusta conductores entre vans arrastrando tarjetas

## 🧮 Algoritmos Utilizados

### K-Means Clustering
Agrupa conductores geográficamente según:
- Proximidad de direcciones de origen
- Terminal de destino común
- Capacidad de vehículos (8 conductores/van)

### TSP Greedy (Traveling Salesman Problem)
Optimiza el orden de recogida dentro de cada ruta para minimizar distancia total.

### Geocodificación
Convierte direcciones de texto a coordenadas GPS usando Google Maps Geocoding API (paralelo con 10 workers).

## 📁 Estructura del Proyecto

```
route-optimizer-demo/
├── lambda_function_updated.py # AWS Lambda Handler + Algoritmos IA
├── api/
│   └── get-street-route.js    # Vercel Function (Google Routes API)
├── src/
│   ├── components/
│   │   ├── Dashboard.jsx      # Vista principal
│   │   ├── FileUpload.jsx     # Carga de archivos
│   │   ├── MapView.jsx        # Mapa interactivo
│   │   ├── KPIDashboard.jsx   # Métricas y gráficos
│   │   └── RouteEditor.jsx    # Editor drag & drop
│   ├── App.jsx                # Componente raíz
│   └── main.jsx              # Entry point
├── data/
│   ├── conductores_completo.csv
│   ├── conductores_santiago_chile.csv
│   └── ...
├── package.json
├── vite.config.js
└── README.md
```

## 🔧 API Endpoints

### `POST /api/upload`
Carga y geocodifica datos de conductores.

**Request:**
```json
{
  "data": [...] // Array de objetos conductor
}
```

**Response:**
```json
{
  "success": true,
  "message": "Datos procesados correctamente",
  "data": { /* datos con coordenadas */ }
}
```

### `POST /api/optimize`
Optimiza rutas usando K-Means + TSP.

**Response:**
```json
{
  "success": true,
  "vans": [...], // Rutas optimizadas
  "metrics": { /* KPIs */ }
}
```

### `GET /api/health`
Health check del servidor.

## 📈 KPIs Disponibles

- **Número de Vans**: Vehículos necesarios
- **Total de Conductores**: Personas transportadas
- **Distancia Total**: Kilómetros recorridos
- **Tiempo Estimado**: Duración del recorrido
- **Ahorro vs. Individual**: Comparación con transporte individual
- **Costo Estimado**: Gastos de combustible

## 🎯 Casos de Uso

1. **Empresas de Transporte**: Optimización de rutas de personal
2. **Terminales de Buses**: Coordinación de llegada de conductores
3. **Compañías de Logística**: Planificación de recogidas
4. **Propuestas Comerciales**: Demo para clientes potenciales

## 🛠️ Tecnologías

| Categoría | Tecnología |
|-----------|-----------|
| Frontend | React, Vite, Tailwind CSS |
| Mapas | Leaflet, OpenStreetMap |
| Gráficos | Recharts |
| Backend | AWS Lambda (Python 3.11) |
| ML/IA | Scikit-learn (K-Means, TSP, 2-opt) |
| APIs | Google Maps (Geocoding & Routes API) |
| Cloud | AWS (Lambda, S3, DynamoDB), Vercel |
| Data Processing | Pandas, NumPy |

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para más detalles.

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:

1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para preguntas o soporte, abre un issue en GitHub.

## 🗺️ Roadmap

- [ ] Autenticación de usuarios
- [ ] Exportación de rutas a PDF/Excel
- [ ] Integración con Google Maps
- [ ] Optimización en tiempo real
- [ ] Historial de optimizaciones
- [ ] API REST completa con documentación Swagger
- [ ] Modo offline con Service Workers
- [ ] Notificaciones push para conductores

---

**Desarrollado con ❤️ para optimizar rutas y mejorar la eficiencia logística**
