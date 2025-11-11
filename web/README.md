# Property Widget - React UI Component

React-based UI component for displaying property listings in ChatGPT.

## Setup

```bash
# Install dependencies
npm install

# Build for production
npm run build

# Watch mode for development
npm run dev

# Type check
npm run type-check
```

## Project Structure

```
src/
├── index.tsx                    # Entry point
├── PropertyListWidget.tsx       # Main widget component
├── PropertyCard.tsx             # Individual property card
├── EmptyState.tsx               # No results view
├── hooks/
│   ├── useOpenAiGlobal.ts      # Subscribe to window.openai
│   ├── useToolOutput.ts         # Read tool response
│   ├── useWidgetState.ts        # Persist state
│   └── useTheme.ts              # Dark mode
├── types/
│   └── property.ts              # TypeScript interfaces
└── styles/
    └── index.css                # Tailwind-inspired styles
```

## Features

- ✅ Display property cards with images, price, bedrooms
- ✅ Favorite/unfavorite properties (persisted)
- ✅ Sort by price or bedrooms
- ✅ Dark mode support
- ✅ Responsive design
- ✅ Empty state handling
- ✅ Loading state

## Build Output

The build process creates `dist/component.js` which is a bundled ESM module that can be embedded in the MCP server response.

## Integration with MCP Server

The Python server needs to:
1. Return enhanced tool response with property data
2. Include the bundled component in the response
3. Provide widget metadata

See `../docs/WIDGET_IMPLEMENTATION_PLAN.md` for details.
