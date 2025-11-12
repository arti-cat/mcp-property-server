# Estate Agent Dashboard with AI Integration

## 🎯 Project Overview

Build a comprehensive estate agent dashboard that combines traditional web UI with AI-powered assistance through MCP (Model Context Protocol) integration. This allows estate agents to manage properties, clients, and viewings using both a familiar web interface and natural language AI commands.

## 📚 Documentation

### Getting Started
1. **[DASHBOARD_VS_WIDGET.md](docs/DASHBOARD_VS_WIDGET.md)** - Start here!
   - Understand the difference between your current ChatGPT widget and the proposed dashboard
   - Compare features, costs, and use cases
   - Choose the right implementation path

2. **[DASHBOARD_QUICKSTART.md](docs/DASHBOARD_QUICKSTART.md)** - Build in 15 minutes
   - Minimal working example
   - Step-by-step setup
   - Test with ChatGPT or Claude

3. **[ESTATE_AGENT_DASHBOARD.md](docs/ESTATE_AGENT_DASHBOARD.md)** - Complete guide
   - Full architecture and features
   - Database schema
   - Deployment instructions
   - Production-ready patterns

### Key Concepts

#### What is MCP?
Model Context Protocol (MCP) is a standard that connects AI models to external tools and data. It allows ChatGPT, Claude, and other AI assistants to interact with your dashboard data through natural language.

#### How It Works
```
Estate Agent → "Show me hot leads this week"
     ↓
AI Model (GPT-4/Claude)
     ↓
MCP Server (your tools)
     ↓
Database Query
     ↓
Results → AI → Natural Language Response
```

## 🏗️ Architecture

### System Components

```
┌─────────────────────────────────────────────────────────┐
│           Estate Agent Dashboard (React)                │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐            │
│  │Properties│  │   CRM    │  │Analytics │            │
│  └──────────┘  └──────────┘  └──────────┘            │
│  ┌───────────────────────────────────────┐            │
│  │      AI Chat Assistant (Embedded)     │            │
│  └───────────────────────────────────────┘            │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
            ┌─────────────────┐
            │  Dashboard API  │
            │   (FastAPI)     │
            └─────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌───────────────┐         ┌──────────────┐
│  MCP Server   │         │   Database   │
│  (FastMCP)    │◄────────│  PostgreSQL  │
└───────────────┘         └──────────────┘
        │
        ▼
┌───────────────┐
│  AI Models    │
│  OpenAI/      │
│  Anthropic/   │
│  Gemini       │
└───────────────┘
```

### Current State ✅

You already have:
- ✅ MCP server with property and CRM tools
- ✅ ChatGPT widget with React components
- ✅ Property data (475 listings)
- ✅ Lead capture and matching tools
- ✅ Viewing scheduling
- ✅ Deployment configuration (Fly.io)

### What's New 🆕

The dashboard adds:
- 🆕 Traditional web interface for agents
- 🆕 Multi-user authentication and roles
- 🆕 Property CRUD operations
- 🆕 Analytics and reporting
- 🆕 Embedded AI chat assistant
- 🆕 Complete CRM system

## 🚀 Quick Start

### Option 1: Minimal Dashboard (15 minutes)

```bash
# Follow DASHBOARD_QUICKSTART.md
cd estate-agent-dashboard
python backend/mcp_server/server.py  # Terminal 1
python backend/api/main.py           # Terminal 2
cd frontend && npm run dev           # Terminal 3
```

Open http://localhost:3000

### Option 2: Use Current Setup

Your existing MCP server already works! Just expose it:

```bash
# Run your current server
python server_apps_sdk.py

# Expose with ngrok
ngrok http 8000

# Use in ChatGPT or Claude
# URL: https://your-url.ngrok.io/mcp/
```

## 💡 Use Cases

### For Estate Agents

**Traditional UI:**
- Browse and manage properties
- View client pipeline
- Schedule viewings
- Generate reports

**AI Assistant:**
- "Show me properties under £200k in DY4"
- "Find matches for client Sarah Mitchell"
- "Schedule viewing for property 32926983 tomorrow at 2pm"
- "Draft email to confirm viewing"

### For Agency Owners

**Dashboard:**
- Team performance metrics
- Sales pipeline overview
- Market trends and analytics
- Activity audit logs

**AI Insights:**
- "What's our conversion rate this month?"
- "Show me top performing agents"
- "Analyze pricing trends in LE65"

## 🔧 Technology Stack

### Frontend
- React 18 + TypeScript
- TailwindCSS + shadcn/ui
- React Query for data fetching
- React Router for navigation

### Backend
- FastAPI (Python 3.12+)
- FastMCP 2.13+ for MCP server
- SQLAlchemy for database ORM
- JWT authentication

### AI Integration
- OpenAI Responses API
- Anthropic Messages API
- Google Gemini SDK
- MCP Protocol

### Deployment
- Docker + Docker Compose
- Fly.io / Railway / Self-hosted
- PostgreSQL database
- Nginx reverse proxy

## 📊 Features

### Property Management
- ✅ Full CRUD operations
- ✅ Image gallery management
- ✅ Status tracking (available/under offer/sold)
- ✅ Advanced filtering and search
- ✅ Bulk import/export

### CRM System
- ✅ Client management (buyers/sellers)
- ✅ Lead tracking and pipeline
- ✅ Viewing scheduling
- ✅ Communication history
- ✅ Task reminders
- ✅ Client-property matching

### AI Assistant
- ✅ Natural language queries
- ✅ Conversational property search
- ✅ Automated client matching
- ✅ Market insights
- ✅ Email drafting
- ✅ Multi-model support

