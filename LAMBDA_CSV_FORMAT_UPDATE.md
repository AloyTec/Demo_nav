# Lambda CSV Format Update

## 🎯 Objetivo

Actualizar la función Lambda para soportar el **formato real de CSV** que usa el cliente actualmente, con separador punto y coma (`;`) y columnas específicas.

## 📁 Formato CSV del Cliente

### Archivo de ejemplo
`ListadoTraslados (54) 26-11-2025.csv`

### Características del formato:
- **Separador**: `;` (punto y coma)
- **Primera fila**: "Table 1" (header del sistema de exportación)
- **Segunda fila**: Nombres de columnas
- **Datos**: Desde la fila 3 en adelante

### Columnas del formato del cliente:
```
Rut;Código OB;Nombre Completo;Dirección;Comuna;Celular;Deposito;Día de programación;Hora de presentación;Lugar de presentación;Código asignación;Usuario creación registro;Fecha creación registro;Usuario modificación registro;Fecha modificación registro;Usuario eliminación registro;Fecha eliminación registro
```

## ✅ Cambios Realizados

### 1. Detección automática de "Table 1" header
```python
# Check if first row is "Table 1" (Excel export header)
if len(df) > 0 and str(df.iloc[0, 0]).strip() == 'Table 1':
    print("Detected 'Table 1' header, re-reading file...")
    # Re-read skipping the first row
    df = pd.read_csv(BytesIO(file_content), sep=';', skiprows=1)
```

### 2. Mapeo flexible de columnas
La Lambda ahora detecta automáticamente las columnas usando múltiples variantes:

| Campo | Columnas posibles |
|-------|-------------------|
| **Nombre** | "Nombre Completo", "Nombre", "Name" |
| **Dirección** | "Dirección", "Dirección Casa", "Address" |
| **Terminal** | "Lugar de presentación", "Terminal Destino", "Terminal", "Deposito" |
| **Hora** | "Hora de presentación", "Hora Presentación", "Hora" |
| **Comuna** | "Comuna" (opcional, mejora el geocoding) |

### 3. Mejor geocoding con Comuna
```python
# Build address with commune for better geocoding
address = str(row[address_col])
if commune_col and not pd.isna(row[commune_col]):
    commune = str(row[commune_col]).strip()
    # Only append commune if it's not already in the address
    if commune.lower() not in address.lower():
        address = f"{address}, {commune}"
```

**Ventaja**: Mejora la precisión del geocoding al agregar la comuna a la dirección.

Ejemplo:
- **Antes**: `"Obisco Umaña #546"` → puede geocodificar incorrectamente
- **Ahora**: `"Obisco Umaña #546, Estación Central"` → geocoding más preciso

### 4. Campos adicionales opcionales
```python
# Add optional fields if available
if 'Código OB' in df.columns:
    driver['code'] = str(row['Código OB'])

if 'Celular' in df.columns:
    driver['phone'] = str(row['Celular'])

if 'Rut' in df.columns:
    driver['rut'] = str(row['Rut'])
```

### 5. Validación de filas vacías
```python
# Skip empty rows
if pd.isna(row[name_col]) or str(row[name_col]).strip() == '':
    continue
```

## 📊 Compatibilidad

La Lambda ahora soporta **múltiples formatos**:

✅ **Formato del cliente** (nuevo):
- Separador: `;`
- Columnas: "Nombre Completo", "Dirección", "Comuna", etc.
- Con header "Table 1"

✅ **Formato de prueba anterior** (test_maipu_40_drivers.csv):
- Separador: `,`
- Columnas: "Nombre", "Dirección Casa", "Terminal", etc.
- Sin header especial

✅ **Formato Excel** (.xlsx):
- Cualquier variante de columnas

## 🚀 Deploy de la Lambda Actualizada

### Paso 1: Comprimir el paquete Lambda
```bash
cd lambda-package-v2
zip -r ../lambda-function-v2.zip .
cd ..
```

