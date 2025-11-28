#!/bin/bash

#############################################
# AWS Lambda Deployment Script with Layers
# Route Optimizer API
#############################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS Lambda Deployment with Layers${NC}"
echo -e "${GREEN}Route Optimizer API${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
FUNCTION_NAME="route-optimizer-api"
S3_BUCKET="route-optimizer-demo-889268462469"
AWS_REGION="us-east-1"
LAYER_NAME="route-optimizer-dependencies"
DEPLOY_DIR="lambda_deploy_package"
LAYER_DIR="lambda_layer"
ZIP_NAME="lambda_deployment_$(date +%Y%m%d_%H%M%S).zip"
LAYER_ZIP_NAME="lambda_layer_$(date +%Y%m%d_%H%M%S).zip"

# Step 1: Create Lambda Layer with heavy dependencies
echo -e "${YELLOW}[1/9] Creating Lambda Layer with heavy dependencies...${NC}"
rm -rf $LAYER_DIR
mkdir -p $LAYER_DIR/python

echo "  Installing heavy dependencies to layer: scipy, numpy, scikit-learn, ortools"
pip install -t $LAYER_DIR/python \
    'scipy>=1.10,<1.17' \
    'numpy>=1.24,<1.27' \
    'scikit-learn>=1.3,<1.8' \
    'ortools>=9.8,<9.9' \
    --quiet --upgrade

# Optimize layer
echo "  Optimizing layer size..."
cd $LAYER_DIR/python

# Remove test directories
find . -type d -name "tests" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "test" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "examples" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "benchmarks" -exec rm -rf {} + 2>/dev/null || true

# Remove unnecessary files
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyx" -delete 2>/dev/null || true
find . -type f -name "*.pxd" -delete 2>/dev/null || true
find . -type f -name "*.pxi" -delete 2>/dev/null || true
find . -type f -name "*.c" -delete 2>/dev/null || true
find . -type f -name "*.cpp" -delete 2>/dev/null || true
find . -type f -name "*.h" -delete 2>/dev/null || true
find . -type f -name "*.hpp" -delete 2>/dev/null || true
find . -type f -name "*.pyi" -delete 2>/dev/null || true
find . -type f -name "*.typed" -delete 2>/dev/null || true

# Remove documentation
find . -type d -name "doc" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "docs" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.md" -delete 2>/dev/null || true
find . -type f -name "*.rst" -delete 2>/dev/null || true
find . -type f -name "*.txt" -delete 2>/dev/null || true
find . -type f -name "LICENSE*" -delete 2>/dev/null || true
find . -type f -name "COPYING*" -delete 2>/dev/null || true

# Remove bin directories
find . -type d -name "bin" -exec rm -rf {} + 2>/dev/null || true

# Strip debug symbols
echo "  Stripping debug symbols..."
find . -name "*.so" -type f -exec strip {} + 2>/dev/null || true

# Remove .a files
find . -type f -name "*.a" -delete 2>/dev/null || true

cd ../..

LAYER_SIZE=$(du -sh $LAYER_DIR | cut -f1)
echo "  ✓ Layer optimized: $LAYER_SIZE"

# Step 2: Create Layer ZIP
echo -e "${YELLOW}[2/9] Creating layer ZIP...${NC}"
cd $LAYER_DIR
zip -r ../$LAYER_ZIP_NAME . -q
cd ..

LAYER_ZIP_SIZE=$(ls -lh $LAYER_ZIP_NAME | awk '{print $5}')
echo "  ✓ Created: $LAYER_ZIP_NAME ($LAYER_ZIP_SIZE)"

# Step 3: Upload Layer to S3
echo -e "${YELLOW}[3/9] Uploading layer to S3...${NC}"
echo "  Bucket: s3://$S3_BUCKET/$LAYER_ZIP_NAME"

aws s3 cp $LAYER_ZIP_NAME s3://$S3_BUCKET/$LAYER_ZIP_NAME --region $AWS_REGION

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Layer upload successful${NC}"
else
    echo -e "  ${RED}✗ Layer upload failed${NC}"
    exit 1
fi

# Step 4: Publish Lambda Layer
echo -e "${YELLOW}[4/9] Publishing Lambda Layer...${NC}"

