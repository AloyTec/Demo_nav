#!/bin/bash

#############################################
# AWS Lambda Docker Container Deployment
# Route Optimizer API
#############################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS Lambda Docker Deployment${NC}"
echo -e "${GREEN}Route Optimizer API${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
AWS_REGION="${AWS_DEFAULT_REGION:-us-east-1}"
AWS_ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
ECR_REPOSITORY="route-optimizer-api"
IMAGE_TAG="${IMAGE_TAG:-latest}"
FUNCTION_NAME="route-optimizer-api"
ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPOSITORY}"

echo -e "${BLUE}Configuration:${NC}"
echo "  AWS Region: $AWS_REGION"
echo "  AWS Account: $AWS_ACCOUNT_ID"
echo "  ECR Repository: $ECR_REPOSITORY"
echo "  Image Tag: $IMAGE_TAG"
echo "  Function Name: $FUNCTION_NAME"
echo ""

# Step 1: Check Docker is running
echo -e "${YELLOW}[1/7] Checking Docker...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker is not running. Please start Docker and try again.${NC}"
    exit 1
fi
echo -e "${GREEN}✓ Docker is running${NC}"
echo ""

# Step 2: Create ECR repository (if it doesn't exist)
echo -e "${YELLOW}[2/7] Creating ECR repository (if needed)...${NC}"
aws ecr describe-repositories --repository-names $ECR_REPOSITORY --region $AWS_REGION > /dev/null 2>&1 || \
    aws ecr create-repository \
        --repository-name $ECR_REPOSITORY \
        --region $AWS_REGION \
        --image-scanning-configuration scanOnPush=true \
        --output json > /dev/null

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ ECR repository ready: $ECR_REPOSITORY${NC}"
else
    echo -e "${RED}✗ Failed to create/verify ECR repository${NC}"
    exit 1
fi
echo ""

# Step 3: Login to ECR
echo -e "${YELLOW}[3/7] Authenticating with ECR...${NC}"
aws ecr get-login-password --region $AWS_REGION | \
    docker login --username AWS --password-stdin $ECR_URI

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Successfully authenticated with ECR${NC}"
else
    echo -e "${RED}✗ ECR authentication failed${NC}"
    exit 1
fi
echo ""

# Step 4: Build Docker image
echo -e "${YELLOW}[4/7] Building Docker image...${NC}"
echo "  This may take 5-10 minutes for first build..."
DOCKER_BUILDKIT=1 docker build --platform linux/amd64 -t $ECR_REPOSITORY:$IMAGE_TAG .

if [ $? -eq 0 ]; then
    IMAGE_SIZE=$(docker images $ECR_REPOSITORY:$IMAGE_TAG --format "{{.Size}}")
    echo -e "${GREEN}✓ Docker image built successfully${NC}"
    echo "  Image size: $IMAGE_SIZE"
else
    echo -e "${RED}✗ Docker build failed${NC}"
    exit 1
fi
echo ""

# Step 5: Tag image for ECR
echo -e "${YELLOW}[5/7] Tagging image for ECR...${NC}"
docker tag $ECR_REPOSITORY:$IMAGE_TAG $ECR_URI:$IMAGE_TAG

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Image tagged: $ECR_URI:$IMAGE_TAG${NC}"
else
    echo -e "${RED}✗ Image tagging failed${NC}"
    exit 1
fi
echo ""

# Step 6: Push to ECR
echo -e "${YELLOW}[6/7] Pushing image to ECR...${NC}"
echo "  This may take 3-5 minutes..."
docker push $ECR_URI:$IMAGE_TAG

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ Image pushed to ECR successfully${NC}"
else
    echo -e "${RED}✗ Failed to push image to ECR${NC}"
    exit 1
fi
echo ""

# Step 7: Update Lambda function
echo -e "${YELLOW}[7/7] Updating Lambda function...${NC}"

# Check if function exists
aws lambda get-function --function-name $FUNCTION_NAME --region $AWS_REGION > /dev/null 2>&1
FUNCTION_EXISTS=$?

if [ $FUNCTION_EXISTS -eq 0 ]; then
    # Update existing function
    echo "  Updating existing function..."
    aws lambda update-function-code \
        --function-name $FUNCTION_NAME \
        --image-uri $ECR_URI:$IMAGE_TAG \
        --region $AWS_REGION \
        --output json > /dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Lambda function code updated${NC}"

        # Wait for update to complete
        echo "  Waiting for function update to complete..."
        aws lambda wait function-updated --function-name $FUNCTION_NAME --region $AWS_REGION

        echo -e "${GREEN}✓ Function is ready${NC}"
    else
        echo -e "${RED}✗ Failed to update Lambda function${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}  Function does not exist. Please create it manually or run:${NC}"
    echo ""
    echo "  aws lambda create-function \\"
    echo "    --function-name $FUNCTION_NAME \\"
    echo "    --package-type Image \\"
    echo "    --code ImageUri=$ECR_URI:$IMAGE_TAG \\"
    echo "    --role arn:aws:iam::$AWS_ACCOUNT_ID:role/lambda-execution-role \\"
    echo "    --timeout 300 \\"
    echo "    --memory-size 2048 \\"
    echo "    --region $AWS_REGION"
    echo ""
    exit 1
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "Deployment Details:"
echo "  • Function: $FUNCTION_NAME"
echo "  • Image URI: $ECR_URI:$IMAGE_TAG"
echo "  • Image Size: $IMAGE_SIZE"
echo "  • Region: $AWS_REGION"
echo ""
echo "Test the function:"
echo "  aws lambda invoke --function-name $FUNCTION_NAME \\"
echo "    --payload '{\"rawPath\":\"/api/health\",\"requestContext\":{\"http\":{\"method\":\"GET\"}}}' \\"
echo "    response.json"
echo ""

# Optional: Clean up local Docker images
read -p "Clean up local Docker images? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker rmi $ECR_REPOSITORY:$IMAGE_TAG 2>/dev/null || true
    docker rmi $ECR_URI:$IMAGE_TAG 2>/dev/null || true
    echo -e "${GREEN}✓ Cleanup complete${NC}"
fi
