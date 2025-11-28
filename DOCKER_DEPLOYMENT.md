# 🐳 Docker Container Deployment Guide

## Route Optimizer Lambda - Container-based Deployment

Este documento describe cómo deployar la función Lambda usando Docker containers en lugar del método tradicional ZIP.

---

## 📋 Ventajas de Docker Container

| Característica | ZIP Deployment | Docker Container |
|----------------|----------------|------------------|
| **Límite de tamaño** | 250 MB (unzipped) | **10 GB** |
| **Optimización requerida** | ⚠️ Muy agresiva | ✅ Mínima |
| **Mantenibilidad** | ⚠️ Compleja | ✅ Simple |
| **Testing local** | ⚠️ Difícil | ✅ Fácil con Docker |
| **Tiempo de build** | ~2-3 min | ~5-10 min (primera vez) |
| **Cold start** | ~1-2 seg | ~3-5 seg |

---

## 🚀 Quick Start

### Requisitos Previos

1. **Docker Desktop** instalado y corriendo
   ```bash
   docker --version  # Debe mostrar versión 20.10+
   ```

2. **AWS CLI** configurado
   ```bash
   aws --version     # Debe mostrar versión 2.x
   aws sts get-caller-identity  # Verifica credenciales
   ```

3. **Permisos IAM** necesarios:
   - `ecr:CreateRepository`
   - `ecr:GetAuthorizationToken`
   - `ecr:PutImage`
   - `ecr:BatchCheckLayerAvailability`
   - `ecr:InitiateLayerUpload`
   - `ecr:UploadLayerPart`
   - `ecr:CompleteLayerUpload`
   - `lambda:UpdateFunctionCode`
   - `lambda:GetFunction`

---

## 📦 Archivos del Proyecto

```
Demo_nav/
├── Dockerfile                    # Definición de la imagen Docker
├── requirements.txt              # Dependencias Python
├── lambda_function.py            # Código de la función Lambda
├── deploy_docker_lambda.sh       # Script de deployment automatizado
├── .dockerignore                 # Archivos a excluir del build
└── DOCKER_DEPLOYMENT.md         # Esta documentación
```

---

## 🔧 Deployment Paso a Paso

### Opción 1: Deployment Automático (Recomendado)

```bash
# 1. Configurar credenciales AWS (si no están configuradas)
export AWS_ACCESS_KEY_ID="tu-access-key"
export AWS_SECRET_ACCESS_KEY="tu-secret-key"
export AWS_DEFAULT_REGION="us-east-1"

# 2. Ejecutar script de deployment
./deploy_docker_lambda.sh
```

El script automáticamente:
- ✅ Verifica que Docker esté corriendo
- ✅ Crea el repositorio ECR (si no existe)
- ✅ Autentica con ECR
- ✅ Construye la imagen Docker
- ✅ Sube la imagen a ECR
- ✅ Actualiza la función Lambda

**Tiempo estimado:** 5-10 minutos (primera vez), 3-5 minutos (deploys posteriores)

---

### Opción 2: Deployment Manual

#### Paso 1: Crear repositorio ECR

```bash
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
AWS_REGION="us-east-1"
ECR_REPOSITORY="route-optimizer-api"

aws ecr create-repository \
    --repository-name $ECR_REPOSITORY \
    --region $AWS_REGION \
    --image-scanning-configuration scanOnPush=true
```

#### Paso 2: Autenticar Docker con ECR

```bash
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com
```

#### Paso 3: Build de la imagen Docker

```bash
docker build --platform linux/amd64 -t route-optimizer-api:latest .
```

**Nota:** `--platform linux/amd64` es necesario si estás en Mac con chip M1/M2.

#### Paso 4: Tag de la imagen

```bash
docker tag route-optimizer-api:latest \
    ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/route-optimizer-api:latest
```

#### Paso 5: Push a ECR

```bash
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/route-optimizer-api:latest
```

#### Paso 6: Actualizar Lambda function

```bash
FUNCTION_NAME="route-optimizer-api"

aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/route-optimizer-api:latest \
    --region $AWS_REGION
```

---

## 🧪 Testing Local

Puedes probar la función Lambda localmente antes de deployar:

```bash
# 1. Build de la imagen
docker build -t route-optimizer-api:test .

# 2. Correr contenedor localmente
docker run -p 9000:8080 \
    -e GOOGLE_MAPS_API_KEY="tu-api-key" \
    route-optimizer-api:test

# 3. En otra terminal, invocar la función
curl -XPOST "http://localhost:9000/2015-03-31/functions/function/invocations" \
    -d '{"rawPath":"/api/health","requestContext":{"http":{"method":"GET"}}}'
```

