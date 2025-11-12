# Widget Quick Start Guide

## TL;DR - What We're Building

A **React-based UI component** that displays property listings inside ChatGPT with interactive features like favorites, sorting, and "load more" functionality.

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                        ChatGPT UI                           │
│  ┌───────────────────────────────────────────────────────┐  │
│  │              User types query                         │  │
│  │  "Show me properties in DY4 under £100k"            │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌───────────────────────────────────────────────────────┐  │
│  │           MCP Tool Call: query_listings               │  │
│  │  { postcode: "DY4", max_price: 100000 }             │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   Python MCP Server                         │
│  ┌───────────────────────────────────────────────────────┐  │
│  │  tools.query_listings()                               │  │
│  │  - Filters 475 properties                            │  │
│  │  - Returns JSON + widget metadata                    │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                   ChatGPT UI (iframe)                       │
│  ┌───────────────────────────────────────────────────────┐  │
│  │        React Component Renders                        │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  🏠 Property Card                               │  │  │
│  │  │  £81,995 | 1 bed | DY4 7LG                     │  │  │
│  │  │  🌳 Garden | 🚗 No Parking                      │  │  │
│  │  │  [View Details] [❤️ Favorite]                   │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │  🏠 Property Card                               │  │  │
│  │  │  £84,950 | 1 bed | B79 7BG                     │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  │                                                       │  │
│  │  [Load More] [Sort: Price ▼] [Filters]              │  │
│  └───────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  User clicks "Load More" → window.openai.callTool()        │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Components

### 1. **Python Server** (`server.py` + `tools.py`)
- Handles MCP tool calls
- Filters property data
- Returns JSON response with widget metadata

### 2. **React Component** (`web/src/`)
- Renders property cards
- Manages UI state (sort, favorites)
- Calls tools via `window.openai.callTool()`
- Persists state via `window.openai.setWidgetState()`

### 3. **window.openai API** (Bridge)
- `toolOutput` - Initial data from server
- `callTool()` - Make new tool calls
- `setWidgetState()` - Persist favorites/hidden
- `requestDisplayMode()` - Switch inline/PiP/fullscreen
- `sendFollowUpMessage()` - Trigger chat messages

---

## File Structure

```
mcp-property-server/
├── server.py                    # MCP server
├── tools.py                     # Tool implementations
├── web/                         # NEW: React project
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   ├── index.tsx            # Entry point
│   │   ├── PropertyListWidget.tsx
│   │   ├── PropertyCard.tsx
│   │   ├── hooks/
│   │   │   ├── useToolOutput.ts
│   │   │   └── useWidgetState.ts
│   │   └── types/
│   │       └── property.ts
│   └── dist/
│       └── component.js         # Bundled output
```

---

## Implementation Steps

### Phase 1: Setup (30 min)
```bash
# Create web directory
mkdir -p web/src/{hooks,types,styles}

# Initialize Node project
cd web
npm init -y

# Install dependencies
npm install react@^18 react-dom@^18
npm install -D typescript @types/react @types/react-dom esbuild

# Create tsconfig.json
# Create esbuild.config.js
```

### Phase 2: Core Component (2-3 hours)
1. Create `PropertyCard.tsx` - Individual property display
2. Create `PropertyListWidget.tsx` - Main container
3. Create `index.tsx` - React root + mount
4. Add basic CSS (Tailwind or custom)

### Phase 3: Hooks (1-2 hours)
1. `useToolOutput()` - Read initial data
2. `useWidgetState()` - Persist favorites
3. `useTheme()` - Dark mode support

### Phase 4: Server Integration (1-2 hours)
1. Modify `tools.py` to return enhanced response
2. Update `server.py` to include widget metadata
3. Bundle component: `npm run build`
4. Test in ChatGPT

### Phase 5: Interactive Features (2-3 hours)
1. Favorite/unfavorite properties
2. Sort by price/bedrooms
3. "Load more" button
4. Filter refinement UI

---

## Data Contracts

### Tool Response (Enhanced)
```python
# tools.py - query_listings()
return {
    "properties": [
        {
            "property_id": "32926983",
            "ld_name": "Potters Brook, Tipton",
            "ld_image": "https://...",
            "price_amount": 81995,
            "bedrooms": 1,
            "postcode": "DY4 7LG",
            "garden": True,
            "parking": False,
            # ... more fields
        }
    ],
    "filters_applied": {
        "postcode": "DY4",
        "max_price": 100000
    },
    "total_results": 47,
    "showing": 5
}
```

### Widget State (Persisted)
```typescript
interface WidgetState {
  favorites: string[];  // property_ids
  hidden: string[];     // property_ids
  sortBy: 'price_asc' | 'price_desc';
}
```

---

## Key APIs

### Read Initial Data
```typescript
const toolOutput = useToolOutput();
const properties = toolOutput?.properties || [];
```

### Persist Favorites
```typescript
const [widgetState, setWidgetState] = useWidgetState({
  favorites: [],
  hidden: []
});

const toggleFavorite = (propertyId: string) => {
  setWidgetState(prev => ({
    ...prev,
    favorites: prev.favorites.includes(propertyId)
      ? prev.favorites.filter(id => id !== propertyId)
      : [...prev.favorites, propertyId]
  }));
};
```

### Load More Properties
```typescript
const loadMore = async () => {
  const response = await window.openai.callTool('query_listings', {
    postcode: 'DY4',
    limit: 10  // Increase limit
  });
  // Update UI with new properties
};
```

### Switch to Fullscreen
```typescript
const expandView = async () => {
  await window.openai.requestDisplayMode({ mode: 'fullscreen' });
};
```

---

## Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Component Type** | List View | Best for scanning multiple properties |
| **Styling** | Tailwind CSS | Fast development, small bundle |
| **State Management** | React hooks + window.openai | Simple, no external libraries |
| **Bundler** | esbuild | Fast, simple, ESM output |
| **TypeScript** | Strict mode | Type safety, better DX |

---

## Success Criteria

### v1 (MVP)
- ✅ Component loads in ChatGPT
- ✅ Displays properties with images
- ✅ External links work
- ✅ Responsive design
- ✅ Dark mode support

### v2 (Enhanced)
- ⭐ Favorites persist
- ⭐ Sort/filter controls
- ⭐ "Load more" functionality

---

## Next Steps

1. **Review this plan** - Discuss any questions
2. **Set up web/ directory** - Initialize Node project
3. **Create basic component** - PropertyCard + PropertyListWidget
4. **Test locally** - Build and verify bundle
5. **Integrate with server** - Modify tools.py response
6. **Deploy to ChatGPT** - Test end-to-end

---

## Questions?

- **Q: Do we need a map in v1?**
  - A: No, defer to v2. Focus on list view first.

- **Q: Should we use a CSS framework?**
  - A: Yes, Tailwind for speed. Can refactor later.

- **Q: How do we handle images that fail to load?**
  - A: Show placeholder, use `onError` handler.

- **Q: What about mobile?**
  - A: Responsive by default. Test on mobile after v1.

---

**Ready to start?** Let's begin with Phase 1: Setup! 🚀
