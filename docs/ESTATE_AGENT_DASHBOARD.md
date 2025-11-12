# Estate Agent Dashboard with AI Integration

## Overview

A comprehensive estate agent dashboard that combines property management, CRM functionality, and AI-powered assistance through MCP (Model Context Protocol) integration. This allows estate agents to interact with their data using natural language while maintaining a traditional web interface.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Estate Agent Dashboard                    │
│                      (Web Application)                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │   Property   │  │     CRM      │  │      AI      │      │
│  │  Management  │  │  Management  │  │   Assistant  │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│         │                 │                  │               │
│         └─────────────────┴──────────────────┘               │
│                           │                                   │
│                           ▼                                   │
│                  ┌─────────────────┐                         │
│                  │   Dashboard API │                         │
│                  │   (FastAPI)     │                         │
│                  └─────────────────┘                         │
│                           │                                   │
└───────────────────────────┼───────────────────────────────────┘
                            │
                ┌───────────┴───────────┐
                │                       │
                ▼                       ▼
        ┌───────────────┐      ┌──────────────┐
        │  MCP Server   │      │   Database   │
        │  (FastMCP)    │      │  (SQLite/    │
        │               │      │  PostgreSQL) │
        └───────────────┘      └──────────────┘
                │
                ▼
        ┌───────────────┐
        │  AI Models    │
        │  (OpenAI/     │
        │  Anthropic)   │
        └───────────────┘
```

## Key Features

### 1. **Property Management**
- Property listings with full CRUD operations
- Image gallery management
- Property status tracking (available, under offer, sold)
- Bulk import/export capabilities
- Advanced filtering and search

### 2. **CRM System**
- Client management (buyers and sellers)
- Lead tracking and pipeline management
- Viewing scheduling with conflict detection
- Communication history
- Task and follow-up reminders
- Client matching to properties

### 3. **AI Assistant Integration**
- Natural language queries via MCP server
- Conversational property search
- Automated client matching
- Market insights and analytics
- Email and document generation
- Multi-modal support (OpenAI, Anthropic, Gemini)

### 4. **Analytics & Reporting**
- Sales pipeline visualization
- Market trends and pricing analytics
- Agent performance metrics
- Custom report generation
- Export to PDF/Excel

### 5. **Multi-User Support**
- Role-based access control (Admin, Agent, Viewer)
- Team collaboration features
- Activity logging and audit trails
- User preferences and settings

## Technology Stack

### Frontend
- **Framework**: React 18+ with TypeScript
- **UI Library**: shadcn/ui + TailwindCSS
- **State Management**: Zustand or React Query
- **Routing**: React Router v6
- **Charts**: Recharts or Chart.js
- **Forms**: React Hook Form + Zod validation
- **Icons**: Lucide React

### Backend
- **API Framework**: FastAPI (Python 3.12+)
- **MCP Server**: FastMCP 2.13+
- **Database**: PostgreSQL (production) / SQLite (development)
- **ORM**: SQLAlchemy 2.0
- **Authentication**: JWT with OAuth2 support
- **File Storage**: Local filesystem or S3-compatible storage

### AI Integration
- **MCP Protocol**: Model Context Protocol
- **Supported Models**: 
  - OpenAI (GPT-4, GPT-4 Turbo)
  - Anthropic (Claude 3.5 Sonnet)
  - Google (Gemini Pro)
- **Transport**: Streamable HTTP for remote access

### Deployment
- **Containerization**: Docker + Docker Compose
- **Hosting**: Fly.io, Railway, or self-hosted
- **Reverse Proxy**: Nginx or Caddy
- **SSL**: Let's Encrypt via Caddy

## MCP Server Integration

### How It Works

The MCP server acts as a bridge between AI models and your dashboard data:

1. **Estate agent asks a question** in ChatGPT, Claude, or the dashboard AI chat
2. **AI model calls MCP tools** to fetch/update data
3. **MCP server executes operations** on the database
4. **Results returned to AI** for natural language response
5. **Optional: Custom UI widgets** render interactive components

### MCP Tools for Dashboard

```python
# Property Tools
@mcp.tool
def search_properties(filters: dict) -> list[Property]:
    """Search properties with advanced filters"""

@mcp.tool
def get_property_details(property_id: str) -> Property:
    """Get detailed property information"""

@mcp.tool
def update_property_status(property_id: str, status: str) -> dict:
    """Update property status (available/under_offer/sold)"""

