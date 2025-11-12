#!/bin/bash
# Property MCP Server - Production Deployment Script

set -e

echo "=================================="
echo "Property MCP Server - Deployment"
echo "=================================="
echo ""

# Check if widget is built
if [ ! -f "web/dist/component.js" ]; then
    echo "❌ Widget not built!"
    echo "Building widget..."
    cd web
    npm install
    npm run build
    cd ..
    echo "✅ Widget built"
else
    echo "✅ Widget already built"
fi

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo ""
    echo "❌ Fly CLI not installed"
    echo ""
    echo "Install with:"
    echo "  macOS:   brew install flyctl"
    echo "  Linux:   curl -L https://fly.io/install.sh | sh"
    echo "  Windows: powershell -Command \"iwr https://fly.io/install.ps1 -useb | iex\""
    echo ""
    exit 1
fi

echo "✅ Fly CLI installed"
echo ""

# Check if logged in
if ! flyctl auth whoami &> /dev/null; then
    echo "❌ Not logged in to Fly.io"
    echo "Run: flyctl auth login"
    exit 1
fi

echo "✅ Authenticated with Fly.io"
echo ""

# Check if app exists
if ! flyctl status &> /dev/null; then
    echo "📦 App not created yet"
    echo ""
    echo "Creating app..."
    flyctl launch --no-deploy
    echo ""
fi

# Deploy
echo "🚀 Deploying to Fly.io..."
echo ""
flyctl deploy

echo ""
echo "=================================="
echo "✅ Deployment Complete!"
echo "=================================="
echo ""

# Get app info
APP_URL=$(flyctl status --json | grep -o '"Hostname":"[^"]*"' | cut -d'"' -f4)

echo "Your app is live at:"
echo "  🌐 https://$APP_URL"
echo ""
echo "MCP Endpoint:"
echo "  🔗 https://$APP_URL/mcp/"
echo ""
echo "Health Check:"
echo "  ❤️  https://$APP_URL/health"
echo ""
echo "Next Steps:"
echo "  1. Test health: curl https://$APP_URL/health"
echo "  2. Open ChatGPT Settings → Apps & Connectors"
echo "  3. Create connector with URL: https://$APP_URL/mcp/"
echo "  4. Enable in chat and test!"
echo ""
echo "View logs: flyctl logs -f"
echo "=================================="
