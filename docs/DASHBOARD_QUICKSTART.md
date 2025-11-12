# Estate Agent Dashboard - Quick Start Guide

## Prerequisites

- Python 3.12+
- Node.js 18+
- PostgreSQL 14+ (or SQLite for development)
- Docker & Docker Compose (optional)
- OpenAI or Anthropic API key

## Quick Setup (15 minutes)

### 1. Clone and Setup Backend

```bash
# Create project directory
mkdir estate-agent-dashboard
cd estate-agent-dashboard

# Create backend structure
mkdir -p backend/{api,mcp_server,database}
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install fastmcp[http] fastapi uvicorn sqlalchemy psycopg2-binary python-jose[cryptography] passlib[bcrypt] python-multipart
```

### 2. Create Minimal MCP Server

Create `backend/mcp_server/server.py`:

```python
from fastmcp import FastMCP
from fastmcp.server.auth import JWTVerifier
import os

# Simple JWT auth (use proper keys in production)
auth = JWTVerifier(
    secret_key=os.getenv("JWT_SECRET", "dev-secret-key"),
    algorithm="HS256",
    audience="estate-dashboard"
)

mcp = FastMCP(
    name="EstateAgentServer",
    auth=auth,
    stateless_http=True
)

# Sample property data (replace with database)
PROPERTIES = [
    {
        "id": "1",
        "title": "Modern 3-Bed House",
        "price": 250000,
        "bedrooms": 3,
        "postcode": "DY4 7LG",
        "status": "available"
    },
    {
        "id": "2",
        "title": "Luxury Apartment",
        "price": 180000,
        "bedrooms": 2,
        "postcode": "LE65 2GH",
        "status": "available"
    }
]

@mcp.tool
def search_properties(
    max_price: int = None,
    min_bedrooms: int = None,
    postcode: str = None
) -> dict:
    """Search properties with filters"""
    results = PROPERTIES.copy()
    
    if max_price:
        results = [p for p in results if p["price"] <= max_price]
    if min_bedrooms:
        results = [p for p in results if p["bedrooms"] >= min_bedrooms]
    if postcode:
        results = [p for p in results if postcode.upper() in p["postcode"]]
    
    return {
        "total": len(results),
        "properties": results
    }

@mcp.tool
def get_property_details(property_id: str) -> dict:
    """Get detailed property information"""
    for prop in PROPERTIES:
        if prop["id"] == property_id:
            return prop
    return {"error": "Property not found"}

@mcp.tool
def update_property_status(property_id: str, status: str) -> dict:
    """Update property status (available/under_offer/sold)"""
    for prop in PROPERTIES:
        if prop["id"] == property_id:
            prop["status"] = status
            return {"success": True, "property": prop}
    return {"error": "Property not found"}

if __name__ == "__main__":
    import uvicorn
    print("🏠 Estate Agent MCP Server starting...")
    print("📍 MCP Endpoint: http://localhost:8001/mcp/")
    
    # Create the app
    app = mcp.streamable_http_app()
    
    # Run server
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        log_level="info"
    )
```

### 3. Create Dashboard API

Create `backend/api/main.py`:

```python
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta

app = FastAPI(title="Estate Agent Dashboard API")

# CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# JWT Configuration
SECRET_KEY = "dev-secret-key"  # Use env var in production
ALGORITHM = "HS256"

# Models
class LoginRequest(BaseModel):
    email: str
    password: str

class PropertyCreate(BaseModel):
    title: str
    price: int
    bedrooms: int
    postcode: str

# Sample data
USERS = {
    "agent@example.com": {
        "id": "user-1",
        "email": "agent@example.com",
        "password": "password123",  # Hash in production!
        "name": "John Agent",
        "role": "agent"
    }
}

PROPERTIES = []

# Auth endpoints
@app.post("/api/auth/login")
def login(request: LoginRequest):
    user = USERS.get(request.email)
    if not user or user["password"] != request.password:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Create JWT token
    token_data = {
        "sub": user["id"],
        "email": user["email"],
        "exp": datetime.utcnow() + timedelta(hours=24)
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm=ALGORITHM)
    
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "name": user["name"],
            "role": user["role"]
        }
    }

# Property endpoints
@app.get("/api/properties")
def list_properties():
    return {"properties": PROPERTIES}

@app.post("/api/properties")
def create_property(property: PropertyCreate):
    new_property = {
        "id": f"prop-{len(PROPERTIES) + 1}",
        **property.dict(),
        "status": "available",
        "created_at": datetime.utcnow().isoformat()
    }
    PROPERTIES.append(new_property)
    return new_property

@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Dashboard API starting...")
    print("📍 API: http://localhost:8000")
    print("📖 Docs: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

### 4. Create Frontend

```bash
# In project root
npx create-vite@latest frontend -- --template react-ts
cd frontend
npm install