### Analytics
- ✅ Sales pipeline visualization
- ✅ Market trends
- ✅ Agent performance
- ✅ Custom reports
- ✅ Export to PDF/Excel

### Multi-User
- ✅ Role-based access (Admin/Agent/Viewer)
- ✅ Team collaboration
- ✅ Activity logging
- ✅ User preferences

## 🔐 Security

### Authentication
- JWT tokens with refresh
- OAuth2 support
- Role-based access control
- Session management

### MCP Server Security
```python
from fastmcp.server.auth import JWTVerifier

auth = JWTVerifier(
    secret_key=os.getenv("JWT_SECRET"),
    algorithm="HS256",
    audience="estate-dashboard"
)

mcp = FastMCP(name="EstateAgentServer", auth=auth)
```

### Multi-Tenant Support
```python
@mcp.tool
async def search_properties(ctx: Context) -> list:
    # Automatically scoped to user's agency
    agency_id = ctx.request_context.agency_id
    return db.query(Property).filter(
        Property.agency_id == agency_id
    ).all()
```

## 📈 Implementation Paths

### Path A: Quick Win (1-2 weeks)
- Minimal dashboard with AI chat
- Basic property management
- Simple authentication
- Deploy to Fly.io

**Best for**: Testing the concept, MVP

### Path B: Full Solution (4-6 weeks)
- Complete feature set
- Production-ready
- Multi-user with roles
- Analytics and reporting

**Best for**: Production deployment, scaling

### Path C: Hybrid (2-3 weeks)
- Agent dashboard (internal)
- ChatGPT widget (public)
- Shared MCP server
- Different permissions

**Best for**: Both internal and public-facing tools

## 💰 Cost Estimates

### Infrastructure
- **Development**: $5-10/month (Fly.io free tier)
- **Production**: $20-50/month (database + hosting)

### AI Usage
- **OpenAI**: ~$0.01-0.10 per query
- **Anthropic**: ~$0.01-0.15 per query
- **Estimated**: $10-100/month depending on usage

### Total
- **Small agency**: $30-60/month
- **Medium agency**: $60-150/month
- **Large agency**: $150-300/month

## 🎓 Learning Resources

### MCP Protocol
- [FastMCP Documentation](https://gofastmcp.com)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [FastMCP Examples](https://github.com/jlowin/fastmcp)

### AI Integration
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
- [Anthropic MCP Guide](https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector)
- [ChatGPT Apps SDK](https://platform.openai.com/docs/mcp)

### Your Documentation
- `docs/external/fastmcp/` - FastMCP integration guides
- `docs/external/custom-ui.md` - ChatGPT widget development
- `docs/templates/` - Reusable widget patterns

## 🤝 How to Proceed

### Step 1: Understand the Difference
Read `docs/DASHBOARD_VS_WIDGET.md` to understand:
- What you already have (ChatGPT widget)
- What the dashboard adds
- Which approach fits your needs

### Step 2: Choose Your Path
- **Quick test?** → Follow `DASHBOARD_QUICKSTART.md`
- **Full build?** → Study `ESTATE_AGENT_DASHBOARD.md`
- **Extend current?** → Add tools to `server_apps_sdk.py`

### Step 3: Start Building
```bash
# Clone the quickstart
# Customize for your needs
# Deploy and test
# Iterate based on feedback
```

## 📝 Example Queries

### Property Management
```
"Show me all properties under £200k in DY4"
"Update property 32926983 status to under offer"
"Add new property: 3-bed house in LE65 for £250k"
"Generate marketing description for property 12345"
```

### CRM
```
"Show me hot leads this week"
"Find properties matching client Sarah Mitchell"
"Schedule viewing for property 32926983 tomorrow at 2pm"
"What's the status of client C0001?"
```

### Analytics
```
"What's our average sale price in DY4?"
"Show me conversion rates this month"
"Which agent has the most viewings?"
"Analyze pricing trends in LE65"
```

### Communication
```
"Draft viewing confirmation email for property 32926983"
"Create property brochure for listing 12345"
"Send follow-up to client C0001"
```

## 🐛 Troubleshooting

### MCP Server Not Connecting
```bash
# Check server is running
curl http://localhost:8001/health

# Check MCP endpoint
curl http://localhost:8001/mcp/
```

### Authentication Issues
```bash
# Verify JWT token
python -c "import jwt; print(jwt.decode('token', 'secret', algorithms=['HS256']))"
```

### Database Connection
```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d estate_agent_db
```

See `DASHBOARD_QUICKSTART.md` for more troubleshooting tips.

## 🎯 Next Steps

1. **Read** `docs/DASHBOARD_VS_WIDGET.md` - Understand the options
2. **Try** `docs/DASHBOARD_QUICKSTART.md` - Build minimal version
3. **Study** `docs/ESTATE_AGENT_DASHBOARD.md` - Plan full implementation
4. **Build** - Start with MVP, iterate based on feedback
5. **Deploy** - Use Fly.io or your preferred platform

## 📞 Support

- **Documentation**: See `docs/` folder
- **Examples**: Check `docs/external/` for integration guides
- **Issues**: Create GitHub issue
- **Questions**: Check FastMCP docs or MCP protocol spec

## 🎉 Success Criteria

You'll know it's working when:
- ✅ Dashboard loads at http://localhost:3000
- ✅ You can login and see properties
- ✅ MCP server responds to AI queries
- ✅ ChatGPT/Claude can search properties
- ✅ Agents can manage data through UI
- ✅ AI assistant provides helpful responses

## 🚀 Ready to Build?

Start with the quickstart guide and build your first AI-powered estate agent dashboard in 15 minutes!

```bash
# Let's go!
cat docs/DASHBOARD_QUICKSTART.md
```

Good luck! 🏠✨
