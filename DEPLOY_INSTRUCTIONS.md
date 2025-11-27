# 🚀 Deploy Instructions - Lambda CSV Format Update

## ✅ Cambios Completados

La función Lambda ha sido actualizada para soportar el **formato real de CSV** que usa tu cliente.

### 📁 Archivo de prueba incluido
- **Nombre**: `ListadoTraslados (54) 26-11-2025.csv`
- **Conductores**: 54
- **Formato**: Punto y coma (`;`) como separador
- **Destino**: El Conquistador (D)

## 📦 Paquete Lambda Listo

**Archivo**: `lambda-function-updated.zip` (66 MB)
- ✅ Código actualizado incluido
- ✅ Todas las dependencias incluidas (pandas, numpy, sklearn, geopy, etc.)
- ✅ Listo para deploy directo a AWS Lambda

## 🎯 Deploy a AWS Lambda

### Opción 1: AWS CLI (Recomendado)

```bash
# Asegúrate de estar en el directorio del proyecto
cd /home/user/Demo_nav

# Deploy a Lambda
aws lambda update-function-code \
  --function-name route-optimizer-lambda \
  --zip-file fileb://lambda-function-updated.zip \
  --region us-east-1

# Verificar que se deployó correctamente
aws lambda get-function \
  --function-name route-optimizer-lambda \
  --region us-east-1 \
  --query 'Configuration.[FunctionName,LastModified,CodeSize]'
```

### Opción 2: Consola AWS

1. Ve a [AWS Lambda Console](https://console.aws.amazon.com/lambda/)
2. Selecciona tu función: **route-optimizer-lambda**
3. En la pestaña "Code", haz click en **"Upload from"**
4. Selecciona **".zip file"**
5. Sube el archivo: `lambda-function-updated.zip`
6. Click **"Save"**
7. Espera a que se complete el upload (~1-2 minutos por el tamaño)

### Opción 3: Reconstruir desde código fuente

```bash
# Si prefieres reconstruir el paquete tú mismo:
cd lambda-package-v2

# Instalar/actualizar dependencias (si es necesario)
pip install -t . pandas numpy scikit-learn geopy openpyxl boto3

# Crear el zip
zip -r ../lambda-function-updated.zip .

# Deploy
aws lambda update-function-code \
  --function-name route-optimizer-lambda \
  --zip-file fileb://../lambda-function-updated.zip
```

## 🧪 Testing

### 1. Test de Health Check
```bash
curl https://YOUR_LAMBDA_URL.lambda-url.us-east-1.on.aws/health
```

**Respuesta esperada**:
```json
{
  "status": "ok",
  "message": "Route Optimizer Lambda is running"
}
```

### 2. Test con la UI Web

1. Ve a tu aplicación web de demostración
2. Haz click en **"Cargar Archivo"**
3. Selecciona: `ListadoTraslados (54) 26-11-2025.csv`
4. Verás un mensaje de confirmación: **"Archivo procesado exitosamente"**
5. Deberías ver: **54 conductores cargados**
6. Haz click en **"Optimizar Rutas"**
7. Espera ~1-2 minutos (geocoding + optimización)
8. Verás las rutas optimizadas en el mapa

### 3. Verificar Logs en CloudWatch

```bash
# Ver los últimos logs
aws logs tail /aws/lambda/route-optimizer-lambda --follow
```

**Busca estos mensajes**:
```
✓ Detected 'Table 1' header, re-reading file...
✓ Mapped columns: Name=Nombre Completo, Address=Dirección, ...
✓ Successfully parsed 54 drivers from file
✓ Using BUS MODE for X drivers to El Conquistador
✓ Optimization complete: X vans, XX.X km total
```

## 📊 Resultados Esperados

Con 54 conductores a "El Conquistador":

- **Vans necesarias**: ~5-6 vans
- **Modo**: Normal (NO bus mode, ya que no es Terminal Maipú)
- **Distancia total**: ~150-200 km (depende de la distribución)
- **Tiempo de procesamiento**: ~1-2 minutos
- **Tiempo de geocoding**: ~54 segundos (1 seg/conductor)

## 🔍 Debugging

### Si el archivo no se procesa correctamente:

1. **Verifica los logs de CloudWatch**:
   - ¿Aparece "Detected 'Table 1' header"?
   - ¿Se mapearon las columnas correctamente?

2. **Verifica la respuesta del endpoint /upload**:
   ```bash
   # Test upload directo
   curl -X POST https://YOUR_LAMBDA_URL/upload \
     -H "Content-Type: application/json" \
     -d '{
       "filename": "test.csv",
       "file_content": "BASE64_ENCODED_CSV"
     }'
   ```

3. **Verifica el timeout de Lambda**:
   - Recomendado: **5 minutos (300 segundos)** para 54 conductores
   - Actual: Verifica en AWS Console > Configuration > General configuration > Timeout

4. **Verifica la memoria de Lambda**:
   - Recomendado: **1024 MB** mínimo
   - Para 54 conductores con pandas/numpy

## ⚙️ Configuración Recomendada de Lambda

```
Function name: route-optimizer-lambda
Runtime: Python 3.12
Memory: 1024 MB
Timeout: 300 seconds (5 minutes)
Environment variables:
  (ninguna necesaria, usa DynamoDB y S3 con IAM roles)
```

## 📝 Notas Importantes

### Diferencias vs formato anterior:

| Aspecto | Formato Anterior | Formato Nuevo (Cliente) |
|---------|------------------|-------------------------|
| Separador | `,` (coma) | `;` (punto y coma) |
| Header especial | No | Sí ("Table 1") |
| Columna nombre | "Nombre" | "Nombre Completo" |
| Comuna | No incluida | Incluida (mejora geocoding) |
| Campos adicionales | Pocos | Rut, Código OB, Celular, etc. |

### Retrocompatibilidad:

✅ La Lambda sigue soportando el formato anterior
✅ Puedes subir archivos con coma o punto y coma
✅ Detección automática de columnas

## 🎉 ¡Listo!

Después del deploy:

1. ✅ Sube el archivo `ListadoTraslados (54) 26-11-2025.csv` en la UI
2. ✅ Optimiza las rutas
3. ✅ Verifica que se generan ~5-6 vans
4. ✅ Verifica las rutas en el mapa con Google Maps Routes API
5. ✅ Comparte la demo con el cliente

## 📚 Documentación Adicional

- **LAMBDA_CSV_FORMAT_UPDATE.md** - Detalles técnicos de los cambios
- **PROJECT_DOCUMENTATION.md** - Documentación completa del proyecto
- **GOOGLE_MAPS_SETUP.md** - Setup de Google Maps API

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs de CloudWatch
2. Verifica que el archivo está en el formato correcto
3. Prueba primero con el archivo de ejemplo incluido
4. Verifica el timeout y memoria de Lambda
