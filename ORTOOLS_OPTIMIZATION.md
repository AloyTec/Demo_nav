# OR-Tools Optimization Implementation

## Resumen de Mejoras

Este documento describe las mejoras implementadas en el sistema de optimización de rutas.

## 1. Implementación de Google OR-Tools

### ¿Qué es OR-Tools?

Google OR-Tools es una suite de optimización de código abierto que proporciona algoritmos avanzados para resolver problemas de:
- Vehicle Routing Problem (VRP)
- Traveling Salesman Problem (TSP)
- Constraint Programming
- Linear Programming

### Ventajas sobre el algoritmo anterior

#### Algoritmo Anterior (K-means + 2-opt TSP)
- **K-means clustering**: Agrupaba conductores geográficamente
- **2-opt TSP**: Optimizaba rutas con intercambios locales (50 iteraciones máx)
- **Limitación**: Soluciones subóptimas, no considera múltiples restricciones simultáneamente

#### Nuevo Algoritmo (OR-Tools VRP Solver)
- **Guided Local Search**: Metaheurística avanzada que explora mejor el espacio de soluciones
- **Path Cheapest Arc**: Estrategia de construcción de solución inicial inteligente
- **Capacidad constraints**: Respeta límites de capacidad de vehículos (10 pasajeros/van)
- **Multi-criterio**: Optimiza distancia considerando restricciones de capacidad
- **Mejor convergencia**: Encuentra soluciones óptimas o casi-óptimas más rápido

### Implementación

```python
def optimize_route_ortools(drivers, time_limit_seconds=30):
    """
    Optimiza rutas usando Google OR-Tools VRP solver

    - Crea matriz de distancias entre todos los puntos
    - Configura el problema de ruteo de vehículos
    - Aplica restricciones de capacidad (10 pasajeros/van)
    - Usa Guided Local Search para encontrar solución óptima
    - Fallback automático a 2-opt TSP si OR-Tools falla
    """
```

### Estrategia de Fallback

El sistema implementa un fallback robusto de 3 niveles:

1. **Nivel 1**: OR-Tools con Guided Local Search (preferido)
2. **Nivel 2**: 2-opt TSP legacy (si OR-Tools falla)
3. **Nivel 3**: Greedy nearest neighbor (si 2-opt falla)

## 2. Configuración de Flota

### Cambios

```python
# Antes: número de vans calculado dinámicamente (2-5 vans)
num_vans = max(2, min(5, len(drivers) // 10 + 1))

# Ahora: flota estándar de 10 vans (configurable)
DEFAULT_NUM_VANS = 10
```

### Ventajas

- **Consistencia operacional**: Siempre usa 10 vans a menos que se especifique otro valor
- **Mejor utilización**: Distribuye pasajeros de forma más eficiente
- **Escalabilidad**: Preparado para flotas más grandes
- **Flexibilidad**: El frontend puede override con valor personalizado

## 3. Mejoras en Manejo de Errores

### Problema Anterior

- Errores de geocoding podían interrumpir toda la optimización
- No había visibilidad de qué direcciones fallaron
- No se reportaba la causa del problema

### Solución Implementada

#### Sistema de Tracking de Errores

```python
error_info = {
    'driver_index': idx + 1,
    'driver_name': driver.get('name', 'Unknown'),
    'address': driver['address'],
    'issue': 'Descripción del problema',
    'severity': 'error' | 'warning' | 'info'
}
```

#### Niveles de Severidad

1. **error**: Fallo crítico en procesamiento (ej: excepción no manejada)
2. **warning**: Geocoding falló, usando centro de Santiago (coordenadas fallback)
3. **info**: Distance Matrix API no disponible, usando cálculo geodésico

#### Continuidad del Proceso

```python
try:
    # Proceso normal de geocoding
    driver['coordinates'] = geocode_address(driver['address'])
except Exception as e:
    # Registrar error PERO continuar con valores fallback
    error_info = {...}
    driver['coordinates'] = fallback_coordinates
    # El proceso continúa sin interrumpirse
```

### Respuesta API Mejorada

```json
{
  "vans": [...],
  "totalDrivers": 54,
  "totalDistance": 123.5,
  "success": true,
  "hasIssues": true,
  "geocodingIssues": [
    {
      "driver_index": 12,
      "driver_name": "Juan Pérez",
      "address": "Calle Inválida 123, Santiago",
      "issue": "Geocoding failed - using Santiago center as fallback",
      "severity": "warning"
    },
    {
      "driver_index": 23,
      "driver_name": "María González",
      "address": "Av. Sin Número, Cerro Navia",
      "issue": "Distance Matrix API failed - using geodesic estimate",
      "severity": "info"
    }
  ],
  "optimizationMethod": "OR-Tools with fallback"
}
```

### Logging Mejorado

```
⚠ Geocoding Issues Summary: 5 address(es) had problems
  ❌ Errors: 1
  ⚠ Warnings: 3
  ℹ Info: 1
```

## 4. Beneficios Generales

### Performance

- **OR-Tools**: Encuentra mejores rutas en menos tiempo
- **Paralelización**: Geocoding continúa siendo paralelo (10 workers)
- **Time limit**: OR-Tools tiene límite de 30 segundos para garantizar respuesta rápida

### Robustez

- **No interrupciones**: Errores de geocoding no detienen la optimización
- **Múltiples fallbacks**: Sistema robusto con 3 niveles de fallback
- **Valores por defecto**: Coordenadas y tiempos razonables si todo falla

### Visibilidad

- **Reporte de errores**: Usuario ve exactamente qué direcciones tuvieron problemas
- **Causa del problema**: Se indica por qué falló (API, formato, etc.)
- **Severidad clara**: Usuario puede priorizar correcciones

### Mantenibilidad

- **Código modular**: Funciones separadas para cada estrategia
- **Fácil testing**: Cada componente puede probarse independientemente
- **Documentación**: Código bien comentado con docstrings

## 5. Próximos Pasos Sugeridos

### Optimizaciones Futuras

1. **Time windows**: Agregar ventanas de tiempo de pickup a OR-Tools
2. **Multi-depot**: Soporte para múltiples puntos de inicio
3. **Real-time updates**: Actualización de rutas en tiempo real
4. **Caché de geocoding**: Guardar coordenadas de direcciones frecuentes

### Monitoreo

1. **Métricas**: Trackear tasa de éxito de geocoding
2. **Performance**: Medir tiempo de optimización promedio
3. **Calidad**: Comparar distancias OR-Tools vs legacy

## Referencias

- [Google OR-Tools Documentation](https://developers.google.com/optimization)
- [VRP Guide](https://developers.google.com/optimization/routing/vrp)
- [Python OR-Tools](https://developers.google.com/optimization/install/python)
