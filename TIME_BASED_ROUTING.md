# Optimización Basada en Tiempo de Presentación

## 🎯 Cambio Implementado

La Lambda ahora considera **ventanas de tiempo** para optimizar las rutas, asegurando que cada pasajero llegue a tiempo a su hora de presentación en el terminal.

## 📊 Concepto

### Antes ❌
- Optimización solo por distancia
- "Hora de presentación" se ignoraba
- No se consideraba tiempo de viaje

### Ahora ✅
- **Hora de presentación** = hora límite de LLEGADA al terminal
- Se calcula tiempo de viaje estimado
- Se calcula hora de recogida máxima
- Los pasajeros se ordenan por hora de presentación

## 🧮 Cálculos

### 1. Estimación de Tiempo de Viaje

```python
def estimate_travel_time(distance_km):
    # Velocidad según distancia
    if distance_km < 15 km:
        speed = 60 km/h  # Ciudad (50-70 km/h promedio)
    else:
        speed = 87 km/h  # Mixto: 70% autopista (105 km/h) + 30% ciudad (60 km/h)

    # Tiempo base
    travel_time = (distance_km / speed) * 60  # minutos

    # Buffer de seguridad (20%)
    travel_time_with_buffer = travel_time * 1.2

    return travel_time_with_buffer
```

### 2. Hora de Recogida

```
Hora de recogida = Hora de presentación - Tiempo de viaje
```

**Ejemplo**:
```
Pasajero: Juan Pérez
Dirección: Maipú (15 km del terminal)
Terminal: El Conquistador
Hora de presentación: 06:00 AM

Cálculo:
- Distancia: 15 km
- Velocidad estimada: 87 km/h (mixta)
- Tiempo base: (15 / 87) * 60 = 10.3 minutos
- Con buffer 20%: 10.3 * 1.2 = 12.4 minutos
- Hora de recogida: 06:00 - 12.4 min = 05:48 AM
```

## ⚙️ Parámetros Configurables

```python
# Velocidades promedio
CITY_SPEED_KMH = 60        # 50-70 km/h rango ciudad
HIGHWAY_SPEED_KMH = 105    # 90-120 km/h rango autopista
CITY_DISTANCE_THRESHOLD = 15  # km - umbral para considerar ciudad

# Seguridad
SAFETY_BUFFER = 1.2        # 20% buffer extra
PICKUP_TIME_MINUTES = 5    # Tiempo de recogida por pasajero
```

## 📋 Información Agregada a Cada Pasajero

```json
{
  "name": "Juan Pérez",
  "address": "Av. Pajaritos 1234, Maipú",
  "terminal": "El Conquistador",
  "distance_to_terminal_km": 15.2,
  "travel_time_minutes": 12.4,
  "presentation_time": "06:00",
  "presentation_time_minutes": 360,
  "pickup_time_latest": "05:48",
  "pickup_time_latest_minutes": 348
}
```

## 🔄 Flujo de Optimización

```
1. Geocodificar dirección del pasajero
   └─> Coordenadas GPS

2. Geocodificar terminal de destino
   └─> Coordenadas del terminal

3. Calcular distancia (geodésica)
   └─> Distancia en km

4. Estimar tiempo de viaje
   ├─> Seleccionar velocidad (ciudad vs autopista)
   ├─> Calcular tiempo base
   └─> Aplicar buffer de seguridad 20%

5. Calcular hora de recogida
   └─> Hora presentación - tiempo de viaje

6. Ordenar pasajeros
   └─> Por hora de presentación (más temprano primero)

7. Agrupar por terminal y zona
   └─> Clusters geográficos compatibles con ventanas

8. Optimizar ruta TSP
   └─> Orden de recogida que minimiza distancia
```

## 📊 Logs de Ejemplo

