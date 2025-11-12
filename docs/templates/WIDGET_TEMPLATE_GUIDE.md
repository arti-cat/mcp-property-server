# ChatGPT Apps SDK Widget Template Guide

**Purpose:** Reusable patterns and templates for creating ChatGPT Apps SDK widgets for MCP servers.

**Based on:** Successful Property MCP Server widget implementation (Nov 2025)

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Server-Side Template](#server-side-template)
3. [Client-Side Template](#client-side-template)
4. [Reusable Hooks](#reusable-hooks)
5. [Project Structure](#project-structure)
6. [Quick Start Checklist](#quick-start-checklist)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                         ChatGPT                              │
│  1. User asks question                                       │
│  2. Detects widget metadata in tool                          │
│  3. Calls MCP tool                                           │
│  4. Fetches widget HTML from resource                        │
│  5. Renders widget in iframe                                 │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      MCP Server                              │
│  • FastMCP with stateless_http=True                          │
│  • Custom request handlers                                   │
│  • Returns: {content, structuredContent, _meta}              │
│  • Serves widget HTML with CSS + React bundle                │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    React Widget                              │
│  • Reads: window.openai.toolOutput                           │
│  • Manages: window.openai.widgetState                        │
│  • Renders: Custom UI with your data                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Server-Side Template

### 1. FastMCP Server Setup

```python
"""
Template MCP Server with Apps SDK Widget Support
Replace [YOUR_*] placeholders with your specific values
"""
from pathlib import Path
from typing import Any, Dict, List
import mcp.types as types
from mcp.server.fastmcp import FastMCP
import json

# --- Constants ---
MIME_TYPE = "text/html+skybridge"
WIDGET_URI = "ui://widget/[YOUR_WIDGET_NAME].html"

# --- Load Widget Bundle ---
WIDGET_HTML = ""
widget_path = Path("web/dist/component.js")
css_path = Path("web/src/styles/index.css")

if widget_path.exists():
    widget_js = widget_path.read_text(encoding="utf-8")
    widget_css = ""
    
    if css_path.exists():
        widget_css = css_path.read_text(encoding="utf-8")
        print(f"✅ Widget CSS loaded: {len(widget_css):,} bytes")
    
    WIDGET_HTML = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>{widget_css}</style>
</head>
<body>
    <div id="root"></div>
    <script type="module">{widget_js}</script>
</body>
</html>"""
    print(f"✅ Widget bundle loaded: {len(widget_js):,} bytes")
else:
    print("❌ Widget bundle not found")

# --- Create FastMCP Server ---
mcp = FastMCP(
    name="[YOUR_SERVER_NAME]",
    stateless_http=True,  # REQUIRED for ChatGPT
)

# --- Helper Functions ---
def _tool_meta() -> Dict[str, Any]:
    """Apps SDK metadata for tools that produce widgets."""
    return {
        "openai/outputTemplate": WIDGET_URI,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "openai/toolInvocation/invoking": "[YOUR_LOADING_MESSAGE]...",
        "openai/toolInvocation/invoked": "[YOUR_SUCCESS_MESSAGE]",
    }

# --- Register Tools ---
@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    """List tools with Apps SDK annotations."""
    return [
        types.Tool(
            name="[your_tool_name]",
            title="[Your Tool Title]",
            description="[Detailed description for when to use this tool]",
            inputSchema={
                "type": "object",
                "properties": {
                    # Your tool parameters
                }
            },
            _meta=_tool_meta(),  # Add widget metadata
            annotations={
                "readOnlyHint": True,  # Skip confirmation prompts
                "destructiveHint": False,
                "openWorldHint": False,
            },
        ),
    ]

# --- Register Resources ---
@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    """List widget resource."""
    return [
        types.Resource(
            name="[Your Widget Name]",
            title="[Your Widget Title]",
            uri=WIDGET_URI,
            description="[Widget description]",
            mimeType=MIME_TYPE,
            _meta=_tool_meta(),
        )
    ]

# --- Custom Resource Handler ---
async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    """Serve widget HTML."""
    if str(req.params.uri) != WIDGET_URI:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )
    
    contents = [
        types.TextResourceContents(
            uri=WIDGET_URI,
            mimeType=MIME_TYPE,
            text=WIDGET_HTML,
            _meta=_tool_meta(),
        )
    ]
    
    return types.ServerResult(types.ReadResourceResult(contents=contents))

# --- Custom Tool Handler ---
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    """Handle tool calls with Apps SDK format."""
    tool_name = req.params.name
    arguments = req.params.arguments or {}
    
    if tool_name == "[your_tool_name]":
        # Your tool logic here
        result = your_tool_function(**arguments)
        
        # Apps SDK format: content + structuredContent + _meta
        return types.ServerResult(
            types.CallToolResult(
                content=[
                    types.TextContent(
                        type="text",
                        text="[Human-readable summary for LLM]",
                    )
                ],
                structuredContent=result,  # Data for widget
                _meta={
                    "openai/toolInvocation/invoked": "[Success message]",
                },
            )
        )
    
    # Unknown tool
    return types.ServerResult(
        types.CallToolResult(
            content=[
                types.TextContent(
                    type="text",
                    text=f"Unknown tool: {tool_name}",
                )
            ],
            isError=True,
        )
    )

# --- Register Handlers ---
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource

# --- Create Streamable HTTP App ---
app = mcp.streamable_http_app()

# --- Add CORS ---
from starlette.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Restrict in production
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=False,
)

# --- Main ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
```

### 2. Tool Response Format

**Critical:** Your tool must return data in this exact format:

```python
types.CallToolResult(
    # For the LLM to understand
    content=[
        types.TextContent(
            type="text",
            text="Found 5 items matching your criteria.",
        )
    ],
    
    # For the widget to render
    structuredContent={
        "items": [...],           # Your data array
        "filters_applied": {...}, # Optional metadata
        "total_results": 5,       # Optional counts
        "showing": 5
    },
    
    # For ChatGPT UI
    _meta={
        "openai/toolInvocation/invoked": "Found items",
    },
)
```

---

## Client-Side Template

### 1. Project Structure

```
web/
├── src/
│   ├── hooks/
│   │   ├── useOpenAiGlobal.ts    # Core hook (reusable)
│   │   ├── useToolOutput.ts      # Read tool data (reusable)
│   │   ├── useWidgetState.ts     # Persist state (reusable)
│   │   └── useTheme.ts           # Dark mode (reusable)
│   ├── types/
│   │   └── [your-types].ts       # Your data types
│   ├── styles/
│   │   └── index.css             # Widget styles
│   ├── [YourWidget].tsx          # Main widget component
│   ├── [ItemCard].tsx            # Item display component
│   ├── EmptyState.tsx            # No results component
│   └── index.tsx                 # Entry point (reusable)
├── dist/
│   └── component.js              # Built bundle
├── package.json
└── tsconfig.json
```

### 2. Entry Point (index.tsx) - REUSABLE

```typescript
import React from 'react';
import { createRoot } from 'react-dom/client';
import { YourWidget } from './YourWidget';
import './styles/index.css';

function init() {
  const rootElement = document.getElementById('root');
  
  if (!rootElement) {
    console.error('Root element not found');
    return;
  }

  const root = createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <YourWidget />
    </React.StrictMode>
  );
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
```

### 3. Main Widget Component Template

```typescript
import React, { useMemo } from 'react';
import { ItemCard } from './ItemCard';
import { EmptyState } from './EmptyState';
import { useToolOutput } from './hooks/useToolOutput';
import { useWidgetState } from './hooks/useWidgetState';
import { useTheme } from './hooks/useTheme';
import type { YourDataType } from './types/your-types';

export function YourWidget() {
  const toolOutput = useToolOutput();
  const theme = useTheme();
  const [widgetState, setWidgetState] = useWidgetState({
    favorites: [],
    sortBy: 'default'
  });

  // Apply theme
  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  // Get items from tool output
  const items = useMemo(() => {
    return toolOutput?.items || [];
  }, [toolOutput]);

  // Sort items
  const sortedItems = useMemo(() => {
    const sorted = [...items];
    // Your sorting logic
    return sorted;
  }, [items, widgetState.sortBy]);

  // Interaction handlers
  const toggleFavorite = (itemId: string) => {
    setWidgetState((prev) => ({
      ...prev,
      favorites: prev.favorites.includes(itemId)
        ? prev.favorites.filter((id) => id !== itemId)
        : [...prev.favorites, itemId]
    }));
  };

  // Loading state
  if (!toolOutput) {
    return (
      <div className="widget-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  // Empty state
  if (sortedItems.length === 0) {
    return (
      <div className="widget-container">
        <EmptyState />
      </div>
    );
  }

  return (
    <div className="widget-container">
      {/* Header */}
      <h2>{sortedItems.length} Items</h2>
      
      {/* Items Grid */}
      <div className="items-grid">
        {sortedItems.map((item) => (
          <ItemCard
            key={item.id}
            item={item}
            isFavorite={widgetState.favorites.includes(item.id)}
            onToggleFavorite={toggleFavorite}
          />
        ))}
      </div>
    </div>
  );
}
```

### 4. TypeScript Types Template

```typescript
// types/your-types.ts

// Window API types
export interface OpenAiGlobals {
  toolOutput?: ToolOutput;
  widgetState?: WidgetState;
  theme?: 'light' | 'dark';
  setWidgetState?: (state: WidgetState) => void;
}

declare global {
  interface Window {
    openai?: OpenAiGlobals;
  }
}

// Tool output structure
export interface ToolOutput {
  items: YourItemType[];
  filters_applied?: Record<string, any>;
  total_results?: number;
  showing?: number;
}

// Widget state (persisted)
export interface WidgetState {
  favorites: string[];
  sortBy: string;
  // Add your state fields
}

// Your data type
export interface YourItemType {
  id: string;
  // Your fields
}
```

### 5. package.json Template

```json
{
  "name": "your-widget",
  "version": "1.0.0",
  "description": "React widget for [Your MCP Server]",
  "main": "dist/component.js",
  "scripts": {
    "build": "esbuild src/index.tsx --bundle --format=esm --outfile=dist/component.js --minify --sourcemap --loader:.css=text",
    "dev": "esbuild src/index.tsx --bundle --format=esm --outfile=dist/component.js --sourcemap --watch --loader:.css=text",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0"
  },
  "devDependencies": {
    "@types/react": "^18.2.0",
    "@types/react-dom": "^18.2.0",
    "esbuild": "^0.19.0",
    "typescript": "^5.3.0"
  }
}
```

---

## Reusable Hooks

### 1. useOpenAiGlobal.ts - COPY AS-IS

```typescript
import { useSyncExternalStore } from 'react';
import type { OpenAiGlobals } from '../types/your-types';

const SET_GLOBALS_EVENT_TYPE = 'openai:set_globals';

/**
 * Hook to subscribe to window.openai global values
 * Automatically updates when ChatGPT dispatches events
 */
export function useOpenAiGlobal<K extends keyof OpenAiGlobals>(
  key: K
): OpenAiGlobals[K] {
  return useSyncExternalStore(
    (onChange) => {
      const handleSetGlobal = (event: CustomEvent) => {
        const value = event.detail?.globals?.[key];
        if (value !== undefined) {
          onChange();
        }
      };

      window.addEventListener(SET_GLOBALS_EVENT_TYPE, handleSetGlobal as EventListener, {
        passive: true,
      });

      return () => {
        window.removeEventListener(SET_GLOBALS_EVENT_TYPE, handleSetGlobal as EventListener);
      };
    },
    () => window.openai?.[key]
  );
}
```

### 2. useToolOutput.ts - COPY AS-IS

```typescript
import { useOpenAiGlobal } from './useOpenAiGlobal';
import type { ToolOutput } from '../types/your-types';

/**
 * Hook to read tool output from MCP server
 */
export function useToolOutput(): ToolOutput | null {
  return useOpenAiGlobal('toolOutput');
}
```

### 3. useWidgetState.ts - COPY AS-IS

```typescript
import { useState, useEffect, useCallback } from 'react';
import { useOpenAiGlobal } from './useOpenAiGlobal';
import type { WidgetState } from '../types/your-types';

/**
 * Hook to manage widget state that persists across sessions
 */
export function useWidgetState(
  defaultState: WidgetState
): readonly [WidgetState, (state: WidgetState | ((prev: WidgetState) => WidgetState)) => void] {
  const widgetStateFromWindow = useOpenAiGlobal('widgetState');

  const [widgetState, _setWidgetState] = useState<WidgetState>(() => {
    if (widgetStateFromWindow != null) {
      return widgetStateFromWindow;
    }
    return defaultState;
  });

  useEffect(() => {
    if (widgetStateFromWindow != null) {
      _setWidgetState(widgetStateFromWindow);
    }
  }, [widgetStateFromWindow]);

  const setWidgetState = useCallback(
    (state: WidgetState | ((prev: WidgetState) => WidgetState)) => {
      _setWidgetState((prevState) => {
        const newState = typeof state === 'function' ? state(prevState) : state;
        
        // Persist to ChatGPT
        if (window.openai?.setWidgetState) {
          window.openai.setWidgetState(newState);
        }
        
        return newState;
      });
    },
    []
  );

  return [widgetState, setWidgetState] as const;
}
```

### 4. useTheme.ts - COPY AS-IS

```typescript
import { useOpenAiGlobal } from './useOpenAiGlobal';

/**
 * Hook to read ChatGPT's theme (light/dark)
 */
export function useTheme(): 'light' | 'dark' {
  return useOpenAiGlobal('theme') ?? 'light';
}
```

---

## Quick Start Checklist

### Server Setup
- [ ] Install FastMCP: `pip install fastmcp[http]`
- [ ] Create server file with template above
- [ ] Replace `[YOUR_*]` placeholders
- [ ] Implement your tool logic
- [ ] Test with `python server.py`

### Widget Setup
- [ ] Create `web/` directory
- [ ] Copy `package.json` template
- [ ] Run `npm install`
- [ ] Copy reusable hooks to `src/hooks/`
- [ ] Create your types in `src/types/`
- [ ] Create your widget component
- [ ] Create CSS in `src/styles/index.css`
- [ ] Build with `npm run build`

### Testing
- [ ] Start server: `python server.py`
- [ ] Expose with ngrok: `ngrok http 8000`
- [ ] Create ChatGPT connector with ngrok URL + `/mcp/`
- [ ] Test in ChatGPT

### Deployment
- [ ] Verify widget renders
- [ ] Test interactions (favorites, sorting, etc.)
- [ ] Test state persistence
- [ ] Test dark mode
- [ ] Document your widget

---

## CSS Template

```css
/* Base variables */
:root {
  --color-bg: #ffffff;
  --color-bg-secondary: #f5f5f5;
  --color-text: #1a1a1a;
  --color-text-secondary: #666666;
  --color-border: #e0e0e0;
  --color-primary: #2196F3;
  --color-primary-hover: #1976D2;
  
  --spacing-xs: 0.25rem;
  --spacing-sm: 0.5rem;
  --spacing-md: 1rem;
  --spacing-lg: 1.5rem;
  --spacing-xl: 2rem;
  
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
  --shadow-md: 0 4px 6px rgba(0,0,0,0.1);
}

/* Dark mode */
[data-theme="dark"] {
  --color-bg: #1a1a1a;
  --color-bg-secondary: #2a2a2a;
  --color-text: #ffffff;
  --color-text-secondary: #b0b0b0;
  --color-border: #404040;
}

/* Base styles */
body {
  margin: 0;
  padding: 0;
  font-family: system-ui, -apple-system, sans-serif;
  background-color: var(--color-bg);
  color: var(--color-text);
}

.widget-container {
  padding: var(--spacing-lg);
  max-width: 1200px;
  margin: 0 auto;
}

.loading {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
}

/* Add your component styles */
```

---

## Key Patterns

### 1. Data Flow
```
MCP Tool → structuredContent → window.openai.toolOutput → useToolOutput() → Your Widget
```

### 2. State Persistence
```
User Action → setWidgetState() → window.openai.setWidgetState() → Persisted in ChatGPT
```

### 3. Theme Support
```
ChatGPT Theme → window.openai.theme → useTheme() → data-theme attribute → CSS variables
```

---

## Common Pitfalls

1. **Forgetting `stateless_http=True`** - Required for ChatGPT
2. **Missing `_meta` fields** - Widget won't be recognized
3. **Wrong MIME type** - Must be `text/html+skybridge`
4. **Not injecting CSS** - Widget renders but unstyled
5. **Not handling loading state** - Widget shows error before data loads
6. **Not using `useSyncExternalStore`** - State updates won't work

---

## Testing Tips

1. **Browser testing first**: Open `http://localhost:8000/widget` to debug
2. **Check console**: Look for React errors in browser DevTools
3. **Verify bundle size**: Keep under 500KB for fast loading
4. **Test dark mode**: Toggle in ChatGPT settings
5. **Test state persistence**: Refresh widget, check if favorites persist

---

## Next Steps

1. Copy this template to your new project
2. Replace all `[YOUR_*]` placeholders
3. Implement your data types
4. Build your widget UI
5. Test locally, then deploy to ChatGPT

**Success Criteria:**
- ✅ Widget renders in ChatGPT
- ✅ Data displays correctly
- ✅ Interactions work (clicks, favorites, etc.)
- ✅ State persists across sessions
- ✅ Dark mode works
- ✅ No console errors

---

## Resources

- [FastMCP Documentation](https://gofastmcp.com)
- [OpenAI Apps SDK Docs](https://platform.openai.com/docs/mcp)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [Property Server Example](../server_apps_sdk.py)
