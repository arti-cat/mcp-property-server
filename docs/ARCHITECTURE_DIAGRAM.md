# ChatGPT Apps SDK Widget Architecture

## High-Level Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                          USER                                    │
│                            ↓                                     │
│                  "Show me properties in DY4"                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                        CHATGPT                                   │
│                                                                  │
│  1. Parses user intent                                           │
│  2. Finds matching tool: query_listings                          │
│  3. Detects widget metadata in tool._meta                        │
│  4. Calls MCP server tool                                        │
│  5. Receives response with structuredContent                     │
│  6. Fetches widget HTML from resource                            │
│  7. Renders widget in iframe                                     │
│  8. Injects data into window.openai.toolOutput                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      MCP SERVER                                  │
│                   (server_apps_sdk.py)                           │
│                                                                  │
│  FastMCP Server (stateless_http=True)                            │
│  ├─ list_tools()                                                 │
│  │   └─ Returns tools with _meta fields                          │
│  ├─ list_resources()                                             │
│  │   └─ Returns widget resource                                  │
│  ├─ call_tool_request()                                          │
│  │   └─ Returns {content, structuredContent, _meta}              │
│  └─ read_resource()                                              │
│      └─ Returns widget HTML (CSS + React bundle)                 │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      REACT WIDGET                                │
│                  (PropertyListWidget.tsx)                        │
│                                                                  │
│  1. useToolOutput() reads window.openai.toolOutput              │
│  2. useWidgetState() manages persistent state                    │
│  3. useTheme() reads light/dark mode                             │
│  4. Renders property cards with data                             │
│  5. User clicks favorite → setWidgetState()                      │
│  6. State saved to window.openai.setWidgetState()                │
└─────────────────────────────────────────────────────────────────┘
```

---

## Detailed Component Architecture

### Server Side

```
server_apps_sdk.py
├─ Constants
│  ├─ MIME_TYPE = "text/html+skybridge"
│  └─ WIDGET_URI = "ui://widget/property-list.html"
│
├─ Widget Loading
│  ├─ Load web/dist/component.js (React bundle)
│  ├─ Load web/src/styles/index.css (Styles)
│  └─ Inject into HTML template
│
├─ FastMCP Setup
│  └─ FastMCP(name="PropertyServer", stateless_http=True)
│
├─ Tool Registration
│  └─ list_tools()
│     └─ Tool(
│        name="query_listings",
│        _meta={
│          "openai/outputTemplate": WIDGET_URI,
│          "openai/widgetAccessible": True,
│          "openai/resultCanProduceWidget": True
│        }
│     )
│
├─ Resource Registration
│  └─ list_resources()
│     └─ Resource(
│        uri=WIDGET_URI,
│        mimeType=MIME_TYPE,
│        _meta={...}
│     )
│
├─ Request Handlers
│  ├─ call_tool_request()
│  │  └─ Returns CallToolResult(
│  │     content=[TextContent(...)],      # For LLM
│  │     structuredContent={...},         # For widget
│  │     _meta={...}                      # For ChatGPT
│  │  )
│  │
│  └─ read_resource()
│     └─ Returns widget HTML with CSS + JS
│
└─ HTTP App
   └─ mcp.streamable_http_app()
```

### Client Side

```
web/
├─ src/
│  ├─ index.tsx (Entry Point)
│  │  └─ Renders <PropertyListWidget />
│  │
│  ├─ PropertyListWidget.tsx (Main Component)
│  │  ├─ useToolOutput() → window.openai.toolOutput
│  │  ├─ useWidgetState() → window.openai.widgetState
│  │  ├─ useTheme() → window.openai.theme
│  │  ├─ State: {favorites, sortBy}
│  │  ├─ Logic: sorting, filtering
│  │  └─ Renders: PropertyCard components
│  │
│  ├─ PropertyCard.tsx (Item Display)
│  │  ├─ Props: property, isFavorite, onToggleFavorite
│  │  └─ Renders: image, price, details, favorite button
│  │
│  ├─ EmptyState.tsx (No Results)
│  │  └─ Renders: "No properties found" message
│  │
│  ├─ hooks/
│  │  ├─ useOpenAiGlobal.ts (Core Hook)
│  │  │  └─ useSyncExternalStore + event listeners
│  │  │
│  │  ├─ useToolOutput.ts
│  │  │  └─ useOpenAiGlobal('toolOutput')
│  │  │
│  │  ├─ useWidgetState.ts
│  │  │  ├─ useState + useEffect
│  │  │  └─ Calls window.openai.setWidgetState()
│  │  │
│  │  └─ useTheme.ts
│  │     └─ useOpenAiGlobal('theme')
│  │
│  ├─ types/
│  │  └─ property.ts
│  │     ├─ Property interface
│  │     ├─ ToolOutput interface
│  │     ├─ WidgetState interface
│  │     └─ OpenAiGlobals interface
│  │
│  └─ styles/
│     └─ index.css
│        ├─ CSS variables (light/dark)
│        ├─ Base styles
│        └─ Component styles
│
└─ dist/
   └─ component.js (Built Bundle)
      └─ Minified React + CSS
