# Quick Deploy Guide

**5-minute deployment to production**

## Prerequisites

```bash
# Install Fly CLI (choose one)
brew install flyctl                    # macOS
curl -L https://fly.io/install.sh | sh # Linux

# Build widget
cd web && npm install && npm run build && cd ..
```

## Deploy

```bash
# One-command deploy
./deploy.sh

# Or manually
flyctl auth login
flyctl launch --no-deploy
flyctl deploy
```

## Connect to ChatGPT

1. **Get your URL**: `flyctl status`
2. **ChatGPT Settings** → Apps & Connectors → Create
3. **Server URL**: `https://your-app.fly.dev/mcp/`
4. **Enable** in new chat → Test: "Show me properties in DY4"

## Common Commands

```bash
# View logs
flyctl logs -f

# Check status
flyctl status

# Restart app
flyctl apps restart

# Scale up
flyctl scale vm shared-cpu-1x --memory 512

# SSH into machine
flyctl ssh console

# Open dashboard
flyctl dashboard
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Widget not rendering | `cd web && npm run build && flyctl deploy` |
| 502 errors | `flyctl logs` then `flyctl apps restart` |
| Slow responses | `flyctl scale vm shared-cpu-1x --memory 512` |

## URLs

- **App**: `https://your-app.fly.dev`
- **Health**: `https://your-app.fly.dev/health`
- **MCP**: `https://your-app.fly.dev/mcp/`
- **Widget Test**: `https://your-app.fly.dev/widget`

## Support

- Full guide: [DEPLOYMENT.md](DEPLOYMENT.md)
- Checklist: [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)
- Fly.io docs: https://fly.io/docs/