# CRM Tools
@mcp.tool
def create_client(client_data: dict) -> Client:
    """Create new client record"""

@mcp.tool
def match_clients_to_property(property_id: str) -> list[Client]:
    """Find clients matching property criteria"""

@mcp.tool
def schedule_viewing(property_id: str, client_id: str, datetime: str) -> Viewing:
    """Schedule property viewing"""

@mcp.tool
def get_pipeline_summary() -> dict:
    """Get sales pipeline overview"""

# Analytics Tools
@mcp.tool
def get_market_insights(postcode: str) -> dict:
    """Get market trends and pricing for area"""

@mcp.tool
def generate_property_report(property_id: str) -> dict:
    """Generate comprehensive property report"""

# Communication Tools
@mcp.tool
def draft_email(template: str, context: dict) -> str:
    """Draft email using template and context"""

@mcp.tool
def generate_property_description(property_id: str) -> str:
    """Generate marketing description for property"""
```

### Authentication & Security

```python
from fastmcp.server.auth import JWTVerifier
from fastmcp.server.auth.providers.bearer import BearerTokenProvider

# JWT-based authentication
auth = JWTVerifier(
    public_key=PUBLIC_KEY,
    audience="estate-agent-dashboard",
    issuer="your-domain.com"
)

mcp = FastMCP(
    name="EstateAgentServer",
    auth=auth,
    stateless_http=True
)
```

### Multi-Tenant Support

```python
from fastmcp.server.context import Context

@mcp.tool
async def search_properties(
    filters: dict,
    ctx: Context = None
) -> list[Property]:
    """Search properties - scoped to authenticated user's agency"""
    # Extract user/agency from JWT token
    user_id = ctx.request_context.user_id
    agency_id = ctx.request_context.agency_id
    
    # Query only properties belonging to this agency
    return db.query(Property).filter(
        Property.agency_id == agency_id
    ).all()
```

## Dashboard Implementation

### Project Structure

```
estate-agent-dashboard/
├── backend/
│   ├── api/
│   │   ├── routes/
│   │   │   ├── properties.py
│   │   │   ├── clients.py
│   │   │   ├── viewings.py
│   │   │   ├── analytics.py
│   │   │   └── auth.py
│   │   ├── models/
│   │   │   ├── property.py
│   │   │   ├── client.py
│   │   │   ├── viewing.py
│   │   │   └── user.py
│   │   ├── schemas/
│   │   │   └── ...
│   │   └── main.py
│   ├── mcp_server/
│   │   ├── server.py
│   │   ├── tools/
│   │   │   ├── property_tools.py
│   │   │   ├── crm_tools.py
│   │   │   ├── analytics_tools.py
│   │   │   └── communication_tools.py
│   │   └── widgets/
│   │       └── property_widget.py
│   ├── database/
│   │   ├── connection.py
│   │   ├── migrations/
│   │   └── seed.py
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── properties/
│   │   │   ├── clients/
│   │   │   ├── analytics/
│   │   │   ├── ai-chat/
│   │   │   └── common/
│   │   ├── pages/
│   │   │   ├── Dashboard.tsx
│   │   │   ├── Properties.tsx
│   │   │   ├── Clients.tsx
│   │   │   ├── Analytics.tsx
│   │   │   └── Settings.tsx
│   │   ├── hooks/
│   │   ├── services/
│   │   │   ├── api.ts
│   │   │   └── mcp.ts
│   │   ├── stores/
│   │   ├── types/
│   │   └── App.tsx
│   ├── package.json
│   └── Dockerfile
├── docker-compose.yml
├── .env.example
└── README.md
```

### Database Schema

```sql
-- Users & Authentication
CREATE TABLE users (
    id UUID PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50), -- admin, agent, viewer
    agency_id UUID,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Agencies (Multi-tenant support)
CREATE TABLE agencies (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    logo_url VARCHAR(500),
    created_at TIMESTAMP DEFAULT NOW()
);