```

---

## Data Flow Diagram

### Tool Execution Flow

```
1. USER QUERY
   "Show me properties in DY4 under £100k"
          ↓
2. CHATGPT PROCESSING
   ├─ Parses intent
   ├─ Selects tool: query_listings
   ├─ Extracts parameters: {postcode: "DY4", max_price: 100000}
   └─ Detects widget metadata
          ↓
3. MCP TOOL CALL
   POST /mcp/tools/call
   {
     "method": "tools/call",
     "params": {
       "name": "query_listings",
       "arguments": {
         "postcode": "DY4",
         "max_price": 100000,
         "limit": 5
       }
     }
   }
          ↓
4. SERVER PROCESSING
   ├─ tools.query_listings(postcode="DY4", max_price=100000)
   ├─ Queries data/listings.jsonl
   ├─ Filters properties
   └─ Returns structured data
          ↓
5. SERVER RESPONSE
   {
     "content": [
       {"type": "text", "text": "Found 5 properties..."}
     ],
     "structuredContent": {
       "properties": [
         {
           "property_id": "32926983",
           "price_amount": 81995,
           "bedrooms": 1,
           "postcode": "DY4 7LG",
           ...
         },
         ...
       ],
       "filters_applied": {"postcode": "DY4", "max_price": 100000},
       "total_results": 5,
       "showing": 5
     },
     "_meta": {
       "openai/toolInvocation/invoked": "Found properties"
     }
   }
          ↓
6. CHATGPT WIDGET LOADING
   ├─ Reads _meta.openai/outputTemplate
   ├─ Fetches resource: ui://widget/property-list.html
   ├─ GET /mcp/resources/read?uri=ui://widget/property-list.html
   └─ Receives HTML with CSS + React bundle
          ↓
7. WIDGET RENDERING
   ├─ ChatGPT creates iframe
   ├─ Injects HTML into iframe
   ├─ Sets window.openai.toolOutput = structuredContent
   ├─ Sets window.openai.theme = "light" | "dark"
   └─ React initializes
          ↓
8. REACT INITIALIZATION
   ├─ index.tsx creates root
   ├─ PropertyListWidget mounts
   ├─ useToolOutput() reads window.openai.toolOutput
   ├─ useWidgetState() reads window.openai.widgetState
   └─ Renders property cards
          ↓
9. USER INTERACTION
   ├─ User clicks favorite button
   ├─ toggleFavorite(propertyId) called
   ├─ setWidgetState({favorites: [...]})
   └─ window.openai.setWidgetState() persists state
          ↓
10. STATE PERSISTENCE
    ├─ ChatGPT stores widgetState
    ├─ Next widget load: window.openai.widgetState restored
    └─ Favorites persist across sessions
```

---

## Key Interfaces

### Server → ChatGPT

```python
# Tool Metadata
_meta = {
    "openai/outputTemplate": "ui://widget/property-list.html",
    "openai/widgetAccessible": True,
    "openai/resultCanProduceWidget": True,
    "openai/toolInvocation/invoking": "Searching properties...",
    "openai/toolInvocation/invoked": "Found properties"
}

# Tool Response
CallToolResult(
    content=[TextContent(...)],        # For LLM understanding
    structuredContent={...},           # For widget rendering
    _meta={...}                        # For ChatGPT UI
)