---

## 🔍 Verificación del Deployment

### Verificar imagen en ECR

```bash
aws ecr describe-images \
    --repository-name route-optimizer-api \
    --region us-east-1
```

### Verificar configuración de Lambda

```bash
aws lambda get-function \
    --function-name route-optimizer-api \
    --region us-east-1 \
    --query 'Configuration.[FunctionName,PackageType,CodeSize,LastModified,State]' \
    --output table
```

### Test de la función

```bash
aws lambda invoke \
    --function-name route-optimizer-api \
    --payload '{"rawPath":"/api/health","requestContext":{"http":{"method":"GET"}}}' \
    --cli-binary-format raw-in-base64-out \
    response.json

cat response.json
```

---

## 📊 Tamaños y Tiempos

**Imagen Docker:**
- Tamaño estimado: ~1.5 - 2 GB
- Tiempo de build: 5-10 minutos (primera vez), 2-3 minutos (con cache)
- Tiempo de push a ECR: 2-3 minutos

**Deployment:**
- Tiempo total primera vez: ~10-15 minutos
- Tiempo deploys posteriores: ~5-7 minutos
- Cold start: ~3-5 segundos
- Warm start: ~100-200 ms

---

## 🐛 Troubleshooting

### Error: "Docker is not running"

**Solución:** Inicia Docker Desktop y espera a que esté completamente iniciado.

### Error: "authentication token has expired"

**Solución:** Re-autentica con ECR:
```bash
aws ecr get-login-password --region us-east-1 | \
    docker login --username AWS --password-stdin \
    ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com
```

### Error: "no space left on device"

**Solución:** Limpia imágenes Docker antiguas:
```bash
docker system prune -a
```

### Error: "exec format error"

**Solución:** Rebuild con la plataforma correcta:
```bash
docker build --platform linux/amd64 -t route-optimizer-api:latest .
```

### Lambda timeout

**Solución:** Aumenta el timeout de la función:
```bash
aws lambda update-function-configuration \
    --function-name route-optimizer-api \
    --timeout 300 \
    --region us-east-1
```

### Out of memory

**Solución:** Aumenta la memoria de la función:
```bash
aws lambda update-function-configuration \
    --function-name route-optimizer-api \
    --memory-size 3008 \
    --region us-east-1
```

---

## 🔄 Actualización del Código

Para deployar cambios en el código:

```bash
# 1. Editar lambda_function.py

# 2. Re-deployar (automático)
./deploy_docker_lambda.sh

# O manual
docker build --platform linux/amd64 -t route-optimizer-api:latest .
docker tag route-optimizer-api:latest ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/route-optimizer-api:latest
docker push ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/route-optimizer-api:latest
aws lambda update-function-code \
    --function-name route-optimizer-api \
    --image-uri ${AWS_ACCOUNT_ID}.dkr.ecr.us-east-1.amazonaws.com/route-optimizer-api:latest
```

---

## 💰 Costos Estimados

**ECR Storage:**
- ~$0.10/GB/mes
- Imagen de ~2GB = ~$0.20/mes

**Lambda Execution:**
- Memory: 2048 MB
- Costo depende del uso
- Capa gratuita: 400,000 GB-seconds/mes

**Data Transfer:**
- Primer GB gratis
- $0.09/GB después

**Total estimado:** $1-5/mes para uso moderado

---

## 📚 Referencias

- [AWS Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [AWS ECR Documentation](https://docs.aws.amazon.com/ecr/)
- [Docker for Lambda](https://docs.aws.amazon.com/lambda/latest/dg/images-test.html)
- [Lambda Runtimes](https://docs.aws.amazon.com/lambda/latest/dg/lambda-runtimes.html)

---

## ✅ Checklist de Deployment

- [ ] Docker Desktop instalado y corriendo
- [ ] AWS CLI configurado con credenciales
- [ ] Permisos IAM verificados
- [ ] Repositorio ECR creado
- [ ] Imagen Docker buildeada
- [ ] Imagen pusheada a ECR
- [ ] Lambda function actualizada
- [ ] Función testeada y funcionando
- [ ] Logs verificados en CloudWatch
- [ ] Documentación actualizada

---

## 🆘 Soporte

Si encuentras problemas:
1. Revisa los logs de CloudWatch
2. Verifica la sección de Troubleshooting
3. Consulta la documentación de AWS
4. Contacta al equipo de desarrollo