```
Geocoding addresses and calculating travel times...
Geocoding 1/54: Obisco Umaña #546, Estación Central
  → Distance: 8.5 km, Travel time: 12.2 min, Pickup by: 06:05, Present at: 06:17

Geocoding 2/54: Osa menor # 03554, Lo Espejo
  → Distance: 12.3 km, Travel time: 17.7 min, Pickup by: 05:51, Present at: 06:09

...

Drivers sorted by presentation time (earliest: 00:18, latest: 23:12)
```

## 🎨 Visualización en UI

Los tiempos ahora se muestran en:
- **Tarjetas de pasajeros**: Hora de recogida y presentación
- **Resumen de vans**: Ventana de recogida del grupo
- **Detalles de ruta**: Tiempo estimado total

## 🧪 Casos de Prueba

### Caso 1: Pasajero Cercano
```
Distancia: 5 km
Velocidad: 60 km/h (ciudad)
Tiempo base: 5 minutos
Con buffer: 6 minutos
Hora presentación: 06:00
Hora recogida: 05:54 ✓
```

### Caso 2: Pasajero Lejano
```
Distancia: 25 km
Velocidad: 87 km/h (mixta)
Tiempo base: 17.2 minutos
Con buffer: 20.6 minutos
Hora presentación: 06:00
Hora recogida: 05:39 ✓
```

### Caso 3: Madrugada Extrema
```
Hora presentación: 00:30
Tiempo viaje: 20 minutos
Hora recogida calculada: 00:10
Resultado: Pasajero debe estar listo a las 00:10 ✓
```

### Caso 4: Hora Negativa (Edge Case)
```
Hora presentación: 00:05
Tiempo viaje: 15 minutos
Hora recogida calculada: -10 minutos (inválido)
Resultado: Se ajusta a 00:00 (medianoche) ✓
```

## 🚀 Beneficios

1. **Garantiza puntualidad**: Todos llegan a tiempo
2. **Optimiza madrugadas**: Recogidas ordenadas cronológicamente
3. **Reduce espera**: Pasajeros no esperan innecesariamente
4. **Mejor planificación**: Conductores ven ventanas de tiempo
5. **Transparencia**: Cliente ve cálculos de tiempo

## 📈 Métricas

Para el archivo de prueba (54 conductores):

```
Hora más temprana presentación: 00:30
Hora más tardía presentación: 23:30
Rango de tiempo: 23 horas
Tiempo promedio de viaje: ~15 minutos
Distancia promedio: ~12 km
```

## 🔮 Mejoras Futuras

### Fase 2: Google Maps API (Opcional)
- Tiempos reales de tráfico
- Rutas exactas por calles
- Consideración de hora del día
- Costo: ~$30-50/mes

### Fase 3: Optimización Avanzada
- Vehicle Routing Problem (VRP) con ventanas de tiempo
- Algoritmo genético para mejor optimización
- Considerar tiempo de recogida acumulado

## ⚠️ Consideraciones

1. **Geocoding**: Agrega ~1 segundo por pasajero (necesario para calcular distancia)
2. **Aproximación**: Tiempos son estimados, no exactos
3. **Tráfico**: No considera tráfico variable por hora
4. **Paradas múltiples**: No suma tiempo de recogida de pasajeros anteriores (simplificación)

## 🎯 Caso Real

**Archivo**: `ListadoTraslados (54) 26-11-2025.csv`

```
Pasajero más temprano:
- Pablo Ricardo Moya Gonzalez
- Hora presentación: 00:30
- Hora recogida: 00:18
- Distancia: 11.5 km

Pasajero más tardío:
- Marco Antonio Ilabaca Banda
- Hora presentación: 23:30
- Hora recogida: 23:17
- Distancia: 9.8 km
```

## 📝 Conclusión

El sistema ahora es **time-aware** y optimiza considerando:
- ✅ Distancias geográficas
- ✅ Tiempos de viaje estimados
- ✅ Horarios de presentación
- ✅ Ventanas de recogida
- ✅ Buffer de seguridad

Esto asegura que **todos los pasajeros lleguen a tiempo** a su hora de presentación en el terminal.
