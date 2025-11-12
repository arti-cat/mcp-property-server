# Reusable Widget Patterns - Quick Reference

**Created:** November 2025  
**Based on:** Property MCP Server successful implementation

---

## What You Can Reuse

### ✅ Copy These Files Exactly (100% Reusable)

1. **`web/src/hooks/useOpenAiGlobal.ts`** - Core ChatGPT API integration
2. **`web/src/hooks/useToolOutput.ts`** - Read tool data
3. **`web/src/hooks/useWidgetState.ts`** - Persist state across sessions
4. **`web/src/hooks/useTheme.ts`** - Dark mode support
5. **`web/src/index.tsx`** - React entry point
6. **`web/package.json`** - Build configuration (update name)
7. **`web/tsconfig.json`** - TypeScript config

### 🔧 Adapt These Patterns (Template-Based)

1. **Server structure** - FastMCP with `stateless_http=True`
2. **Tool metadata** - `_meta` fields for widget recognition
3. **Response format** - `{content, structuredContent, _meta}`
4. **CSS variables** - Theme system with light/dark modes
5. **Widget component** - Loading/empty/data states pattern

---

## Quick Start (3 Options)

### Option 1: Use the Generator Script

```bash
cd docs
./create-widget-project.sh my-new-widget
cd my-new-widget
pip install -r requirements.txt
cd web && npm install && npm run build
cd .. && python server.py
```

### Option 2: Copy from Property Server

```bash
# Copy reusable hooks
cp -r property-server/web/src/hooks your-project/web/src/

# Copy build config
cp property-server/web/package.json your-project/web/
cp property-server/web/tsconfig.json your-project/web/

# Copy server template
cp property-server/server_apps_sdk.py your-project/server.py
# Then replace [YOUR_*] placeholders
```

### Option 3: Manual Setup

Follow the complete guide in `WIDGET_TEMPLATE_GUIDE.md`

---

## Core Patterns

### 1. Server Pattern (FastMCP + Apps SDK)

```python
from mcp.server.fastmcp import FastMCP
import mcp.types as types

# REQUIRED: stateless_http for ChatGPT
mcp = FastMCP(name="YourServer", stateless_http=True)

# Widget metadata
def _tool_meta():
    return {
        "openai/outputTemplate": "ui://widget/your-widget.html",
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }

# Tool response format
types.CallToolResult(
    content=[types.TextContent(type="text", text="Summary for LLM")],
    structuredContent={"items": [...]},  # Data for widget
    _meta={"openai/toolInvocation/invoked": "Done"},
)
```

### 2. Widget Pattern (React + Hooks)

```typescript
import { useToolOutput } from './hooks/useToolOutput';
import { useWidgetState } from './hooks/useWidgetState';
import { useTheme } from './hooks/useTheme';

export function YourWidget() {
  const toolOutput = useToolOutput();  // Read data
  const theme = useTheme();            // Dark mode
  const [state, setState] = useWidgetState({  // Persist state
    favorites: []
  });

  // Loading state
  if (!toolOutput) return <div>Loading...</div>;
  
  // Empty state
  if (toolOutput.items.length === 0) return <div>No items</div>;
  
  // Render data
  return <div>{/* Your UI */}</div>;
}
```

### 3. Data Flow Pattern

```
User Query
    ↓
ChatGPT detects widget metadata
    ↓
Calls MCP tool
    ↓
Server returns {content, structuredContent, _meta}
    ↓
ChatGPT fetches widget HTML
    ↓
Widget reads window.openai.toolOutput
    ↓
Widget renders with data
    ↓
User interacts (favorites, sorting, etc.)
    ↓
Widget calls window.openai.setWidgetState()
    ↓
State persists in ChatGPT
```

---

## File Checklist

### Server Files
- [ ] `server.py` - FastMCP server with Apps SDK
- [ ] `requirements.txt` - Python dependencies
- [ ] `tools.py` - Tool implementations (optional)

### Widget Files
- [ ] `web/package.json` - Node dependencies
- [ ] `web/tsconfig.json` - TypeScript config
- [ ] `web/src/index.tsx` - Entry point
- [ ] `web/src/Widget.tsx` - Main component
- [ ] `web/src/hooks/` - Reusable hooks (4 files)
- [ ] `web/src/types/` - TypeScript types
- [ ] `web/src/styles/index.css` - Styles
- [ ] `web/dist/component.js` - Built bundle

