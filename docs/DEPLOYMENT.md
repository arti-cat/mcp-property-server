# Production Deployment Guide

This guide covers deploying the Property MCP Server to production with persistent hosting.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Platform Options](#platform-options)
3. [Fly.io Deployment (Recommended)](#flyio-deployment-recommended)
4. [Alternative Platforms](#alternative-platforms)
5. [Post-Deployment](#post-deployment)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### Required

- **Git** - Version control
- **Docker** - For containerization (optional for Fly.io)
- **ChatGPT Pro/Team/Enterprise/Edu** - For ChatGPT integration

### Build Widget (Required)

```bash
cd web
npm install
npm run build
cd ..
```

Verify `web/dist/component.js` exists before deploying.

---

## Platform Options

Based on OpenAI's recommendations:

| Platform | Pros | Cons | Best For |
|----------|------|------|----------|
| **Fly.io** ⭐ | Free tier, auto TLS, global CDN, easy setup | Limited free resources | Most users |
| **Render** | Simple UI, auto-deploy from Git | Slower cold starts | Git-based workflows |
| **Railway** | Great DX, simple pricing | No free tier | Production apps |
| **Google Cloud Run** | Scale-to-zero, generous free tier | Cold starts can be slow | Variable traffic |

**Recommendation**: Fly.io for its balance of features, performance, and free tier.

---

## Fly.io Deployment (Recommended)

### 1. Install Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://fly.io/install.sh | sh

# Windows
powershell -Command "iwr https://fly.io/install.ps1 -useb | iex"
```

### 2. Sign Up & Authenticate

```bash
fly auth signup
# or
fly auth login
```

### 3. Create App

```bash
# From project root
fly launch --no-deploy

# Follow prompts:
# - App name: property-mcp-server (or your choice)
# - Region: Choose closest to your users (e.g., lhr for London)
# - PostgreSQL: No
# - Redis: No
```

This creates `fly.toml` (already provided in repo).

### 4. Configure Secrets (Optional)

If you add API keys or secrets later:

```bash
fly secrets set API_KEY=your-secret-key
fly secrets set DATABASE_URL=your-db-url
```

### 5. Deploy

```bash
fly deploy
```

This will:
- Build Docker image
- Push to Fly.io registry
- Deploy to your app
- Provide HTTPS URL

### 6. Get Your URL

```bash
fly status
```

Your app will be at: `https://property-mcp-server.fly.dev/mcp/`

### 7. Verify Deployment

```bash
# Check health
curl https://property-mcp-server.fly.dev/health

# Check MCP endpoint
curl https://property-mcp-server.fly.dev/mcp/
```

### 8. View Logs

```bash
# Real-time logs
fly logs

# Specific app
fly logs -a property-mcp-server
```

### 9. Scale (Optional)

```bash
# View current scale
fly scale show

# Scale up
fly scale vm shared-cpu-1x --memory 512

# Scale to multiple regions
fly regions add iad syd
```

---

## Alternative Platforms

### Render

1. **Connect GitHub repo**
2. **Create Web Service**
   - Environment: Docker
   - Branch: main
   - Port: 8080
3. **Environment Variables**
   ```
   ENVIRONMENT=production
   PORT=8080
   ```
4. **Deploy** - Auto-deploys on push

### Railway

1. **New Project** → Deploy from GitHub
2. **Settings**
   - Build: Dockerfile
   - Port: 8080
3. **Variables**
   ```
   ENVIRONMENT=production
   PORT=8080
   ```
4. **Generate Domain** - Get public URL

### Google Cloud Run

```bash
# Build and push
gcloud builds submit --tag gcr.io/PROJECT_ID/property-mcp

# Deploy
gcloud run deploy property-mcp \
  --image gcr.io/PROJECT_ID/property-mcp \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --port 8080 \
  --set-env-vars ENVIRONMENT=production
```

---

## Post-Deployment

### Connect to ChatGPT

1. **Enable Developer Mode**
   - ChatGPT → Settings → Apps & Connectors → Advanced
   - Toggle "Developer Mode"

2. **Create Connector**
   - Settings → Apps & Connectors → Create
   - Name: Property Server
   - Server URL: `https://your-app.fly.dev/mcp/`
   - Check "I trust this provider"
   - Click Create

3. **Use in Chat**
   - New chat → + → More → Developer Mode
   - Enable "Property Server" connector
   - Test: "Show me properties in DY4 under £100,000"

### Verify Widget Rendering

Ask ChatGPT:
```
Show me 5 properties in DY4 7LG under £100,000
```

You should see:
- ✅ Interactive property cards
- ✅ Favorite button (heart icon)
- ✅ Sort dropdown
- ✅ Responsive layout

---

## Monitoring & Maintenance

### Health Checks

The server includes a `/health` endpoint:

```bash
curl https://your-app.fly.dev/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-12T20:00:00Z",
  "environment": "production"
}
```

### Logging

**Fly.io:**
```bash
# Real-time
fly logs

# Last 100 lines
fly logs --lines 100

# Follow specific app
fly logs -a property-mcp-server -f
```

**Key metrics to monitor:**
- Request latency
- Error rates
- Memory usage
- CPU usage

### Updating

```bash
# Make changes locally
git add .
git commit -m "Update feature"

# Rebuild widget if needed
cd web && npm run build && cd ..

# Deploy
fly deploy
```

### Rollback

```bash
# List releases
fly releases

# Rollback to previous
fly releases rollback
```

---

## Troubleshooting

### Widget Not Rendering

**Symptom**: ChatGPT shows text instead of widget

**Solutions**:
1. Verify widget built: `ls -lh web/dist/component.js`
2. Check logs: `fly logs | grep -i widget`
3. Test endpoint: `curl https://your-app.fly.dev/widget`
4. Rebuild: `cd web && npm run build && fly deploy`

### 502 Bad Gateway

**Symptom**: Server not responding

**Solutions**:
1. Check status: `fly status`
2. View logs: `fly logs`
3. Restart: `fly apps restart`
4. Check health: `curl https://your-app.fly.dev/health`

### High Memory Usage

**Symptom**: App crashing or slow

**Solutions**:
1. Check metrics: `fly dashboard`
2. Scale up: `fly scale vm shared-cpu-1x --memory 512`
3. Review logs for memory leaks

### Cold Starts

**Symptom**: First request slow

**Solutions**:
1. Keep 1 machine always running: `auto_stop_machines = false` in `fly.toml`
2. Use health checks to keep warm
3. Consider upgrading plan for more resources

### CORS Issues

**Symptom**: Browser errors about CORS

**Solutions**:
1. Verify CORS middleware in `server_apps_sdk.py`
2. Check allowed origins
3. Test with curl: `curl -H "Origin: https://chatgpt.com" https://your-app.fly.dev/mcp/`

---

## Cost Estimates

### Fly.io Free Tier

- 3 shared-cpu VMs (256MB RAM each)
- 160GB outbound data transfer/month
- **Cost**: $0/month for basic usage

### Paid Tiers (if needed)

- **Hobby**: $5/month - 1 dedicated CPU, 512MB RAM
- **Scale**: $29/month - 2 dedicated CPUs, 1GB RAM

### Other Platforms

- **Render**: Free tier available, $7/month for paid
- **Railway**: $5/month minimum
- **Google Cloud Run**: Pay per request, ~$0-5/month for low traffic

---

## Security Best Practices

1. **Secrets Management**
   - Never commit secrets to Git
   - Use platform secret managers
   - Rotate keys regularly

2. **HTTPS Only**
   - All platforms provide automatic TLS
   - Never expose HTTP endpoints

3. **Rate Limiting**
   - Consider adding rate limiting for public APIs
   - Monitor for abuse

4. **Logging**
   - Log all tool calls with IDs
   - Monitor for suspicious patterns
   - Set up alerts for errors

---

## Next Steps

1. ✅ Deploy to Fly.io
2. ✅ Connect to ChatGPT
3. ✅ Test widget rendering
4. ✅ Monitor logs for 24 hours
5. ✅ Set up alerts (optional)
6. ✅ Document custom domain (optional)

---

## Support Resources

- **Fly.io Docs**: https://fly.io/docs/
- **FastMCP**: https://gofastmcp.com
- **OpenAI Apps SDK**: https://platform.openai.com/docs/mcp
- **Project Issues**: GitHub Issues

---

## Quick Reference

```bash
# Deploy
fly deploy

# Logs
fly logs -f

# Status
fly status

# Restart
fly apps restart

# Scale
fly scale show
fly scale vm shared-cpu-1x --memory 512

# Secrets
fly secrets list
fly secrets set KEY=value

# SSH into machine
fly ssh console

# Open dashboard
fly dashboard
```