# Install dependencies
npm install @tanstack/react-query axios react-router-dom zustand
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

Create `frontend/src/App.tsx`:

```tsx
import { useState } from 'react';
import { QueryClient, QueryClientProvider, useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';

const queryClient = new QueryClient();
const API_URL = 'http://localhost:8000/api';

// API client
const api = axios.create({
  baseURL: API_URL,
});

// Set auth token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Login component
function Login({ onLogin }: { onLogin: (token: string) => void }) {
  const [email, setEmail] = useState('agent@example.com');
  const [password, setPassword] = useState('password123');

  const loginMutation = useMutation({
    mutationFn: async () => {
      const response = await api.post('/auth/login', { email, password });
      return response.data;
    },
    onSuccess: (data) => {
      localStorage.setItem('token', data.access_token);
      onLogin(data.access_token);
    },
  });

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-96">
        <h1 className="text-2xl font-bold mb-6">Estate Agent Dashboard</h1>
        <input
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="Email"
          className="w-full p-2 border rounded mb-4"
        />
        <input
          type="password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          placeholder="Password"
          className="w-full p-2 border rounded mb-4"
        />
        <button
          onClick={() => loginMutation.mutate()}
          disabled={loginMutation.isPending}
          className="w-full bg-blue-600 text-white p-2 rounded hover:bg-blue-700"
        >
          {loginMutation.isPending ? 'Logging in...' : 'Login'}
        </button>
      </div>
    </div>
  );
}

// Dashboard component
function Dashboard() {
  const { data, isLoading } = useQuery({
    queryKey: ['properties'],
    queryFn: async () => {
      const response = await api.get('/properties');
      return response.data.properties;
    },
  });

  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm p-4">
        <h1 className="text-xl font-bold">Estate Agent Dashboard</h1>
      </nav>
      
      <div className="container mx-auto p-6">
        <div className="bg-white rounded-lg shadow p-6 mb-6">
          <h2 className="text-2xl font-bold mb-4">Properties</h2>
          
          {data?.length === 0 ? (
            <p className="text-gray-500">No properties yet. Add your first property!</p>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {data?.map((property: any) => (
                <div key={property.id} className="border rounded-lg p-4">
                  <h3 className="font-bold">{property.title}</h3>
                  <p className="text-gray-600">£{property.price.toLocaleString()}</p>
                  <p className="text-sm text-gray-500">{property.bedrooms} beds • {property.postcode}</p>
                  <span className="inline-block mt-2 px-2 py-1 bg-green-100 text-green-800 text-xs rounded">
                    {property.status}
                  </span>
                </div>
              ))}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-bold mb-4">AI Assistant</h2>
          <div className="bg-blue-50 border border-blue-200 rounded p-4">
            <p className="text-sm text-blue-800 mb-2">
              <strong>MCP Server:</strong> http://localhost:8001/mcp/
            </p>
            <p className="text-sm text-gray-600">
              Use this URL in ChatGPT or Claude to connect the AI assistant to your dashboard.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

// Main App
function App() {
  const [token, setToken] = useState(localStorage.getItem('token'));

  return (
    <QueryClientProvider client={queryClient}>
      {token ? <Dashboard /> : <Login onLogin={setToken} />}
    </QueryClientProvider>
  );
}

export default App;
```

Update `frontend/tailwind.config.js`:

