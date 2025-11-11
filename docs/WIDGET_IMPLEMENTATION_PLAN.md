# Widget Implementation Plan: Property Listings UI

## Overview

This document outlines the plan for implementing ChatGPT Apps SDK UI components for the Property MCP Server, starting with the `query_listings` tool.

---

## 1. Component Design Decision

### Chosen Component: **Property List Card View**

Based on the Pizzaz examples, we'll implement a **List-style component** similar to the Pizzaz List example because:

- ✅ Displays multiple properties in a scannable format
- ✅ Shows key details at a glance (price, bedrooms, postcode)
- ✅ Supports inline actions (view details, favorite, filter)
- ✅ Works well in inline, PiP, and fullscreen modes
- ✅ Handles empty states gracefully

### Future Components (Roadmap)
1. **Property Map View** - Geographic visualization with clustering
2. **Property Detail Modal** - Fullscreen deep-dive with photo gallery
3. **Price Calculator Widget** - For `calculate_average_price` tool

---

## 2. Data Flow Architecture

### Current State (Text-Only)
```
User Query → ChatGPT → MCP Tool Call → Python Function → JSON Response → Text Summary
```

### Future State (With Widget)
```
User Query → ChatGPT → MCP Tool Call → Python Function → JSON Response + Widget Metadata
                                                              ↓
                                                    React Component Renders
                                                              ↓
                                                    User Interacts (filters, favorites)
                                                              ↓
                                                    window.openai.callTool() or setWidgetState()
```

---

## 3. Component Requirements

### 3.1 User Interactions

**Viewer vs. Editor**: Hybrid
- Primary: Read-only viewer (display properties)
- Secondary: Interactive filters and favorites (state management)

**Single-shot vs. Multiturn**: Multiturn
- User can refine filters without new chat messages
- State persists across follow-up queries
- Favorites persist in widget state

**Layout Modes**:
- **Inline** (default): Show 3-5 properties in compact cards
- **PiP**: Show filters + scrollable list
- **Fullscreen**: Grid layout with detailed cards + map preview

### 3.2 Data Requirements

**Tool Response Structure** (from `query_listings`):
```json
{
  "properties": [
    {
      "property_id": "32926983",
      "ld_name": "Potters Brook, Tipton",
      "ld_image": "https://...",
      "price_text": "£81,995",
      "price_amount": 81995,
      "bedrooms": 1,
      "bathrooms": 1,
      "property_type": "Apartment - First Floor",
      "postcode": "DY4 7LG",
      "garden": true,
      "parking": false,
      "status": "Sold Subject to Contract",
      "overview": ["NO UPWARD CHAIN", "One Bedroom Apartment", ...],
      "detail_url": "https://...",
      "lat": "52.5278129577636700",
      "lng": "-2.0472130775451660"
    }
  ],
  "filters_applied": {
    "postcode": "DY4",
    "max_price": 100000,
    "min_bedrooms": 1
  },
  "total_results": 47,
  "showing": 5
}
```

**Widget State** (persisted via `setWidgetState`):
```json
{
  "favorites": ["32926983", "34187182"],
  "hidden": ["12345678"],
  "sort_by": "price_asc",
  "view_mode": "grid"
}
```

### 3.3 Component Features

**Must Have (v1)**:
- ✅ Display property cards with image, price, beds, postcode
- ✅ Show garden/parking icons
- ✅ Click to open external detail URL
- ✅ Empty state handling
- ✅ Responsive design (mobile + desktop)
- ✅ Dark mode support

**Should Have (v2)**:
- ⭐ Favorite/bookmark properties
- ⭐ Hide/dismiss properties
- ⭐ Sort by price/bedrooms
- ⭐ Inline filter refinement
- ⭐ "Load more" button (call tool with higher limit)

**Could Have (v3)**:
- 🗺️ Toggle map view
- 📊 Price comparison chart
- 🔔 Save search criteria
- 📤 Share property list

---

## 4. Project Structure

```
mcp-property-server/
├── server.py                    # MCP server (existing)
├── tools.py                     # Tool implementations (existing)
├── data_loader.py               # Data loading (existing)
├── web/                         # NEW: React component project
│   ├── package.json
│   ├── tsconfig.json
│   ├── esbuild.config.js
│   ├── src/
│   │   ├── index.tsx            # Entry point + React root
│   │   ├── PropertyListWidget.tsx  # Main component
│   │   ├── PropertyCard.tsx     # Individual property card
│   │   ├── EmptyState.tsx       # No results view
│   │   ├── hooks/
│   │   │   ├── useOpenAiGlobal.ts
│   │   │   ├── useToolOutput.ts
│   │   │   ├── useWidgetState.ts
│   │   │   └── useTheme.ts
│   │   ├── types/
│   │   │   └── property.ts      # TypeScript interfaces
│   │   └── styles/
│   │       └── index.css        # Tailwind + custom styles
│   └── dist/
│       └── component.js         # Build output (bundled)
└── docs/
    └── WIDGET_IMPLEMENTATION_PLAN.md  # This file
```

