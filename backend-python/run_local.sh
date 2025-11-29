#!/bin/bash

#############################################
# Local Development Server Runner
# Route Optimizer API
#############################################

set -e  # Exit on error

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Route Optimizer - Local Dev Server${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo -e "${YELLOW}Virtual environment not found. Creating...${NC}"
    uv venv --python 3.12
    echo -e "${GREEN}✓ Virtual environment created${NC}"
    echo ""
fi

# Activate virtual environment
if [ -f ".venv/bin/activate" ]; then
    source .venv/bin/activate
elif [ -f ".venv/Scripts/activate" ]; then
    source .venv/Scripts/activate
else
    echo -e "${RED}✗ Could not find virtual environment activation script${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Virtual environment activated${NC}"
echo ""

# Check if dependencies are installed
if ! python -c "import flask" 2>/dev/null; then
    echo -e "${YELLOW}Dependencies not installed. Installing...${NC}"
    uv pip install -e ".[dev]"
    echo -e "${GREEN}✓ Dependencies installed${NC}"
    echo ""
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠ .env file not found${NC}"
    echo -e "${YELLOW}Creating from .env.example...${NC}"
    cp .env.example .env
    echo -e "${RED}Please edit .env and add your configuration${NC}"
    echo -e "${RED}Especially: GOOGLE_MAPS_API_KEY${NC}"
    echo ""
    read -p "Press Enter to continue or Ctrl+C to exit..."
fi

# Load .env file
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo -e "${GREEN}✓ Environment variables loaded${NC}"
    echo ""
fi

# Verify critical environment variables
if [ -z "$GOOGLE_MAPS_API_KEY" ] || [ "$GOOGLE_MAPS_API_KEY" = "your-google-maps-api-key-here" ]; then
    echo -e "${RED}❌ GOOGLE_MAPS_API_KEY not configured in .env${NC}"
    echo -e "${YELLOW}The API will run but geocoding will fail.${NC}"
    echo -e "${YELLOW}Get an API key from: https://console.cloud.google.com/google/maps-apis${NC}"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Get port from environment or default to 8000
PORT=${PORT:-8000}

echo -e "${BLUE}Starting Flask development server...${NC}"
echo ""

# Run the Flask app
python app.py

# This will only execute if the server stops
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Server stopped${NC}"
echo -e "${GREEN}========================================${NC}"