```js
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
  },
  plugins: [],
}
```

Update `frontend/src/index.css`:

```css
@tailwind base;
@tailwind components;
@tailwind utilities;
```

### 5. Run Everything

```bash
# Terminal 1: Run MCP Server
cd backend
source venv/bin/activate
python mcp_server/server.py

# Terminal 2: Run Dashboard API
cd backend
source venv/bin/activate
python api/main.py

# Terminal 3: Run Frontend
cd frontend
npm run dev
```

### 6. Test the Setup

1. **Dashboard**: Open http://localhost:3000
   - Login with: `agent@example.com` / `password123`
   - View the dashboard

2. **API Docs**: Open http://localhost:8000/docs
   - Test API endpoints

3. **MCP Server**: Use with ChatGPT or Claude

### 7. Connect to ChatGPT

```bash
# Expose MCP server with ngrok
ngrok http 8001
```

Then in ChatGPT:
1. Go to Settings → Connectors
2. Create new connector
3. URL: `https://your-ngrok-url.ngrok-free.dev/mcp/`
4. Test with: "Search for properties under £200k"

### 8. Connect to Claude Desktop

Add to `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "estate-agent": {
      "command": "python",
      "args": ["/absolute/path/to/backend/mcp_server/server.py"]
    }
  }
}
```

## Next Steps

### Add Database Support

```bash
pip install sqlalchemy alembic psycopg2-binary
```

Create `backend/database/models.py`:

```python
from sqlalchemy import Column, String, Integer, Boolean, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

Base = declarative_base()

class Property(Base):
    __tablename__ = "properties"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False)
    description = Column(String)
    price = Column(Integer, nullable=False)
    bedrooms = Column(Integer)
    bathrooms = Column(Integer)
    postcode = Column(String)
    address = Column(String)
    property_type = Column(String)
    has_garden = Column(Boolean, default=False)
    has_parking = Column(Boolean, default=False)
    status = Column(String, default="available")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Client(Base):
    __tablename__ = "clients"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    email = Column(String)
    mobile = Column(String)
    role = Column(String)  # buyer, seller
    stage = Column(String)  # hot, warm, cold
    budget_max = Column(Integer)
    min_bedrooms = Column(Integer)
    created_at = Column(DateTime, default=datetime.utcnow)
```

### Add More MCP Tools

```python
@mcp.tool
def create_client(
    full_name: str,
    email: str,
    mobile: str,
    role: str,
    budget_max: int = None
) -> dict:
    """Create new client record"""
    # Add to database
    return {"success": True, "client_id": "C0001"}

@mcp.tool
def match_properties_to_client(client_id: str) -> dict:
    """Find properties matching client preferences"""
    # Query database
    return {"matches": [...]}

@mcp.tool
def schedule_viewing(
    property_id: str,
    client_id: str,
    datetime_iso: str
) -> dict:
    """Schedule property viewing"""
    # Add to database
    return {"success": True, "viewing_id": "V0001"}
```

### Add Authentication

```python
from fastmcp.server.auth import JWTVerifier

auth = JWTVerifier(
    secret_key=os.getenv("JWT_SECRET"),
    algorithm="HS256",
    audience="estate-dashboard"
)

mcp = FastMCP(name="EstateAgentServer", auth=auth)
```

### Deploy to Production

See `ESTATE_AGENT_DASHBOARD.md` for full deployment guide.

## Troubleshooting

### MCP Server Not Connecting

```bash
# Check server is running
curl http://localhost:8001/health

# Check MCP endpoint
curl http://localhost:8001/mcp/
```

### CORS Errors

Update `backend/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### JWT Token Issues

```python
# Verify token
import jwt
token = "your-token"
decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
print(decoded)
```

## Resources

- Full Documentation: `docs/ESTATE_AGENT_DASHBOARD.md`
- FastMCP Docs: https://gofastmcp.com
- OpenAI MCP: https://platform.openai.com/docs/mcp
- Anthropic MCP: https://docs.anthropic.com/en/docs/agents-and-tools/mcp-connector

## Support

Questions? Check the main documentation or create an issue.
