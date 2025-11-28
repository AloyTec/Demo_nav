#!/bin/bash

#############################################
# Deploy Docker Image and Configure Lambda
# Includes timeout and memory fixes
#############################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Lambda Deployment & Configuration${NC}"
echo -e "${GREEN}Route Optimizer API${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration
FUNCTION_NAME="${LAMBDA_FUNCTION_NAME:-route-optimizer-api}"
TIMEOUT=120
MEMORY_SIZE=1024

echo -e "${BLUE}Configuration:${NC}"
echo "  Function Name: $FUNCTION_NAME"
echo "  Timeout: ${TIMEOUT}s"
echo "  Memory: ${MEMORY_SIZE}MB"
echo ""

# Step 1: Deploy Docker Image
echo -e "${YELLOW}Step 1: Deploying Docker Image${NC}"
echo -e "${BLUE}This will build and push the updated image to ECR...${NC}"
echo ""

# Run the existing deploy script
if [ -f "./deploy_docker_lambda.sh" ]; then
    bash ./deploy_docker_lambda.sh
else
    echo -e "${RED}✗ deploy_docker_lambda.sh not found${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}✓ Docker deployment complete${NC}"
echo ""

# Step 2: Update Lambda Configuration
echo -e "${YELLOW}Step 2: Updating Lambda Configuration${NC}"
echo ""

# Get current configuration
echo -e "${BLUE}Current configuration:${NC}"
CURRENT_CONFIG=$(aws lambda get-function-configuration --function-name $FUNCTION_NAME)
CURRENT_TIMEOUT=$(echo $CURRENT_CONFIG | python3 -c "import sys, json; print(json.load(sys.stdin)['Timeout'])")
CURRENT_MEMORY=$(echo $CURRENT_CONFIG | python3 -c "import sys, json; print(json.load(sys.stdin)['MemorySize'])")

echo "  Current Timeout: ${CURRENT_TIMEOUT}s"
echo "  Current Memory: ${CURRENT_MEMORY}MB"
echo ""

# Update configuration if needed
if [ "$CURRENT_TIMEOUT" != "$TIMEOUT" ] || [ "$CURRENT_MEMORY" != "$MEMORY_SIZE" ]; then
    echo -e "${YELLOW}Updating Lambda configuration...${NC}"

    aws lambda update-function-configuration \
        --function-name $FUNCTION_NAME \
        --timeout $TIMEOUT \
        --memory-size $MEMORY_SIZE \
        --output json > /dev/null

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Configuration updated successfully${NC}"
        echo "  New Timeout: ${TIMEOUT}s"
        echo "  New Memory: ${MEMORY_SIZE}MB"

        # Wait for update to complete
        echo ""
        echo -e "${YELLOW}Waiting for configuration update to complete...${NC}"
        aws lambda wait function-updated --function-name $FUNCTION_NAME
        echo -e "${GREEN}✓ Configuration update complete${NC}"
    else
        echo -e "${RED}✗ Failed to update configuration${NC}"
        exit 1
    fi
else
    echo -e "${GREEN}✓ Configuration already up to date${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Deployment and Configuration Complete!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Step 3: Test the function
echo -e "${YELLOW}Step 3: Testing the function${NC}"
echo ""

# Test health endpoint
echo "Testing health endpoint..."
RESPONSE=$(aws lambda invoke \
    --function-name $FUNCTION_NAME \
    --payload '{"rawPath":"/api/health","requestContext":{"http":{"method":"GET"}}}' \
    /tmp/response.json 2>&1)

if [ $? -eq 0 ]; then
    RESULT=$(cat /tmp/response.json)
    echo -e "${GREEN}✓ Function responding${NC}"
    echo "  Response: $RESULT"
    rm /tmp/response.json
else
    echo -e "${RED}✗ Function test failed${NC}"
    echo "$RESPONSE"
fi

echo ""
echo -e "${GREEN}All done!${NC}"
echo ""
echo "Next steps:"
echo "  1. Check CloudWatch Logs to verify no more timeout/memory errors"
echo "  2. Test with actual requests via your Lambda URL"
echo "  3. Monitor execution time and memory usage"
echo ""
