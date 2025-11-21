# 📊 GUÍA DE ARCHIVOS EXCEL PARA EL DEMO

## 📁 Archivos Disponibles

Tienes **3 archivos CSV** listos para usar en el demo:

### 1. `conductores_pequeno.csv` - 10 conductores
**📍 Ubicación:** `/tmp/route-optimizer-demo/data/conductores_pequeno.csv`

**Mejor para:**
- ✅ Demo rápido (procesa en ~30 segundos)
- ✅ Primera impresión
- ✅ Explicar el concepto básico

**Contenido:**
- 10 conductores
- Todos van a Terminal Aeropuerto T1
- Mismo horario (06:30)
- 2 vans aproximadamente

---

### 2. `conductores_completo.csv` - 30 conductores ⭐ RECOMENDADO
**📍 Ubicación:** `/tmp/route-optimizer-demo/data/conductores_completo.csv`

**Mejor para:**
- ✅ **DEMO PRINCIPAL** ⭐
- ✅ Mostrar optimización real
- ✅ Ver diferencia entre múltiples vans
- ✅ Mostrar KPIs significativos

**Contenido:**
- 30 conductores
- Divididos entre Terminal T1 y T2
- Diferentes horarios (06:30 a 07:45)
- 4-6 vans optimizadas
- Datos realistas de Ciudad de México

---

### 3. `conductores_50.csv` - 50 conductores
**📍 Ubicación:** `/tmp/route-optimizer-demo/data/conductores_50.csv`

**Mejor para:**
- ✅ Demostrar escalabilidad
- ✅ Mostrar capacidad del sistema
- ✅ Impresionar con volumen

**Contenido:**
- 50 conductores
- Mezcla de terminales
- Horarios escalonados (06:30 a 08:45)
- 8-10 vans optimizadas
- Procesamiento ~2 minutos

---

## 📋 Formato de las Columnas

Todos los archivos incluyen:

| Columna | Descripción | Ejemplo |
|---------|-------------|---------|
| **Código** | ID único del conductor | C001, C002, etc. |
| **Nombre** | Nombre completo | Juan Pérez García |
| **Dirección Casa** | Dirección de recogida | Av. Insurgentes Sur 1234 Col. Del Valle CDMX |
| **Terminal Destino** | Dónde debe llegar | Terminal Aeropuerto T1 |
| **Hora Presentación** | Hora que debe estar en terminal | 06:30, 07:00, etc. |

---

## 🎯 Cómo Usar en el Demo

### Opción 1: Drag & Drop (Recomendado)

1. **Abrir Finder/Explorador:**
   ```
   /tmp/route-optimizer-demo/data/
   ```

2. **Arrastrar el archivo** al área de carga en el navegador

3. **¡Listo!** El sistema procesa automáticamente

### Opción 2: Click para Seleccionar

1. **Click en** "Seleccionar Archivo"

2. **Navegar a:**
   ```
   /tmp/route-optimizer-demo/data/
   ```

3. **Seleccionar** el archivo deseado

4. **Click en** "Abrir"

---

## 🎬 Flujo Recomendado para la Presentación

### PASO 1: Empezar Pequeño (2 min)
**Archivo:** `conductores_pequeno.csv`

**Qué decir:**
> "Empecemos con un ejemplo sencillo de 10 conductores..."

**Mostrar:**
- ✅ Proceso de carga simple
- ✅ Validación automática
- ✅ Geocodificación rápida

---

### PASO 2: Demo Principal (10 min) ⭐
**Archivo:** `conductores_completo.csv`

**Qué decir:**
> "Ahora veamos un escenario real con 30 conductores, 
> múltiples terminales y diferentes horarios..."

**Recorrer:**
1. **Carga de Datos** → Mostrar procesamiento
2. **Mapa de Rutas** → Explicar colores y rutas
3. **KPIs y Métricas** → Mostrar ahorros
4. **Editor Manual** → Drag & drop de un conductor

---

### PASO 3: Impresionar con Volumen (Opcional - 3 min)
**Archivo:** `conductores_50.csv`

**Qué decir:**
> "¿Y si tienen 50 conductores? El sistema escala sin problemas..."

**Enfatizar:**
- ✅ Procesamiento rápido incluso con más datos
- ✅ Optimización sigue siendo efectiva
- ✅ Sistema enterprise-ready

---

## 💡 Tips para la Demo

### ✅ DO's (Hacer)

1. **Usar `conductores_completo.csv` como principal**
   - Muestra mejor el valor
   - Datos más realistas
   - Gráficos más interesantes

