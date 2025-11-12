# Pre-Deployment Checklist

Use this checklist before deploying to production.

## ✅ Pre-Deployment

### Code & Build
- [ ] Widget built: `ls -lh web/dist/component.js`
- [ ] All tests passing: `python3 -m pytest test_server.py -v`
- [ ] No uncommitted changes: `git status`
- [ ] Latest code pushed: `git push origin main`

### Configuration
- [ ] `Dockerfile` present
- [ ] `fly.toml` configured (or platform equivalent)
- [ ] `.dockerignore` configured
- [ ] Environment variables documented

### Testing
- [ ] Local server runs: `python3 server_apps_sdk.py --http`
- [ ] Health endpoint works: `curl http://localhost:8000/health`
- [ ] Widget renders locally: Open `http://localhost:8000/widget`
- [ ] All tools tested via ChatGPT (local ngrok)

---

## 🚀 Deployment

### Platform Setup
- [ ] Fly CLI installed: `flyctl version`
- [ ] Authenticated: `flyctl auth whoami`
- [ ] App created: `flyctl launch --no-deploy` (first time only)

### Deploy
- [ ] Run deployment: `./deploy.sh` or `flyctl deploy`
- [ ] Deployment successful (no errors)
- [ ] App status healthy: `flyctl status`

---

## ✅ Post-Deployment

### Verification
- [ ] Health check passes: `curl https://your-app.fly.dev/health`
- [ ] MCP endpoint responds: `curl https://your-app.fly.dev/mcp/`
- [ ] Widget endpoint works: `curl https://your-app.fly.dev/widget`
- [ ] Logs show no errors: `flyctl logs`

### ChatGPT Integration
- [ ] Developer Mode enabled in ChatGPT
- [ ] Connector created with production URL
- [ ] Connector enabled in test chat
- [ ] Test query works: "Show me properties in DY4 under £100,000"
- [ ] Widget renders correctly (property cards visible)
- [ ] Favorites work (heart icon toggles)
- [ ] Sorting works (price/bedrooms dropdown)

### Performance
- [ ] Response time < 2 seconds
- [ ] No memory warnings in logs
- [ ] CPU usage normal
- [ ] No 502/503 errors

---

## 📊 Monitoring Setup

### Logging
- [ ] Logs accessible: `flyctl logs -f`
- [ ] Error tracking configured
- [ ] Request IDs logged
- [ ] Tool call IDs logged

### Alerts (Optional)
- [ ] Health check monitoring
- [ ] Error rate alerts
- [ ] Memory usage alerts
- [ ] Uptime monitoring (e.g., UptimeRobot)

---

## 🔒 Security

### Secrets
- [ ] No secrets in Git
- [ ] Environment variables set via platform
- [ ] API keys rotated (if any)

### Access
- [ ] HTTPS only (automatic with Fly.io)
- [ ] CORS configured correctly
- [ ] Rate limiting considered

---

## 📝 Documentation

### Updated Docs
- [ ] README.md includes production URL
- [ ] DEPLOYMENT.md reviewed
- [ ] Environment variables documented
- [ ] Troubleshooting section complete

### Team Communication
- [ ] Team notified of deployment
- [ ] Production URL shared
- [ ] Known issues documented
- [ ] Rollback procedure documented

---

## 🎯 Golden Prompts Test

Test these prompts in ChatGPT to verify functionality:

### Property Search
- [ ] "Show me properties in DY4 7LG under £100,000"
- [ ] "Find 3-bedroom houses with parking"
- [ ] "What flats are available with gardens?"
- [ ] "Show me the cheapest properties in DY4"

### Calculations
- [ ] "What's the average price for 2-bedroom properties?"
- [ ] "Calculate average price for flats in DY4"

### Lead Capture
- [ ] "I'm looking to buy a 3-bed house, budget £150k"
- [ ] "I want to sell my property at 123 Main St"
- [ ] "Schedule a viewing for property ID 1 tomorrow at 2pm"

### Widget Features
- [ ] Property cards display with images
- [ ] Favorite button works (persists across refreshes)
- [ ] Sort by price works
- [ ] Sort by bedrooms works
- [ ] Dark mode adapts to ChatGPT theme

---

## 🔄 Rollback Plan

If deployment fails:

1. **Check logs**: `flyctl logs`
2. **View releases**: `flyctl releases`
3. **Rollback**: `flyctl releases rollback`
4. **Verify**: Test health endpoint
5. **Investigate**: Review error logs
6. **Fix locally**: Test changes
7. **Redeploy**: `flyctl deploy`

---

## 📞 Support Contacts

- **Platform Support**: Fly.io support (if issues)
- **FastMCP**: https://github.com/jlowin/fastmcp/issues
- **OpenAI Apps SDK**: https://platform.openai.com/docs/mcp

---

## ✅ Sign-Off

Deployment completed by: _______________

Date: _______________

Production URL: _______________

Notes:
_______________________________________________
_______________________________________________
_______________________________________________
