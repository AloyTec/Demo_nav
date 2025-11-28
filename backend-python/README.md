# 🐍 Route Optimizer Backend - Python

Backend local para desarrollo rápido del Route Optimizer API usando **uv** (gestor de paquetes ultra-rápido).

---

## 🚀 Quick Start con UV

### 1. Instalar UV

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# O con pip
pip install uv
```

### 2. Setup del Proyecto

```bash
# Ir al directorio backend-python
cd backend-python

# Crear virtual environment y instalar dependencias
uv venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias (¡ULTRA RÁPIDO!)
uv pip install -e ".[dev]"
```

### 3. Configurar Variables de Entorno

```bash
# Copiar el archivo de ejemplo
cp .env.example .env

# Editar .env y agregar tu Google Maps API Key
nano .env  # o tu editor preferido
```

### 4. Correr el Servidor

```bash
# Opción 1: Usando Python directamente
python app.py

# Opción 2: Usando UV (recomendado)
uv run python app.py

# Opción 3: Usando el script helper
chmod +x run_local.sh
./run_local.sh
```

El servidor estará corriendo en: **http://localhost:8000**

---

## 📁 Estructura del Proyecto

```
backend-python/
├── lambda_function.py       # Lógica principal (mismo código que Lambda)
├── app.py                   # Servidor Flask para desarrollo local
├── pyproject.toml           # Configuración del proyecto y dependencias
├── .env.example             # Template de variables de entorno
├── .env                     # Variables de entorno (no committed)
├── run_local.sh             # Script helper para correr
└── README.md                # Esta documentación
```

---

## 🔧 Desarrollo con UV

### ¿Por qué UV?

- ⚡ **10-100x más rápido** que pip
- 🔒 **Lock files** automáticos para reproducibilidad
- 🎯 **Resolución de dependencias** inteligente
- 🌐 **Compatible** con pip y PyPI

### Comandos Útiles

```bash
# Instalar dependencias de desarrollo
uv pip install -e ".[dev]"

# Agregar una nueva dependencia
uv pip install nombre-paquete
# Luego actualizar pyproject.toml manualmente

# Actualizar todas las dependencias
uv pip install --upgrade -e ".[dev]"

# Correr tests (cuando existan)
uv run pytest

# Formatear código
uv run black .

# Linter
uv run ruff check .
```

---

## 🌐 API Endpoints

### GET `/`
Información del servidor

### GET `/api/health`
Health check

**Response:**
```json
{
  "status": "ok",
  "message": "Route Optimizer Lambda is running"
}
```

### POST `/api/upload`
Subir archivo Excel/CSV con datos de conductores

**Request:**
```json
{
  "filename": "drivers.xlsx",
  "file_content": "base64_encoded_file_content"
}
```

**Response:**
```json
{
  "drivers": [...],
  "count": 42,
  "message": "Archivo procesado exitosamente"
}
```

### POST `/api/optimize`
Optimizar rutas

**Request:**
```json
{
  "drivers": [
    {
      "name": "Juan Pérez",
      "address": "Av. Libertador 1234, Santiago",
      "terminal": "Terminal Aeropuerto T1",
      "time": "08:00"
    }
  ],
  "config": {
    "numVans": 10,
    "safetyMargin": 0.20
  }
}
```

**Response:**
```json
{
  "vans": [...],
  "totalDrivers": 42,
  "totalDistance": 325.5,
  "distanceSavedPercent": 15.2,
  "success": true
}
```

---

## 🧪 Testing Local

### Con curl:

```bash
# Health check
curl http://localhost:8000/api/health

# Test upload (necesitas un archivo base64)
curl -X POST http://localhost:8000/api/upload \
  -H "Content-Type: application/json" \
  -d @test_upload.json

# Test optimize
curl -X POST http://localhost:8000/api/optimize \
  -H "Content-Type: application/json" \
  -d @test_optimize.json
```

### Con el Frontend:

```bash
# En otra terminal, correr el frontend
cd ..  # volver a la raíz
npm install
npm run dev

# El frontend en http://localhost:5173 se conectará al backend en :8000
```

---

## 🔍 Debugging

### Logs Detallados

El servidor Flask imprime logs detallados en la consola:

```
Geocoding 1: Av. Libertador 1234, Santiago
  ✓ Geocoded: Avenida Libertador Bernardo O'Higgins 1234, Santiago, Chile
  ✓ Real route: 15.3 km, 22.5 min (from Distance Matrix API)
```

### Variables de Entorno

```bash
# Ver todas las variables configuradas
cat .env

# Verificar que Google Maps API esté configurada
echo $GOOGLE_MAPS_API_KEY
```

### Errores Comunes

**Error: "GOOGLE_MAPS_API_KEY not configured"**
- Solución: Agregar API key en `.env`

**Error: "ModuleNotFoundError: No module named 'flask'"**
- Solución: `uv pip install -e ".[dev]"`

**Error: "Port 8000 already in use"**
- Solución: Cambiar `PORT=8001` en `.env`

---

## 📊 Comparación: UV vs pip

| Acción | pip | uv | Mejora |
|--------|-----|-----|--------|
| Instalar pandas | ~15s | ~1s | **15x** |
| Instalar todas deps | ~120s | ~5s | **24x** |
| Resolver conflictos | ~30s | ~0.5s | **60x** |
| Actualizar paquetes | ~45s | ~2s | **22x** |

---

## 🚢 Deploy a Lambda

Cuando estés listo para deployar:

```bash
# Volver al directorio raíz
cd ..

# Usar Docker deployment
./deploy_docker_lambda.sh

# O seguir instrucciones en DOCKER_DEPLOYMENT.md
```

---

## 📚 Recursos

- [UV Documentation](https://github.com/astral-sh/uv)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Google Maps API](https://developers.google.com/maps)
- [OR-Tools](https://developers.google.com/optimization)

---

## 🆘 Ayuda

Si tienes problemas:
1. Verifica que `.env` esté configurado correctamente
2. Asegúrate que el virtual environment esté activado
3. Revisa los logs en la consola
4. Consulta la documentación de UV

---

## ✅ Checklist de Setup

- [ ] UV instalado
- [ ] Virtual environment creado
- [ ] Dependencias instaladas con `uv pip install -e ".[dev]"`
- [ ] Archivo `.env` creado y configurado
- [ ] Google Maps API Key agregada
- [ ] Servidor corriendo en `localhost:8000`
- [ ] Health check funcionando
- [ ] Frontend conectado (opcional)