# Resource Response
Resource(
    uri="ui://widget/property-list.html",
    mimeType="text/html+skybridge",
    text="<html>...</html>"           # Widget HTML
)
```

### ChatGPT → Widget

```typescript
// window.openai API
interface OpenAiGlobals {
  toolOutput?: {
    properties: Property[];
    filters_applied?: any;
    total_results?: number;
  };
  
  widgetState?: {
    favorites: string[];
    sortBy: string;
  };
  
  theme?: 'light' | 'dark';
  
  setWidgetState?: (state: any) => void;
}
```

### Widget Hooks

```typescript
// Read tool data
const toolOutput = useToolOutput();
// → window.openai.toolOutput

// Manage persistent state
const [state, setState] = useWidgetState({favorites: []});
// → window.openai.widgetState
// → window.openai.setWidgetState()

// Read theme
const theme = useTheme();
// → window.openai.theme
```

---

## Build Process

```
1. WIDGET DEVELOPMENT
   web/src/*.tsx (TypeScript + React)
          ↓
   npm run build (esbuild)
          ↓
   web/dist/component.js (Bundled JS)

2. SERVER LOADING
   server_apps_sdk.py
   ├─ Reads web/dist/component.js
   ├─ Reads web/src/styles/index.css
   └─ Injects into HTML template
          ↓
   WIDGET_HTML = """
   <!DOCTYPE html>
   <html>
   <head>
     <style>{css}</style>
   </head>
   <body>
     <div id="root"></div>
     <script type="module">{js}</script>
   </body>
   </html>
   """

3. RUNTIME SERVING
   ChatGPT requests widget
          ↓
   GET /mcp/resources/read
          ↓
   Server returns WIDGET_HTML
          ↓
   ChatGPT renders in iframe
```

---

## Security & Isolation

```
┌─────────────────────────────────────────┐
│          ChatGPT Domain                  │
│                                          │
│  ┌────────────────────────────────────┐ │
│  │      Widget Iframe (Sandboxed)     │ │
│  │                                    │ │
│  │  • Isolated from ChatGPT DOM      │ │
│  │  • No direct access to user data  │ │
│  │  • Communication via window.openai│ │
│  │  • CSP restrictions apply         │ │
│  └────────────────────────────────────┘ │
│                                          │
│  window.openai API (Controlled Bridge)  │
│  ├─ toolOutput (read-only)              │
│  ├─ widgetState (read/write)            │
│  ├─ theme (read-only)                   │
│  └─ setWidgetState (controlled write)   │
└─────────────────────────────────────────┘
```

---

## Performance Considerations

### Bundle Size
- **Target:** < 500KB
- **Current:** ~150KB (minified)
- **Optimization:** Tree-shaking, minification, no large deps

### Load Time
- **Widget HTML:** Inline CSS + JS (single request)
- **Images:** Lazy loading
- **Data:** Passed via `toolOutput` (no additional requests)

### Rendering
- **React:** Virtual DOM for efficient updates
- **Memoization:** `useMemo` for expensive operations
- **State:** Minimal re-renders with proper hooks

---

## Error Handling

```
Widget Loading Error
├─ Widget bundle not found
│  └─ Server prints: "❌ Widget bundle not found"
│
├─ Widget fails to render
│  └─ React error boundary (optional)
│
└─ Data not available
   └─ Loading state: "Loading properties..."

Tool Execution Error
├─ Tool not found
│  └─ Returns: isError=True
│
├─ Invalid parameters
│  └─ Returns: error message in content
│
└─ Server error
   └─ Returns: HTTP 500 with error details

State Persistence Error
├─ setWidgetState not available
│  └─ Graceful degradation (state not persisted)
│
└─ Invalid state format
   └─ Falls back to default state
```

---

## Testing Strategy

```
1. UNIT TESTING (Widget)
   ├─ Test hooks in isolation
   ├─ Test component rendering
   └─ Test state management

2. INTEGRATION TESTING (Server)
   ├─ Test tool execution
   ├─ Test response format
   └─ Test widget HTML serving

3. E2E TESTING (ChatGPT)
   ├─ Test widget loading
   ├─ Test data display
   ├─ Test interactions
   └─ Test state persistence

4. BROWSER TESTING (Local)
   ├─ Open http://localhost:8000/widget
   ├─ Check console for errors
   ├─ Test with mock data
   └─ Verify styling
```

---

This architecture enables rich, interactive experiences in ChatGPT while maintaining security, performance, and maintainability.
