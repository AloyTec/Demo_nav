# Google Maps Integration - Setup Guide

Esta rama implementa rutas optimizadas por calles usando Google Maps Directions API a través de Vercel Serverless Functions.

## 🎯 Qué hace esto?

- **Antes**: Las rutas se mostraban como líneas rectas entre puntos
- **Ahora**: Las rutas siguen las calles reales usando Google Maps Directions API
- **Implementación**: Vercel Serverless Functions (API key segura en servidor)

## 🔧 Setup

### 1. Obtener Google Maps API Key

1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Crea un nuevo proyecto o selecciona uno existente
3. Habilita la **Routes API** (la nueva API, no la vieja Directions API):
   - Ve a "APIs & Services" > "Library"
   - Busca "Routes API" (no "Directions API")
   - Click en "Enable"
   - **IMPORTANTE**: Debe ser "Routes API", no "Directions API" (legacy)
4. Crea una API key:
   - Ve a "APIs & Services" > "Credentials"
   - Click "Create Credentials" > "API Key"
   - **IMPORTANTE**: Restringe la API key:
     - Application restrictions: HTTP referrers
     - Website restrictions:
       - `https://demonav-pi.vercel.app/*`
       - `https://*.vercel.app/*`
       - `http://localhost:3000/*` (para desarrollo local)
     - API restrictions: Solo "Routes API"

### 2. Configurar Variables de Entorno

#### Desarrollo Local:

```bash
# Crea un archivo .env en la raíz del proyecto
echo "GOOGLE_MAPS_API_KEY=tu_api_key_aquí" > .env
```

#### Producción (Vercel):

1. Ve a tu proyecto en [Vercel Dashboard](https://vercel.com/dashboard)
2. Settings > Environment Variables
3. Agrega:
   - Name: `GOOGLE_MAPS_API_KEY`
   - Value: Tu API key de Google Maps
   - Environment: Production, Preview, Development

### 3. Probar Localmente

```bash
# Instalar Vercel CLI si no lo tienes
npm install -g vercel

# Ejecutar en modo desarrollo (esto inicia Vercel Dev que simula el ambiente de producción)
vercel dev

# La app estará en http://localhost:3000
# Las funciones serverless estarán en http://localhost:3000/api/get-street-route
```

### 4. Deploy a Vercel

```bash
# Commit y push de cambios
git add .
git commit -m "Add Google Maps street routing integration"
git push origin claude/google-maps-integration-012CEaJaXA5wN8pDUeaBTFTy

# Vercel detectará automáticamente la nueva rama y creará un preview deployment
```

## 📁 Archivos Creados/Modificados

### Nuevos Archivos:
- `api/get-street-route.js` - Serverless function que llama a Google Maps API
- `.env.example` - Template de variables de entorno
- `GOOGLE_MAPS_SETUP.md` - Este archivo

### Archivos Modificados:
- `src/components/MapView.jsx` - Ahora llama a la función serverless y muestra rutas por calles
- `vercel.json` - Configuración de funciones serverless
- `package.json` - Agregado `vercel` CLI para desarrollo

## 💰 Costos Estimados

### Google Maps Directions API:
- **Gratis**: $200/mes de crédito
- **Basic tier**: $5 por 1,000 requests (hasta 10 waypoints)
- **Advanced tier**: $10 por 1,000 requests (11-25 waypoints)

### Para este demo:
- ~4-5 vans por optimización = 4-5 API calls
- Costo por optimización: ~$0.04-0.05 USD
- Con $200 gratis: **~4,000 optimizaciones gratis/mes**

## 🎨 Cambios Visuales

### Indicador de Carga:
- Mientras se cargan las rutas: "Cargando rutas..." con spinner
- Cuando terminan: "✓ Rutas optimizadas" en verde

### Rutas:
- **Líneas rectas** (sin Google Maps): Línea punteada, más delgada
- **Rutas por calles** (con Google Maps): Línea sólida, más gruesa

## 🔍 Debugging

### Logs en Browser:
```javascript
// Abre la consola del navegador (F12)
// Verás logs como:
// "Fetching street route for Van 1..."
// "✓ Street route loaded for Van 1: 15.3 km"
```

### Logs en Vercel:
1. Ve a tu proyecto en Vercel Dashboard
2. Click en el deployment
3. "Functions" tab
4. Click en `/api/get-street-route`
5. Verás los logs de cada llamada

## ❌ Troubleshooting

### Error: "API key missing"
- Verifica que `GOOGLE_MAPS_API_KEY` esté configurada en Vercel
- Redeploy el proyecto después de agregar la variable

### Error: "REQUEST_DENIED"
- Verifica que Directions API esté habilitada en Google Cloud
- Verifica las restricciones de la API key

### Las rutas siguen siendo líneas rectas
- Abre la consola del navegador y busca errores
- Verifica que la función `/api/get-street-route` esté respondiendo
- Fallback automático: Si falla Google Maps, usa las rutas originales

## 🚀 Próximos Pasos

1. ✅ Implementación básica funcionando
2. 🔄 Testing con archivo de 40 conductores
3. 📊 Monitoreo de costos en Google Cloud Console
4. 🎯 Optimizaciones adicionales (cache, batch requests, etc.)

## 📚 Referencias

- [Vercel Functions Documentation](https://vercel.com/docs/functions)
- [Google Maps Directions API](https://developers.google.com/maps/documentation/directions)
- [Vercel Environment Variables](https://vercel.com/docs/projects/environment-variables)