---

## Common Customizations

### Change Widget Name
1. Server: Update `WIDGET_URI = "ui://widget/YOUR-NAME.html"`
2. No changes needed in widget code

### Add New State Field
```typescript
const [state, setState] = useWidgetState({
  favorites: [],
  yourNewField: 'default'  // Add here
});
```

### Add Sorting
```typescript
const sorted = useMemo(() => {
  const copy = [...items];
  copy.sort((a, b) => /* your logic */);
  return copy;
}, [items, state.sortBy]);
```

### Add Filtering
```typescript
const filtered = useMemo(() => {
  return items.filter(item => /* your logic */);
}, [items, state.filters]);
```

---

## Testing Workflow

1. **Local Development**
   ```bash
   # Terminal 1: Build widget
   cd web && npm run dev
   
   # Terminal 2: Run server
   python server.py
   
   # Browser: Test at http://localhost:8000/widget
   ```

2. **ChatGPT Testing**
   ```bash
   # Terminal 1: Run server
   python server.py
   
   # Terminal 2: Expose with ngrok
   ngrok http 8000
   
   # ChatGPT: Create connector with ngrok URL + /mcp/
   ```

---

## Key Success Factors

### Must Have
- ✅ `stateless_http=True` in FastMCP
- ✅ `_meta` fields in tool and resource
- ✅ `structuredContent` in tool response
- ✅ CSS injected into widget HTML
- ✅ Loading and empty states in widget

### Nice to Have
- 🎨 Dark mode support (via `useTheme`)
- 💾 State persistence (via `useWidgetState`)
- 🔄 Sorting/filtering
- ❤️ Favorites/bookmarks
- 📱 Responsive design

---

## Performance Tips

1. **Keep bundle small** - Under 500KB
2. **Lazy load images** - Use loading="lazy"
3. **Memoize expensive operations** - Use `useMemo`
4. **Debounce state updates** - Avoid excessive `setWidgetState` calls
5. **Minimize CSS** - Use CSS variables, avoid large frameworks

---

## Debugging Tips

### Widget Not Rendering
- Check: `_meta` fields present in tool?
- Check: `WIDGET_URI` matches in tool and resource?
- Check: `MIME_TYPE = "text/html+skybridge"`?
- Check: Widget bundle built? (`web/dist/component.js` exists?)

### Data Not Showing
- Check: `structuredContent` in tool response?
- Check: `window.openai.toolOutput` in browser console?
- Check: Widget reading correct field? (`toolOutput.items`)

### State Not Persisting
- Check: Calling `setWidgetState()` not `setState()`?
- Check: `window.openai.setWidgetState` exists?
- Check: Using `useWidgetState` hook?

### Styles Not Applied
- Check: CSS injected into HTML template?
- Check: CSS variables defined?
- Check: `data-theme` attribute set?

---

## Migration Path

### From Basic MCP Server → Widget-Enabled

1. Add `stateless_http=True` to FastMCP
2. Add `_meta` fields to tools
3. Change tool response to include `structuredContent`
4. Create widget project (use generator script)
5. Build widget and inject into server
6. Test in ChatGPT

**Time estimate:** 2-4 hours for simple widgets

---

## Resources

- **Full Guide:** `WIDGET_TEMPLATE_GUIDE.md`
- **Generator Script:** `create-widget-project.sh`
- **Working Example:** `../server_apps_sdk.py`
- **Widget Example:** `../web/src/PropertyListWidget.tsx`

---

## Support Checklist

When asking for help, provide:
- [ ] Server logs
- [ ] Browser console errors
- [ ] `window.openai` object (in console)
- [ ] Tool response format
- [ ] Widget bundle size
- [ ] ChatGPT connector URL

---

## Next Steps

1. **Read:** `WIDGET_TEMPLATE_GUIDE.md` for complete details
2. **Generate:** Run `./create-widget-project.sh your-project`
3. **Customize:** Replace placeholders with your data
4. **Test:** Build and test locally first
5. **Deploy:** Expose with ngrok and test in ChatGPT
6. **Iterate:** Improve based on user feedback

**Good luck building your widget!** 🚀