-- Properties
CREATE TABLE properties (
    id UUID PRIMARY KEY,
    agency_id UUID REFERENCES agencies(id),
    external_id VARCHAR(100), -- From data feed
    title VARCHAR(500),
    description TEXT,
    property_type VARCHAR(100),
    price INTEGER,
    bedrooms INTEGER,
    bathrooms INTEGER,
    postcode VARCHAR(20),
    address TEXT,
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    has_garden BOOLEAN,
    has_parking BOOLEAN,
    status VARCHAR(50), -- available, under_offer, sold, withdrawn
    images JSONB, -- Array of image URLs
    features JSONB, -- Array of features
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Clients
CREATE TABLE clients (
    id UUID PRIMARY KEY,
    agency_id UUID REFERENCES agencies(id),
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255),
    mobile VARCHAR(50),
    role VARCHAR(50), -- buyer, seller
    stage VARCHAR(50), -- hot, warm, cold, instructed, completed
    budget_min INTEGER,
    budget_max INTEGER,
    min_bedrooms INTEGER,
    preferred_postcodes TEXT[],
    notes TEXT,
    assigned_agent_id UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Viewings
CREATE TABLE viewings (
    id UUID PRIMARY KEY,
    property_id UUID REFERENCES properties(id),
    client_id UUID REFERENCES clients(id),
    agent_id UUID REFERENCES users(id),
    scheduled_at TIMESTAMP NOT NULL,
    status VARCHAR(50), -- scheduled, completed, cancelled, no_show
    feedback TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Activity Log
CREATE TABLE activity_log (
    id UUID PRIMARY KEY,
    agency_id UUID REFERENCES agencies(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(100),
    entity_type VARCHAR(50), -- property, client, viewing
    entity_id UUID,
    details JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Indexes
CREATE INDEX idx_properties_agency ON properties(agency_id);
CREATE INDEX idx_properties_status ON properties(status);
CREATE INDEX idx_properties_postcode ON properties(postcode);
CREATE INDEX idx_clients_agency ON clients(agency_id);
CREATE INDEX idx_clients_stage ON clients(stage);
CREATE INDEX idx_viewings_property ON viewings(property_id);
CREATE INDEX idx_viewings_client ON viewings(client_id);
CREATE INDEX idx_viewings_scheduled ON viewings(scheduled_at);
```

## AI Chat Interface

### Embedded Chat Component

```tsx
// src/components/ai-chat/AIChat.tsx
import { useState } from 'react';
import { useOpenAI } from '@/hooks/useOpenAI';

export function AIChat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const { sendMessage, isLoading } = useOpenAI();

  const handleSend = async () => {
    if (!input.trim()) return;
    
    const userMessage = { role: 'user', content: input };
    setMessages(prev => [...prev, userMessage]);
    setInput('');
    
    // Send to OpenAI with MCP server configured
    const response = await sendMessage(input);
    setMessages(prev => [...prev, response]);
  };

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg, idx) => (
          <MessageBubble key={idx} message={msg} />
        ))}
      </div>
      
      <div className="border-t p-4">
        <div className="flex gap-2">
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Ask about properties, clients, or analytics..."
            className="flex-1 px-4 py-2 border rounded-lg"
          />
          <button
            onClick={handleSend}
            disabled={isLoading}
            className="px-6 py-2 bg-blue-600 text-white rounded-lg"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
```

### OpenAI Integration with MCP

```typescript
// src/services/openai.ts
import OpenAI from 'openai';

const client = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

export async function sendMessageWithMCP(
  message: string,
  mcpServerUrl: string,
  authToken: string
) {
  const response = await client.responses.create({
    model: 'gpt-4.1',
    tools: [
      {
        type: 'mcp',
        server_label: 'estate_agent_server',
        server_url: mcpServerUrl,
        require_approval: 'never',
        headers: {
          Authorization: `Bearer ${authToken}`
        }
      }
    ],
    input: message,
  });

  return response.output_text;
}
```

### Anthropic Integration with MCP

```typescript
// src/services/anthropic.ts
import Anthropic from '@anthropic-ai/sdk';

const client = new Anthropic({
  apiKey: process.env.ANTHROPIC_API_KEY,
});

export async function sendMessageWithMCP(
  message: string,
  mcpServerUrl: string,
  authToken: string
) {
  const response = await client.beta.messages.create({
    model: 'claude-sonnet-4-20250514',
    max_tokens: 4096,
    messages: [{ role: 'user', content: message }],
    mcp_servers: [
      {
        type: 'url',
        url: mcpServerUrl,
        name: 'estate-agent-server',
        authorization_token: authToken
      }
    ],
    extra_headers: {
      'anthropic-beta': 'mcp-client-2025-04-04'
    }
  });

  return response.content;
}
```

## Deployment Guide

### Docker Compose Setup

```yaml
# docker-compose.yml
version: '3.8'

services:
  postgres:
    image: postgres:16
    environment:
      POSTGRES_DB: estate_agent_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  backend:
    build: ./backend
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/estate_agent_db
      JWT_SECRET: ${JWT_SECRET}
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
    ports:
      - "8000:8000"
    depends_on:
      - postgres

  mcp-server:
    build: ./backend
    command: python -m mcp_server.server
    environment:
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/estate_agent_db
      JWT_SECRET: ${JWT_SECRET}
    ports:
      - "8001:8001"
    depends_on:
      - postgres

  frontend:
    build: ./frontend
    environment:
      VITE_API_URL: http://localhost:8000
      VITE_MCP_URL: http://localhost:8001
    ports:
      - "3000:3000"
    depends_on:
      - backend

  nginx:
    image: nginx:alpine
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - frontend
      - backend
      - mcp-server

volumes:
  postgres_data:
```

### Environment Variables

```bash
# .env
# Database
DB_PASSWORD=your_secure_password

# Authentication
JWT_SECRET=your_jwt_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI APIs
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...

# Application
ENVIRONMENT=production
FRONTEND_URL=https://yourdomain.com
MCP_SERVER_URL=https://mcp.yourdomain.com

# Email (optional)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your@email.com
SMTP_PASSWORD=your_password
```

### Fly.io Deployment

```bash
# Deploy backend + MCP server
cd backend
fly launch --no-deploy
fly secrets set DATABASE_URL=... JWT_SECRET=... OPENAI_API_KEY=...
fly deploy

# Deploy frontend
cd frontend
fly launch --no-deploy
fly deploy
```

## Usage Examples

### Example 1: Natural Language Property Search

**User**: "Show me 3-bedroom houses under £250k in the DY4 area with parking"

**AI Response**: 
- Calls `search_properties()` MCP tool
- Returns formatted list with property cards
- Displays interactive widget in ChatGPT

### Example 2: Client Matching

**User**: "Find properties for Sarah Mitchell (client C0001)"

**AI Response**:
- Calls `get_client_details()` to fetch preferences
- Calls `match_clients_to_property()` to find matches
- Returns personalized property recommendations

### Example 3: Pipeline Analysis

**User**: "Show me my hot leads this week"

**AI Response**:
- Calls `get_pipeline_summary()` with filters
- Returns formatted list of hot leads
- Suggests follow-up actions

### Example 4: Automated Email

**User**: "Draft a viewing confirmation email for property 32926983 and client C0001"

**AI Response**:
- Calls `get_property_details()` and `get_client_details()`
- Calls `draft_email()` with template
- Returns ready-to-send email

## Benefits

### For Estate Agents
- ✅ **Faster workflows** - Natural language commands instead of clicking
- ✅ **Better client service** - Quick property matching and insights
- ✅ **Mobile-friendly** - Use ChatGPT app on the go
- ✅ **Always available** - AI assistant works 24/7

### For Agency Owners
- ✅ **Data-driven decisions** - AI-powered analytics and insights
- ✅ **Improved efficiency** - Automate repetitive tasks
- ✅ **Better tracking** - Complete audit trail of activities
- ✅ **Scalable** - Multi-tenant architecture

### For Clients
- ✅ **Faster responses** - Agents can answer queries instantly
- ✅ **Better matches** - AI-powered property recommendations
- ✅ **Transparency** - Real-time updates on viewings and offers

## Next Steps

1. **Phase 1: Core Dashboard** (2-3 weeks)
   - Set up project structure
   - Implement authentication
   - Build property and client CRUD
   - Basic analytics

2. **Phase 2: MCP Integration** (1-2 weeks)
   - Deploy MCP server
   - Implement core tools
   - Test with OpenAI/Anthropic
   - Add custom widgets

3. **Phase 3: Advanced Features** (2-3 weeks)
   - Advanced analytics
   - Email automation
   - Document generation
   - Mobile app (optional)

4. **Phase 4: Polish & Deploy** (1 week)
   - User testing
   - Performance optimization
   - Production deployment
   - Documentation

## Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [OpenAI Responses API](https://platform.openai.com/docs/api-reference/responses)
- [Anthropic MCP Guide](https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [ChatGPT Apps SDK](https://platform.openai.com/docs/mcp)

## Support

For questions or issues:
- GitHub Issues: [Your repo]
- Email: support@yourdomain.com
- Documentation: https://docs.yourdomain.com