2. **Explicar las columnas mientras carga**
   - "Como ven, usamos su Excel actual..."
   - "Código de conductor, nombre, dirección..."
   - "Terminal de destino y hora de presentación"

3. **Destacar la flexibilidad**
   - "Funciona con diferentes horarios"
   - "Múltiples terminales simultáneas"
   - "Datos reales de Ciudad de México"

4. **Pausar en el mapa**
   - Dejar que vean las rutas
   - Explicar los colores
   - Hacer zoom a zonas específicas

### ❌ DON'Ts (Evitar)

1. **No cargar el mismo archivo 2 veces**
   - Refresca la página entre archivos

2. **No apurar el procesamiento**
   - Usa esos segundos para explicar el algoritmo

3. **No ignorar errores de geocodificación**
   - Son normales en demos
   - Explica que en producción se usa Google Maps

---

## 🗺️ Qué Verás en Cada Módulo

### 📍 Mapa de Rutas

**Con `conductores_completo.csv` verás:**
- 4-6 rutas de diferentes colores
- Marcadores numerados (orden de recogida)
- Distribución geográfica inteligente
- Leyenda con info de cada van
- Stats: vans, conductores, km totales

### 📊 KPIs y Métricas

**Gráficos que aparecerán:**
1. **Distribución de Conductores** por van (bar chart)
2. **Proporción de Asignación** (pie chart)
3. **Distancia por Van** (bar chart)
4. **Comparativa Manual vs Optimizado**

**Métricas principales:**
- Total de vans: 4-6
- Total de conductores: 30
- Reducción de KM: ~10-15%
- Tiempo ahorrado: ~15-20 min

### ✏️ Editor Manual

**Podrás:**
- Ver los 30 conductores distribuidos en tarjetas
- Arrastrar conductores entre vans
- Ver recálculo automático de distancias
- Historial de cambios

---

## 📝 Datos de los Archivos

### Direcciones Reales Incluidas

Todos los archivos usan **direcciones reales de CDMX**:
- ✅ Av. Insurgentes Sur
- ✅ Paseo de la Reforma
- ✅ Av. Revolución
- ✅ Av. Universidad
- ✅ Av. Cuauhtémoc
- ✅ Y más...

### Terminales

- **Terminal Aeropuerto T1** - Para vuelos nacionales
- **Terminal Aeropuerto T2** - Para vuelos internacionales

### Horarios

Escalonados cada 15 minutos:
- 06:30 - Primer turno
- 06:45 - Segundo grupo
- 07:00 - Tercer grupo
- ... hasta 08:45

---

## 🎯 Resultados Esperados

### Con `conductores_completo.csv` (30 conductores):

**Sin optimizar (manual):**
- Distancia estimada: ~180 km
- Tiempo estimado: 240 minutos
- Distribución: Desbalanceada

**Con optimización (IA):**
- Distancia optimizada: ~158 km
- Tiempo estimado: 200 minutos
- Distribución: Perfecta
- **Ahorro: 22 km (12%)**

---

## 🚀 Inicio Rápido

```bash
# 1. Asegúrate que los servidores estén corriendo
# Backend: http://localhost:5002
# Frontend: http://localhost:3000

# 2. Abre el navegador en http://localhost:3000

# 3. Arrastra uno de estos archivos:
/tmp/route-optimizer-demo/data/conductores_pequeno.csv      # 10 conductores
/tmp/route-optimizer-demo/data/conductores_completo.csv     # 30 conductores ⭐
/tmp/route-optimizer-demo/data/conductores_50.csv           # 50 conductores

# 4. ¡Disfruta viendo la magia! ✨
```

---

## 📞 Troubleshooting

### ❓ "No encuentra el archivo"
**Solución:** Usa el path completo:
```
/tmp/route-optimizer-demo/data/conductores_completo.csv
```

### ❓ "Error de geocodificación"
**Normal en demos.** Algunas direcciones pueden fallar con OpenStreetMap gratuito.
**Solución:** Menciona que en producción usarán Google Maps API (más preciso).

### ❓ "Tarda mucho en procesar"
**Normal con 50 conductores.** Puede tardar hasta 2 minutos.
**Solución:** Usa el tiempo para explicar los algoritmos de IA.

---

## ✅ Checklist Pre-Demo

- [ ] Backend corriendo (http://localhost:5002)
- [ ] Frontend corriendo (http://localhost:3000)
- [ ] Archivos CSV ubicados
- [ ] Navegador listo
- [ ] Script de presentación revisado
- [ ] Calculadora ROI preparada

---

**¡Ya tienes todo listo para impresionar!** 🚀

**Archivo recomendado:** `conductores_completo.csv` (30 conductores)