---

## 5. Implementation Phases

### Phase 1: Setup & Scaffolding (Day 1)
- [ ] Create `web/` directory structure
- [ ] Initialize Node project with React + TypeScript
- [ ] Install dependencies: `react`, `react-dom`, `typescript`, `esbuild`
- [ ] Configure TypeScript (`tsconfig.json`)
- [ ] Set up esbuild bundler
- [ ] Create basic component skeleton
- [ ] Add `window.openai` TypeScript definitions

### Phase 2: Core Component (Day 1-2)
- [ ] Implement `PropertyCard.tsx` with:
  - Property image
  - Price display
  - Bedrooms/bathrooms
  - Garden/parking icons
  - Postcode badge
  - External link button
- [ ] Implement `PropertyListWidget.tsx` with:
  - Read `window.openai.toolOutput`
  - Map properties to cards
  - Grid/list layout
  - Empty state handling
- [ ] Implement `EmptyState.tsx`
- [ ] Add responsive CSS with Tailwind

### Phase 3: React Hooks (Day 2)
- [ ] `useOpenAiGlobal` - Subscribe to host events
- [ ] `useToolOutput` - Read initial tool response
- [ ] `useWidgetState` - Persist favorites/hidden
- [ ] `useTheme` - Dark mode support

### Phase 4: Server Integration (Day 2-3)
- [ ] Modify `tools.py` to return enhanced response structure
- [ ] Update `server.py` to include widget metadata in tool response
- [ ] Add component bundle to MCP response
- [ ] Test with ChatGPT Developer Mode

### Phase 5: Interactive Features (Day 3-4)
- [ ] Favorite/bookmark functionality
- [ ] Hide/dismiss properties
- [ ] Sort controls
- [ ] "Load more" button (calls `query_listings` with higher limit)
- [ ] Filter refinement UI

### Phase 6: Testing & Polish (Day 4-5)
- [ ] Test in inline mode
- [ ] Test in PiP mode
- [ ] Test in fullscreen mode
- [ ] Mobile responsiveness
- [ ] Dark mode verification
- [ ] Error handling
- [ ] Loading states

---

## 6. Technical Decisions

### 6.1 Styling Approach
**Decision**: Tailwind CSS + CSS Variables

**Rationale**:
- Fast development with utility classes
- Easy dark mode with `color-scheme`
- Small bundle size with tree-shaking
- Consistent with Pizzaz examples

### 6.2 State Management
**Decision**: React hooks + `window.openai.setWidgetState`

**Rationale**:
- No external state library needed
- Widget state syncs with ChatGPT
- Simple and maintainable
- Under 4k tokens for performance

### 6.3 Bundler
**Decision**: esbuild

**Rationale**:
- Fast builds
- Simple configuration
- ESM output format
- Recommended by Apps SDK docs

### 6.4 TypeScript
**Decision**: Strict TypeScript with full type safety

**Rationale**:
- Catch errors at compile time
- Better IDE support
- Self-documenting code
- Easier refactoring

---

## 7. Widget State Contract

### Component State (React)
```typescript
interface ComponentState {
  sortBy: 'price_asc' | 'price_desc' | 'bedrooms_desc';
  viewMode: 'grid' | 'list';
  expandedPropertyId: string | null;
}
```

### Widget State (Persisted to ChatGPT)
```typescript
interface WidgetState {
  favorites: string[];        // property_ids
  hidden: string[];          // property_ids
  lastQuery: {               // For "load more" functionality
    postcode?: string;
    max_price?: number;
    min_bedrooms?: number;
  };
}
```

### Server State (Python)
- Authoritative data in `data/listings.jsonl`
- Filtered results computed on-demand
- No server-side state persistence needed

---

## 8. API Contracts

### 8.1 Tool Response Enhancement

**Before** (current):
```python
return filtered_results[:limit]  # Just a list
```

**After** (with widget metadata):
```python
return {
    "properties": filtered_results[:limit],
    "filters_applied": {
        "postcode": postcode,
        "max_price": max_price,
        "min_bedrooms": min_bedrooms,
        "has_garden": has_garden,
        "has_parking": has_parking
    },
    "total_results": len(filtered_results),
    "showing": min(limit, len(filtered_results)),
    "_widget": {
        "component": "PropertyListWidget",
        "version": "1.0.0"
    }
}
```

### 8.2 Component-Initiated Tool Calls

**Load More**:
```typescript
const response = await window.openai.callTool('query_listings', {
  ...lastQuery,
  limit: 10  // Increase limit
});
```

**Refine Filters**:
```typescript
const response = await window.openai.callTool('query_listings', {
  postcode: 'DY4',
  max_price: 150000,
  min_bedrooms: 2,
  has_garden: true
});
```

---

## 9. Responsive Design Breakpoints

```css
/* Mobile: < 640px */
- Single column
- Compact cards
- Bottom sheet for filters

/* Tablet: 640px - 1024px */
- Two columns
- Medium cards
- Side panel for filters

/* Desktop: > 1024px */
- Three columns (inline)
- Four columns (fullscreen)
- Large cards with hover effects
```