### Paso 2: Subir a AWS Lambda
```bash
# Opción 1: Usando AWS CLI
aws lambda update-function-code \
  --function-name route-optimizer-lambda \
  --zip-file fileb://lambda-function-v2.zip

# Opción 2: Usando la consola AWS
# 1. Ve a AWS Lambda Console
# 2. Selecciona la función "route-optimizer-lambda"
# 3. Click en "Upload from" > ".zip file"
# 4. Selecciona lambda-function-v2.zip
# 5. Click "Save"
```

### Paso 3: Verificar el deploy
```bash
# Test con el endpoint de health
curl https://tu-lambda-url.lambda-url.us-east-1.on.aws/health
```

## 🧪 Testing con el nuevo formato

### 1. Probar en local (opcional)
```python
import pandas as pd

# Test parsing
df = pd.read_csv('ListadoTraslados (54) 26-11-2025.csv', sep=';', skiprows=1)
print(df.columns)
print(df.head())
```

### 2. Probar en la demo
1. Ve a la aplicación web
2. Sube el archivo `ListadoTraslados (54) 26-11-2025.csv`
3. Verifica que se procesen los 54 conductores
4. Click en "Optimizar Rutas"

### 3. Verificar logs en CloudWatch
```bash
# Busca en los logs:
# "Detected 'Table 1' header, re-reading file..."
# "Mapped columns: Name=Nombre Completo, Address=Dirección, ..."
# "Successfully parsed 54 drivers from file"
```

## 📋 Ejemplo de datos procesados

**Input CSV**:
```
21865183-6;141651;Dany Manuel Nuñez Alvarado;Obisco Umaña #546;Estación Central;56958914827;El Conquistador;26/11/2025;06:17;EL CONQUISTADOR (D);...
```

**Output JSON**:
```json
{
  "name": "Dany Manuel Nuñez Alvarado",
  "address": "Obisco Umaña #546, Estación Central",
  "terminal": "EL CONQUISTADOR (D)",
  "time": "06:17",
  "code": "141651",
  "phone": "56958914827",
  "rut": "21865183-6"
}
```

## ⚠️ Notas Importantes

1. **El terminal es "El Conquistador"**, no "Terminal Maipú"
   - La Lambda NO activará el modo bus de acercamiento
   - Todas las vans irán directamente al terminal El Conquistador

2. **54 conductores** = aproximadamente **5-6 vans** (con capacidad de 10)

3. **Geocoding time**: ~54 segundos (1 segundo por conductor)
   - Considera aumentar el timeout de la Lambda si es necesario

4. **Rate limiting**: La Lambda espera 1 segundo entre geocodificaciones
   - Para respetar los límites de Nominatim (OpenStreetMap)

## 🔄 Siguientes Pasos

1. ✅ Cambios en Lambda completados
2. 📦 Deploy del paquete Lambda actualizado
3. 🧪 Testing con archivo real del cliente
4. 📊 Validar resultados de optimización
5. 🗺️ Verificar rutas de Google Maps en el mapa

## 📚 Archivos Modificados

- **lambda-package-v2/lambda_function.py** - Función de parsing actualizada
- **ListadoTraslados (54) 26-11-2025.csv** - Archivo de prueba real del cliente

## 🐛 Troubleshooting

### Error: "El archivo debe contener columnas de Nombre y Dirección"
- **Causa**: Columnas no detectadas
- **Solución**: Verifica que el archivo tenga las columnas esperadas
- **Debug**: Revisa los logs de CloudWatch para ver qué columnas se encontraron

### Error: Geocoding timeout
- **Causa**: Muchos conductores, geocoding lento
- **Solución**: Aumenta el timeout de la Lambda a 5 minutos (300 segundos)

### Los conductores no se geocodifican correctamente
- **Causa**: Direcciones ambiguas sin comuna
- **Solución**: ✅ Ya implementado - ahora agrega la comuna automáticamente

## 📝 Conclusión

La Lambda ahora es **más flexible y robusta**:
- ✅ Soporta el formato real del cliente
- ✅ Detección automática de delimitadores
- ✅ Mapeo flexible de columnas
- ✅ Mejor geocoding con comuna
- ✅ Retrocompatible con formatos anteriores
