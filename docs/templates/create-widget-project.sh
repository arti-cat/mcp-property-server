#!/bin/bash
# ChatGPT Apps SDK Widget Project Generator
# Usage: ./create-widget-project.sh <project-name>

set -e

PROJECT_NAME="${1:-my-widget}"
echo "🚀 Creating ChatGPT Apps SDK Widget Project: $PROJECT_NAME"

# Create directory structure
mkdir -p "$PROJECT_NAME"/{web/src/{hooks,types,styles},docs}
cd "$PROJECT_NAME"

echo "📁 Created directory structure"

# Create package.json
cat > web/package.json << 'EOF'
{
  "name": "widget",
  "version": "1.0.0",
  "description": "ChatGPT Apps SDK Widget",
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
EOF

# Create tsconfig.json
cat > web/tsconfig.json << 'EOF'
{
  "compilerOptions": {
    "target": "ES2020",
    "module": "ESNext",
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "jsx": "react-jsx",
    "strict": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "moduleResolution": "node",
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true
  },
  "include": ["src"]
}
EOF

# Create reusable hooks
cat > web/src/hooks/useOpenAiGlobal.ts << 'EOF'
import { useSyncExternalStore } from 'react';

const SET_GLOBALS_EVENT_TYPE = 'openai:set_globals';

export function useOpenAiGlobal<K extends keyof any>(key: K): any {
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
    () => (window as any).openai?.[key]
  );
}
EOF

cat > web/src/hooks/useToolOutput.ts << 'EOF'
import { useOpenAiGlobal } from './useOpenAiGlobal';

export function useToolOutput(): any {
  return useOpenAiGlobal('toolOutput');
}
EOF

cat > web/src/hooks/useWidgetState.ts << 'EOF'
import { useState, useEffect, useCallback } from 'react';
import { useOpenAiGlobal } from './useOpenAiGlobal';

export function useWidgetState(defaultState: any): readonly [any, (state: any) => void] {
  const widgetStateFromWindow = useOpenAiGlobal('widgetState');

  const [widgetState, _setWidgetState] = useState(() => {
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

  const setWidgetState = useCallback((state: any) => {
    _setWidgetState((prevState: any) => {
      const newState = typeof state === 'function' ? state(prevState) : state;
      
      if ((window as any).openai?.setWidgetState) {
        (window as any).openai.setWidgetState(newState);
      }
      
      return newState;
    });
  }, []);

  return [widgetState, setWidgetState] as const;
}
EOF

cat > web/src/hooks/useTheme.ts << 'EOF'
import { useOpenAiGlobal } from './useOpenAiGlobal';

export function useTheme(): 'light' | 'dark' {
  return useOpenAiGlobal('theme') ?? 'light';
}
EOF

# Create types template
cat > web/src/types/widget.ts << 'EOF'
// TODO: Define your data types here

export interface ToolOutput {
  items: any[];
  total_results?: number;
  showing?: number;
}

export interface WidgetState {
  favorites: string[];
  sortBy: string;
}
EOF

# Create main widget component
cat > web/src/Widget.tsx << 'EOF'
import React from 'react';
import { useToolOutput } from './hooks/useToolOutput';
import { useWidgetState } from './hooks/useWidgetState';
import { useTheme } from './hooks/useTheme';

export function Widget() {
  const toolOutput = useToolOutput();
  const theme = useTheme();
  const [widgetState, setWidgetState] = useWidgetState({
    favorites: [],
    sortBy: 'default'
  });

  React.useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
  }, [theme]);

  if (!toolOutput) {
    return (
      <div className="widget-container">
        <div className="loading">Loading...</div>
      </div>
    );
  }

  const items = toolOutput.items || [];

  if (items.length === 0) {
    return (
      <div className="widget-container">
        <div className="empty-state">No items found</div>
      </div>
    );
  }

  return (
    <div className="widget-container">
      <h2>{items.length} Items</h2>
      <div className="items-grid">
        {items.map((item: any, index: number) => (
          <div key={index} className="item-card">
            {JSON.stringify(item)}
          </div>
        ))}
      </div>
    </div>
  );
}
EOF

# Create entry point
cat > web/src/index.tsx << 'EOF'
import React from 'react';
import { createRoot } from 'react-dom/client';
import { Widget } from './Widget';
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
      <Widget />
    </React.StrictMode>
  );
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
EOF

# Create CSS
cat > web/src/styles/index.css << 'EOF'
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

