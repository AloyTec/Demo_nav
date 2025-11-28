# 🔧 Lambda Configuration Fix Guide

## Issues Found

Your Lambda function is experiencing:

1. **⏱️ Timeout: 3 seconds** - Function times out before completing
2. **💾 Memory: 128 MB** - Insufficient for ML libraries (joblib, ortools, sklearn)
3. **🔒 Permission Error**: joblib multiprocessing failure in Lambda environment

## ✅ Fixes Applied

### 1. Code Changes ✓

Updated `lambda_function.py` and `Dockerfile` to:
- Set `JOBLIB_TEMP_FOLDER=/tmp` (Lambda's only writable directory)
- Disable multiprocessing (`JOBLIB_MULTIPROCESSING=0`)
- Configure single-threaded execution for NumPy/BLAS libraries

### 2. AWS Lambda Configuration (Required)

You MUST update your Lambda configuration:

#### **Option A: AWS Console (Recommended)**

1. Go to [AWS Lambda Console](https://console.aws.amazon.com/lambda)
2. Select your function
3. Go to **Configuration** → **General configuration**
4. Click **Edit**
5. Update:
   - **Memory**: `1024 MB` (minimum 512 MB, 1024 MB recommended)
   - **Timeout**: `2 min 0 sec` (120 seconds)
6. Click **Save**

#### **Option B: AWS CLI**

```bash
# Replace YOUR_FUNCTION_NAME with your Lambda function name
aws lambda update-function-configuration \
    --function-name YOUR_FUNCTION_NAME \
    --timeout 120 \
    --memory-size 1024
```

#### **Option C: Terraform (if using IaC)**

```hcl
resource "aws_lambda_function" "route_optimizer" {
  # ... other configuration ...
  timeout     = 120
  memory_size = 1024
}
```

## 📋 Next Steps

1. **Rebuild and push Docker image** (code has been updated)
2. **Update Lambda configuration** (see options above)
3. **Test the function**

## 🔍 Recommended Configuration

| Setting | Current | Recommended | Why |
|---------|---------|-------------|-----|
| **Timeout** | 3 sec | 120 sec | Geocoding + optimization takes 30-60 seconds |
| **Memory** | 128 MB | 1024 MB | ML libraries need ~500 MB, 1024 MB for performance |
| **Ephemeral Storage** | 512 MB | 512 MB (default) | Sufficient for /tmp usage |

## 💡 Cost Impact

- **Memory increase** (128 MB → 1024 MB): ~8x memory cost
- **Timeout increase** (3s → 120s): Only pay for actual execution time
- **Estimated cost per request**: ~$0.0001 - $0.0002 (still very cheap)

## 🧪 Testing

After deploying, test with:

```bash
curl https://YOUR_LAMBDA_URL.lambda-url.us-east-1.on.aws/api/health
```

Expected response:
```json
{
  "status": "ok",
  "message": "Route Optimizer Lambda is running"
}
```

## 🐛 Troubleshooting

If you still see timeout errors:
- Check CloudWatch Logs for actual execution time
- Consider increasing timeout to 180 seconds for large datasets (100+ drivers)
- Monitor memory usage in CloudWatch metrics

If you see memory errors:
- Increase memory to 1536 MB or 2048 MB
- Large datasets (200+ drivers) may need 2048 MB

## 📚 References

- [AWS Lambda Configuration](https://docs.aws.amazon.com/lambda/latest/dg/configuration-function-common.html)
- [Lambda Container Images](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html)
- [Lambda Pricing](https://aws.amazon.com/lambda/pricing/)