LAYER_VERSION=$(aws lambda publish-layer-version \
    --layer-name $LAYER_NAME \
    --content S3Bucket=$S3_BUCKET,S3Key=$LAYER_ZIP_NAME \
    --compatible-runtimes python3.11 \
    --region $AWS_REGION \
    --output text \
    --query 'Version')

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Layer published: Version $LAYER_VERSION${NC}"
else
    echo -e "  ${RED}✗ Layer publishing failed${NC}"
    exit 1
fi

LAYER_ARN="arn:aws:lambda:$AWS_REGION:$(aws sts get-caller-identity --query Account --output text):layer:$LAYER_NAME:$LAYER_VERSION"
echo "  Layer ARN: $LAYER_ARN"

# Step 5: Clean up old deployment directory
echo -e "${YELLOW}[5/9] Cleaning up old deployment directory...${NC}"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Step 6: Install lighter dependencies for function code
echo -e "${YELLOW}[6/9] Installing lighter dependencies...${NC}"
echo "  Installing: pandas, geopy, urllib3, openpyxl, xlrd"
pip install -t $DEPLOY_DIR \
    'pandas>=2.0,<2.4' \
    'geopy>=2.4,<2.5' \
    'urllib3>=2.0,<3.0' \
    'openpyxl>=3.0,<3.2' \
    'xlrd>=2.0,<2.1' \
    --quiet --upgrade

# Step 7: Copy Lambda function code
echo -e "${YELLOW}[7/9] Copying Lambda function code...${NC}"
if [ -f "lambda_function_updated.py" ]; then
    cp lambda_function_updated.py $DEPLOY_DIR/lambda_function.py
    echo "  ✓ Copied lambda_function_updated.py"
elif [ -f "lambda_function.py" ]; then
    cp lambda_function.py $DEPLOY_DIR/
    echo "  ✓ Copied lambda_function.py"
else
    echo -e "${RED}  ✗ Error: No lambda function file found!${NC}"
    exit 1
fi

# Step 8: Create function ZIP (much smaller now)
echo -e "${YELLOW}[8/9] Creating function deployment ZIP...${NC}"
cd $DEPLOY_DIR
zip -r ../$ZIP_NAME . -q
cd ..

ZIP_SIZE=$(ls -lh $ZIP_NAME | awk '{print $5}')
echo "  ✓ Created: $ZIP_NAME ($ZIP_SIZE)"

# Step 9: Upload and update Lambda function
echo -e "${YELLOW}[9/9] Uploading and updating Lambda function...${NC}"
echo "  Uploading to S3..."

aws s3 cp $ZIP_NAME s3://$S3_BUCKET/$ZIP_NAME --region $AWS_REGION

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Upload successful${NC}"
else
    echo -e "  ${RED}✗ Upload failed${NC}"
    exit 1
fi

echo "  Updating function code..."

aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --s3-bucket $S3_BUCKET \
    --s3-key $ZIP_NAME \
    --region $AWS_REGION \
    --output json > /dev/null

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Lambda function code updated${NC}"

    # Wait for function to be ready
    echo "  Waiting for function to be ready..."
    aws lambda wait function-updated --function-name $FUNCTION_NAME --region $AWS_REGION

    # Attach layer to function
    echo "  Attaching layer to function..."
    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --layers $LAYER_ARN \
        --region $AWS_REGION \
        --output json > /dev/null

    if [ $? -eq 0 ]; then
        echo -e "  ${GREEN}✓ Layer attached to function${NC}"

        echo -e "${GREEN}========================================${NC}"
        echo -e "${GREEN}Deployment Complete!${NC}"
        echo -e "${GREEN}========================================${NC}"
        echo ""
        echo "Deployment Details:"
        echo "  • Function: $FUNCTION_NAME"
        echo "  • Function Package: $ZIP_NAME ($ZIP_SIZE)"
        echo "  • Layer: $LAYER_NAME (Version $LAYER_VERSION)"
        echo "  • Layer Size: $LAYER_SIZE"
        echo "  • S3 Bucket: $S3_BUCKET"
        echo ""
    else
        echo -e "  ${RED}✗ Failed to attach layer${NC}"
        exit 1
    fi
else
    echo -e "  ${RED}✗ Lambda function update failed${NC}"
    exit 1
fi

# Clean up local files (optional)
read -p "Clean up local deployment files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf $DEPLOY_DIR
    rm -rf $LAYER_DIR
    rm $ZIP_NAME
    rm $LAYER_ZIP_NAME
    echo -e "${GREEN}✓ Cleanup complete${NC}"
fi