---

## 10. Error Handling & Fallbacks

### Component Load Failure
```typescript
try {
  // Render component
} catch (error) {
  // Fallback: Show JSON data + retry button
  return <pre>{JSON.stringify(toolOutput, null, 2)}</pre>;
}
```

### Tool Call Failure
```typescript
try {
  await window.openai.callTool('query_listings', args);
} catch (error) {
  // Show error toast
  // Suggest using chat input instead
}
```

### Missing Data
```typescript
if (!toolOutput?.properties?.length) {
  return <EmptyState message="No properties found" />;
}
```

---

## 11. Performance Considerations

### Bundle Size Target
- **Goal**: < 100KB gzipped
- **Strategy**: 
  - Tree-shake unused code
  - Lazy load images
  - No heavy dependencies (charts, maps in v1)

### Token Efficiency
- Widget state < 4k tokens
- Only persist essential data (favorites, hidden)
- Don't duplicate tool output in widget state

### Image Optimization
- Use `loading="lazy"` for images
- Show placeholder while loading
- Handle missing images gracefully

---

## 12. Testing Strategy

### Unit Tests (Future)
- Component rendering
- Hook behavior
- State management

### Integration Tests
1. **Inline Mode**: Default view in chat
2. **PiP Mode**: Floating window
3. **Fullscreen Mode**: Full takeover
4. **Dark Mode**: Color scheme switching
5. **Mobile**: Touch interactions
6. **Tool Calls**: Component-initiated queries

### Manual Testing Checklist
- [ ] Component loads in ChatGPT
- [ ] Properties display correctly
- [ ] Images load (or show placeholder)
- [ ] External links work
- [ ] Favorites persist across reloads
- [ ] Sort/filter updates UI
- [ ] "Load more" fetches new data
- [ ] Empty state shows when no results
- [ ] Dark mode looks good
- [ ] Mobile responsive

---

## 13. Documentation Plan

### For Developers
- `web/README.md` - Setup and build instructions
- `web/src/README.md` - Component architecture
- Inline code comments
- TypeScript types as documentation

### For Users
- Update main `README.md` with widget screenshots
- Add "Using the UI" section
- Show example queries that trigger widgets

---

## 14. Deployment Checklist

- [ ] Build component: `npm run build`
- [ ] Verify bundle size
- [ ] Test in ChatGPT Developer Mode
- [ ] Update server to include component
- [ ] Deploy to ngrok (or production)
- [ ] Update ChatGPT connector
- [ ] Test end-to-end
- [ ] Document any issues
- [ ] Create demo video/screenshots

---

## 15. Future Enhancements

### Property Map Widget
- Mapbox integration
- Marker clustering
- Detail pane on click
- Fullscreen mode

### Property Detail Modal
- Photo gallery with swipe
- Full description
- Contact agent button
- Share functionality

### Price Calculator Widget
- For `calculate_average_price` tool
- Chart visualization
- Comparison table
- Export data

### Advanced Features
- Save searches
- Email alerts
- Property comparison
- Mortgage calculator

---

## 16. Key Learnings from Docs

### From `custom-ui.md`
1. **window.openai API** is the bridge between React and ChatGPT
2. **useOpenAiGlobal** hook for reactive updates
3. **setWidgetState** for persistence (< 4k tokens)
4. **callTool** for component-initiated actions
5. **requestDisplayMode** for layout changes
6. **sendFollowUpMessage** for conversational updates

### From `plan-ui.md`
1. **Plan early** - Define data requirements upfront
2. **Responsive by default** - Mobile + desktop
3. **State contract** - Be explicit about what's stored where
4. **Telemetry** - Plan debugging hooks early
5. **Fallbacks** - Always handle component load failures

---

## 17. Success Criteria

### v1 (MVP)
- ✅ Component loads in ChatGPT
- ✅ Displays properties with images, price, beds
- ✅ External links work
- ✅ Responsive design
- ✅ Dark mode support
- ✅ Empty state handling

### v2 (Enhanced)
- ⭐ Favorites persist
- ⭐ Sort/filter controls
- ⭐ "Load more" functionality
- ⭐ Smooth animations
- ⭐ Loading states

### v3 (Advanced)
- 🗺️ Map view toggle
- 📊 Price charts
- 🔔 Save searches
- 📤 Share functionality

---

## Next Steps

1. **Review this plan** with team/stakeholders
2. **Set up development environment** (Phase 1)
3. **Create basic component** (Phase 2)
4. **Integrate with server** (Phase 4)
5. **Test in ChatGPT** (Phase 6)
6. **Iterate based on feedback**

---

## Questions to Resolve

1. Should we use a CSS framework (Tailwind) or custom CSS?
2. Do we need a map in v1 or defer to v2?
3. What's the priority: favorites or filters?
4. Should we support property comparison?
5. Do we need analytics/telemetry from day 1?

---

**Last Updated**: 2025-11-11
**Status**: Planning Phase
**Next Review**: After Phase 1 completion
