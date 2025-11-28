# AWS Lambda Deployment Guide
## Route Optimizer API

Este documento explica cómo desplegar actualizaciones del código Lambda de forma segura y confiable.

---

## 📋 Requisitos Previos

1. **AWS CLI configurado** con credenciales válidas
2. **Python 3.11** instalado
3. **pip** actualizado
4. Acceso al bucket S3: `route-optimizer-demo-889268462469`
5. Permisos para actualizar la función Lambda: `route-optimizer-api`

---

## 🚀 Método Rápido (Script Automatizado)

### Opción 1: Usar el script de deploy

```bash
# Asegúrate de que tu código actualizado esté en lambda_function_updated.py
./deploy_lambda.sh
```

El script automáticamente:
- ✅ Instala las dependencias de Python correctas
- ✅ Optimiza el tamaño del paquete
- ✅ Crea el archivo ZIP
- ✅ Sube a S3
- ✅ Actualiza la función Lambda

---

## 📦 Método Manual (Paso a Paso)

### 1. Preparar el entorno

```bash
# Limpiar directorio previo
rm -rf lambda_deploy_package
mkdir lambda_deploy_package
```

### 2. Instalar dependencias

**IMPORTANTE:** Usar versiones específicas que funcionan con Lambda:

```bash
pip install -t lambda_deploy_package \
    'pandas>=2.0,<2.4' \
    'numpy>=1.24,<1.27' \
    'geopy>=2.4,<2.5' \
    'scikit-learn>=1.3,<1.8' \
    'urllib3>=2.0,<3.0' \
    'openpyxl>=3.0,<3.2' \
    'xlrd>=2.0,<2.1' \
    --upgrade
```

**¿Por qué estas versiones?**
- numpy 1.x es más ligero que 2.x (crítico para el límite de 250MB)
- Estas versiones han sido probadas y funcionan en Lambda

### 3. Copiar código Lambda

```bash
cp lambda_function_updated.py lambda_deploy_package/lambda_function.py
```

### 4. Optimizar el paquete

```bash
cd lambda_deploy_package

# Eliminar tests
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true

# Eliminar archivos innecesarios
find . -type f -name "*.pyc" -delete
find . -type f -name "*.pyx" -delete
find . -type f -name "*.c" -delete
find . -type f -name "*.md" -delete

# Strip símbolos de debug
find . -name "*.so" -type f -exec strip {} + 2>/dev/null || true

cd ..
```

### 5. Crear ZIP

```bash
cd lambda_deploy_package
zip -r ../lambda_deployment.zip . -q
cd ..
```

### 6. Verificar tamaño

```bash
ls -lh lambda_deployment.zip
# Debe ser aproximadamente 65-70 MB (comprimido)
# Descomprimido debe ser < 250 MB
```

### 7. Subir a S3

```bash
aws s3 cp lambda_deployment.zip \
    s3://route-optimizer-demo-889268462469/lambda_deployment.zip \
    --region us-east-1
```

### 8. Actualizar Lambda

```bash
aws lambda update-function-code \
    --function-name route-optimizer-api \
    --s3-bucket route-optimizer-demo-889268462469 \
    --s3-key lambda_deployment.zip \
    --region us-east-1
```

### 9. Verificar el deploy

```bash
# Esperar a que la función esté lista
aws lambda wait function-updated \
    --function-name route-optimizer-api \
    --region us-east-1

# Verificar estado
aws lambda get-function \
    --function-name route-optimizer-api \
    --region us-east-1 \
    --query 'Configuration.[State,LastUpdateStatus]' \
    --output text
```

---

## ⚠️ Problemas Comunes y Soluciones

### Error: "Unzipped size must be smaller than 262144000 bytes"

**Causa:** El paquete descomprimido excede 250 MB.

**Solución:**
1. Usar versiones ligeras de las bibliotecas (numpy 1.x en lugar de 2.x)
2. Ejecutar la optimización del paso 4 correctamente
3. Verificar que se eliminaron archivos innecesarios:
   ```bash
   du -h -d 1 lambda_deploy_package/ | sort -h
   ```

### Error: "InvalidAccessKeyId"

**Causa:** Credenciales de AWS incorrectas o con comillas.

**Solución:**
```bash
# Verificar credenciales
aws configure list

# Si tienen comillas, exportar sin comillas:
export AWS_ACCESS_KEY_ID=AKIA...
export AWS_SECRET_ACCESS_KEY=...
export AWS_DEFAULT_REGION=us-east-1
```

### Error: Function update timeout

**Causa:** La función tardó mucho en actualizarse.

**Solución:**
```bash
# Esperar manualmente
aws lambda wait function-updated --function-name route-optimizer-api --region us-east-1

# O verificar estado cada 10 segundos
watch -n 10 'aws lambda get-function --function-name route-optimizer-api --query Configuration.LastUpdateStatus --output text'
```

---

## 📊 Tamaños de Referencia

| Componente | Tamaño Aproximado |
|------------|-------------------|
| numpy 1.26 | ~25 MB |
| pandas 2.x | ~30 MB |
| scipy | ~70 MB (si se usa) |
| sklearn | ~28 MB |
| geopy + deps | ~2 MB |
| Código Lambda | ~40 KB |
| **Total (sin optimizar)** | ~210 MB |
| **Total (optimizado)** | ~190 MB |
| **ZIP comprimido** | ~65-70 MB |

---

## 🔒 Variables de Entorno

La función Lambda requiere:

```
GOOGLE_MAPS_API_KEY=AIzaSy...
```

Configurar con:
```bash
aws lambda update-function-configuration \
    --function-name route-optimizer-api \
    --environment "Variables={GOOGLE_MAPS_API_KEY=AIzaSy...}" \
    --region us-east-1
```

---

## 📝 Notas Importantes

1. **Siempre hacer backup** del código que funciona antes de actualizar
2. **Probar localmente** antes de desplegar
3. **Verificar logs** después del deploy:
   ```bash
   aws logs tail /aws/lambda/route-optimizer-api --follow
   ```
4. **Rollback rápido** si algo falla:
   ```bash
   # Usar el último ZIP que funcionó
   aws lambda update-function-code \
       --function-name route-optimizer-api \
       --s3-bucket route-optimizer-demo-889268462469 \
       --s3-key lambda_fixed.zip
   ```

---

## 🎯 Checklist de Deploy

- [ ] Código actualizado en `lambda_function_updated.py`
- [ ] Credenciales AWS configuradas
- [ ] Script de deploy ejecutable: `chmod +x deploy_lambda.sh`
- [ ] Ejecutar: `./deploy_lambda.sh`
- [ ] Verificar que no hay errores
- [ ] Probar endpoint: `/api/health`
- [ ] Verificar logs en CloudWatch

---

## 📞 Soporte

Si encuentras problemas:
1. Revisa los logs de CloudWatch
2. Verifica el tamaño del paquete
3. Asegúrate de usar las versiones correctas de las bibliotecas
4. Si todo falla, usa el último ZIP que funcionó (lambda_fixed.zip)

---

**Última actualización:** 2025-11-28
