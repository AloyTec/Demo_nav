#!/bin/bash

#############################################
# AWS Lambda Deployment Script
# Route Optimizer API
#############################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS Lambda Deployment Script${NC}"
echo -e "${GREEN}Route Optimizer API${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
FUNCTION_NAME="route-optimizer-api"
S3_BUCKET="route-optimizer-demo-889268462469"
AWS_REGION="us-east-1"
DEPLOY_DIR="lambda_deploy_package"
ZIP_NAME="lambda_deployment_$(date +%Y%m%d_%H%M%S).zip"

# Step 1: Clean up old deployment directory
echo -e "${YELLOW}[1/7] Cleaning up old deployment directory...${NC}"
rm -rf $DEPLOY_DIR
mkdir -p $DEPLOY_DIR

# Step 2: Install Python dependencies (using specific versions that work)
echo -e "${YELLOW}[2/7] Installing Python dependencies...${NC}"
echo "  Installing: pandas, numpy, geopy, scikit-learn, urllib3, openpyxl, xlrd, ortools"
pip install -t $DEPLOY_DIR \
    'pandas>=2.0,<2.4' \
    'numpy>=1.24,<1.27' \
    'geopy>=2.4,<2.5' \
    'scikit-learn>=1.3,<1.8' \
    'urllib3>=2.0,<3.0' \
    'openpyxl>=3.0,<3.2' \
    'xlrd>=2.0,<2.1' \
    'ortools>=9.8,<9.9' \
    --quiet --upgrade

# Step 3: Copy Lambda function code
echo -e "${YELLOW}[3/7] Copying Lambda function code...${NC}"
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

# Step 4: Clean up unnecessary files to reduce size
echo -e "${YELLOW}[4/7] Optimizing package size...${NC}"
cd $DEPLOY_DIR

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

# Remove bin directories (executables not needed in Lambda)
find . -type d -name "bin" -exec rm -rf {} + 2>/dev/null || true

# Remove scipy test data
find . -path "*/scipy/*/tests/data/*" -delete 2>/dev/null || true

# Note: We don't remove scipy or sklearn modules due to complex internal dependencies
# Instead, we focus on removing unnecessary files (already done above)

# Strip debug symbols from .so files
echo "  Stripping debug symbols from shared libraries..."
find . -name "*.so" -type f -exec strip {} + 2>/dev/null || true

# Remove .a files (static libraries)
find . -type f -name "*.a" -delete 2>/dev/null || true

cd ..

PACKAGE_SIZE=$(du -sh $DEPLOY_DIR | cut -f1)
echo "  ✓ Package optimized: $PACKAGE_SIZE"

# Step 5: Create ZIP file
echo -e "${YELLOW}[5/7] Creating deployment ZIP...${NC}"
cd $DEPLOY_DIR
zip -r ../$ZIP_NAME . -q
cd ..

ZIP_SIZE=$(ls -lh $ZIP_NAME | awk '{print $5}')
echo "  ✓ Created: $ZIP_NAME ($ZIP_SIZE)"

# Step 6: Upload to S3
echo -e "${YELLOW}[6/7] Uploading to S3...${NC}"
echo "  Bucket: s3://$S3_BUCKET/$ZIP_NAME"

aws s3 cp $ZIP_NAME s3://$S3_BUCKET/$ZIP_NAME --region $AWS_REGION

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Upload successful${NC}"
else
    echo -e "  ${RED}✗ Upload failed${NC}"
    exit 1
fi

# Step 7: Update Lambda function
echo -e "${YELLOW}[7/7] Updating Lambda function...${NC}"
echo "  Function: $FUNCTION_NAME"

aws lambda update-function-code \
    --function-name $FUNCTION_NAME \
    --s3-bucket $S3_BUCKET \
    --s3-key $ZIP_NAME \
    --region $AWS_REGION \
    --output json > /dev/null

if [ $? -eq 0 ]; then
    echo -e "  ${GREEN}✓ Lambda function updated successfully${NC}"

    # Wait for function to be ready
    echo "  Waiting for function to be ready..."
    aws lambda wait function-updated --function-name $FUNCTION_NAME --region $AWS_REGION

    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Deployment Complete!${NC}"
    echo -e "${GREEN}========================================${NC}"
    echo ""
    echo "Deployment Details:"
    echo "  • Function: $FUNCTION_NAME"
    echo "  • Package: $ZIP_NAME"
    echo "  • Size: $ZIP_SIZE"
    echo "  • S3: s3://$S3_BUCKET/$ZIP_NAME"
    echo ""
else
    echo -e "  ${RED}✗ Lambda function update failed${NC}"
    exit 1
fi

# Clean up local files (optional)
read -p "Clean up local deployment files? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -rf $DEPLOY_DIR
    rm $ZIP_NAME
    echo -e "${GREEN}✓ Cleanup complete${NC}"
fi
