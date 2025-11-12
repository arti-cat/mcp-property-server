#!/bin/bash

# Apps SDK Deployment Script
# This script helps you deploy and test the Property MCP Server with Apps SDK

set -e

echo "========================================================================"
echo "Property MCP Server - Apps SDK Deployment"
echo "========================================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if widget is built
echo "Checking widget bundle..."
if [ -f "web/dist/component.js" ]; then
    SIZE=$(du -h web/dist/component.js | cut -f1)
    echo -e "${GREEN}✅ Widget bundle found: ${SIZE}${NC}"
else
    echo -e "${RED}❌ Widget bundle not found${NC}"
    echo "Building widget..."
    cd web
    npm install
    npm run build
    cd ..
    echo -e "${GREEN}✅ Widget built${NC}"
fi

echo ""
echo "------------------------------------------------------------------------"
echo "Starting Apps SDK Server..."
echo "------------------------------------------------------------------------"
echo ""

# Start the server
python3 server_apps_sdk.py