[data-theme="dark"] {
  --color-bg: #1a1a1a;
  --color-bg-secondary: #2a2a2a;
  --color-text: #ffffff;
  --color-text-secondary: #b0b0b0;
  --color-border: #404040;
}

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

.loading, .empty-state {
  text-align: center;
  padding: var(--spacing-xl);
  color: var(--color-text-secondary);
}

.items-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: var(--spacing-md);
}

.item-card {
  padding: var(--spacing-md);
  background: var(--color-bg-secondary);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}
EOF

# Create server template
cat > server.py << 'EOF'
"""
MCP Server with ChatGPT Apps SDK Widget Support
TODO: Replace [YOUR_*] placeholders with your values
"""
from pathlib import Path
from typing import Any, Dict, List
import mcp.types as types
from mcp.server.fastmcp import FastMCP
import json

MIME_TYPE = "text/html+skybridge"
WIDGET_URI = "ui://widget/my-widget.html"

# Load widget bundle
WIDGET_HTML = ""
widget_path = Path("web/dist/component.js")
css_path = Path("web/src/styles/index.css")

if widget_path.exists():
    widget_js = widget_path.read_text(encoding="utf-8")
    widget_css = ""
    
    if css_path.exists():
        widget_css = css_path.read_text(encoding="utf-8")
    
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
    print(f"✅ Widget loaded")
else:
    print("❌ Widget not found - run: cd web && npm run build")

mcp = FastMCP(name="MyServer", stateless_http=True)

def _tool_meta() -> Dict[str, Any]:
    return {
        "openai/outputTemplate": WIDGET_URI,
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
        "openai/toolInvocation/invoking": "Loading...",
        "openai/toolInvocation/invoked": "Done",
    }

@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="my_tool",
            title="My Tool",
            description="TODO: Add description",
            inputSchema={"type": "object", "properties": {}},
            _meta=_tool_meta(),
            annotations={"readOnlyHint": True},
        ),
    ]

@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name="My Widget",
            title="My Widget",
            uri=WIDGET_URI,
            description="Interactive widget",
            mimeType=MIME_TYPE,
            _meta=_tool_meta(),
        )
    ]

async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    if str(req.params.uri) != WIDGET_URI:
        return types.ServerResult(
            types.ReadResourceResult(contents=[], _meta={"error": "Unknown resource"})
        )
    
    return types.ServerResult(
        types.ReadResourceResult(
            contents=[
                types.TextResourceContents(
                    uri=WIDGET_URI,
                    mimeType=MIME_TYPE,
                    text=WIDGET_HTML,
                    _meta=_tool_meta(),
                )
            ]
        )
    )

async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    tool_name = req.params.name
    
    if tool_name == "my_tool":
        # TODO: Implement your tool logic
        result = {"items": [{"id": "1", "name": "Example"}]}
        
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text="Found 1 item")],
                structuredContent=result,
                _meta={"openai/toolInvocation/invoked": "Done"},
            )
        )
    
    return types.ServerResult(
        types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Unknown tool: {tool_name}")],
            isError=True,
        )
    )

mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource

app = mcp.streamable_http_app()

from starlette.middleware.cors import CORSMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="0.0.0.0", port=8000)
EOF

# Create requirements.txt
cat > requirements.txt << 'EOF'
fastmcp[http]
EOF

# Create README
cat > README.md << 'EOF'
# ChatGPT Apps SDK Widget Project

## Setup

1. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Node dependencies:
   ```bash
   cd web && npm install
   ```

3. Build widget:
   ```bash
   cd web && npm run build
   ```

4. Run server:
   ```bash
   python server.py
   ```

5. Expose with ngrok:
   ```bash
   ngrok http 8000
   ```

6. Create ChatGPT connector with: `https://your-url.ngrok.io/mcp/`

## Development

- Edit widget: `web/src/Widget.tsx`
- Edit types: `web/src/types/widget.ts`
- Edit styles: `web/src/styles/index.css`
- Rebuild: `cd web && npm run build`

## TODO

- [ ] Define your data types in `web/src/types/widget.ts`
- [ ] Implement tool logic in `server.py`
- [ ] Customize widget UI in `web/src/Widget.tsx`
- [ ] Add your styles in `web/src/styles/index.css`
- [ ] Test in ChatGPT
EOF

echo ""
echo "✅ Project created successfully!"
echo ""
echo "📋 Next steps:"
echo "   1. cd $PROJECT_NAME"
echo "   2. pip install -r requirements.txt"
echo "   3. cd web && npm install"
echo "   4. npm run build"
echo "   5. cd .. && python server.py"
echo ""
echo "📚 See README.md for full instructions"
