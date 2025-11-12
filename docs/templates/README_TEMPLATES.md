# Widget Templates & Patterns - Index

**Created:** November 2025  
**Status:** Production-Ready  
**Based On:** Property MCP Server (475 properties, interactive widget)

---

## 📚 Documentation Overview

This directory contains comprehensive templates and patterns for building ChatGPT Apps SDK widgets for MCP servers.

### Quick Navigation

| Document | Purpose | Audience |
|----------|---------|----------|
| **[WIDGET_TEMPLATE_GUIDE.md](WIDGET_TEMPLATE_GUIDE.md)** | Complete implementation guide | Developers building new widgets |
| **[REUSABLE_PATTERNS.md](REUSABLE_PATTERNS.md)** | Quick reference & patterns | Developers familiar with basics |
| **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** | System architecture & flow | Technical leads, architects |
| **[create-widget-project.sh](create-widget-project.sh)** | Project generator script | Quick start for new projects |

---

## 🚀 Quick Start

### For Beginners

1. Read **[WIDGET_TEMPLATE_GUIDE.md](WIDGET_TEMPLATE_GUIDE.md)** (30 min)
2. Run the generator script:
   ```bash
   ./create-widget-project.sh my-first-widget
   ```
3. Follow the generated README.md

### For Experienced Developers

1. Skim **[REUSABLE_PATTERNS.md](REUSABLE_PATTERNS.md)** (5 min)
2. Copy reusable hooks from `../web/src/hooks/`
3. Adapt server template from `../server_apps_sdk.py`

### For Architects

1. Review **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)** (15 min)
2. Understand data flow and security model
3. Plan your widget architecture

---

## 📖 What's Inside

### 1. WIDGET_TEMPLATE_GUIDE.md

**Complete implementation guide with:**
- ✅ Server-side template (FastMCP + Apps SDK)
- ✅ Client-side template (React + TypeScript)
- ✅ Reusable hooks (copy-paste ready)
- ✅ Project structure
- ✅ TypeScript types
- ✅ CSS template
- ✅ Quick start checklist

**Use when:** Building a widget from scratch

### 2. REUSABLE_PATTERNS.md

**Quick reference with:**
- ✅ List of 100% reusable files
- ✅ Core patterns (server, widget, data flow)
- ✅ Common customizations
- ✅ Testing workflow
- ✅ Debugging tips
- ✅ Migration path

**Use when:** You know the basics, need quick answers

### 3. ARCHITECTURE_DIAGRAM.md

**System architecture with:**
- ✅ High-level flow diagrams
- ✅ Component architecture
- ✅ Data flow diagrams
- ✅ Key interfaces
- ✅ Build process
- ✅ Security model
- ✅ Performance considerations

**Use when:** Understanding how everything fits together

### 4. create-widget-project.sh

**Project generator that creates:**
- ✅ Complete project structure
- ✅ Reusable hooks (pre-configured)
- ✅ Server template
- ✅ Widget template
- ✅ Build configuration
- ✅ README with instructions

**Use when:** Starting a new widget project

---

## 🎯 What You Can Build

### Widget Types

1. **List/Grid Widgets** (like Property Server)
   - Display collections of items
   - Sorting, filtering, favorites
   - Example: Properties, products, search results

2. **Dashboard Widgets**
   - Charts, metrics, KPIs
   - Real-time data visualization
   - Example: Analytics, monitoring

3. **Form Widgets**
   - Interactive forms
   - Multi-step workflows
   - Example: Booking, configuration

4. **Detail Widgets**
   - Single item deep-dive
   - Rich media, galleries
   - Example: Product details, profiles

5. **Comparison Widgets**
   - Side-by-side comparisons
   - Feature matrices
   - Example: Product comparison, pricing

---

## 🔧 Reusable Components

### 100% Reusable (Copy As-Is)

```
web/src/hooks/
├── useOpenAiGlobal.ts    ✅ Core ChatGPT API integration
├── useToolOutput.ts      ✅ Read tool data
├── useWidgetState.ts     ✅ Persist state
└── useTheme.ts           ✅ Dark mode support

web/src/index.tsx         ✅ React entry point
web/package.json          ✅ Build config (update name)
web/tsconfig.json         ✅ TypeScript config
```

### Template-Based (Adapt to Your Needs)

```
server.py                 🔧 FastMCP server structure
web/src/Widget.tsx        🔧 Main widget component
web/src/types/*.ts        🔧 TypeScript types
web/src/styles/index.css  🔧 CSS variables & styles
```

---

## 📊 Success Metrics

### Property Server Widget (Reference Implementation)

- **Bundle Size:** 149KB (minified)
- **Load Time:** < 1 second
- **Features:** 
  - ✅ 475 properties displayed
  - ✅ Favorites with persistence
  - ✅ Sorting (price, bedrooms)
  - ✅ Dark mode support
  - ✅ Responsive design
- **Status:** ✅ Production-ready in ChatGPT

### Your Widget Should Achieve

- **Bundle Size:** < 500KB
- **Load Time:** < 2 seconds
- **Features:**
  - ✅ Loading state
  - ✅ Empty state
  - ✅ Error handling
  - ✅ Basic interactions
  - ✅ State persistence (optional)

---

## 🛠️ Technology Stack

### Server Side
- **Framework:** FastMCP 2.13+
- **Transport:** Streamable HTTP
- **Language:** Python 3.12+
- **Dependencies:** `fastmcp[http]`

### Client Side
- **Framework:** React 18.2+
- **Language:** TypeScript 5.3+
- **Build Tool:** esbuild 0.19+
- **Bundle Format:** ESM

### Integration
- **Protocol:** MCP (Model Context Protocol)
- **API:** OpenAI Apps SDK
- **MIME Type:** `text/html+skybridge`
- **Communication:** `window.openai` API

---

## 📋 Implementation Checklist

### Planning Phase
- [ ] Define your data structure
- [ ] Sketch widget UI
- [ ] List required interactions
- [ ] Plan state management

### Development Phase
- [ ] Set up project (use generator)
- [ ] Implement server tool
- [ ] Build widget UI
- [ ] Add interactions
- [ ] Test locally

### Testing Phase
- [ ] Test in browser (http://localhost:8000/widget)
- [ ] Test with ngrok + ChatGPT
- [ ] Test dark mode
- [ ] Test state persistence
- [ ] Test edge cases

### Deployment Phase
- [ ] Optimize bundle size
- [ ] Add error handling
- [ ] Document usage
- [ ] Deploy to production

---

## 🐛 Common Issues & Solutions

### Issue: Widget Not Rendering

**Symptoms:** ChatGPT shows text response, no widget

**Solutions:**
1. Check `_meta` fields in tool definition
2. Verify `WIDGET_URI` matches in tool and resource
3. Confirm `MIME_TYPE = "text/html+skybridge"`
4. Ensure widget bundle is built

### Issue: Data Not Showing

**Symptoms:** Widget renders but shows "Loading..." or empty

**Solutions:**
1. Check `structuredContent` in tool response
2. Verify `window.openai.toolOutput` in console
3. Check widget is reading correct field
4. Add console.log in useToolOutput hook

### Issue: Styles Not Applied

**Symptoms:** Widget renders but looks unstyled

**Solutions:**
1. Verify CSS is injected into HTML template
2. Check CSS variables are defined
3. Confirm `data-theme` attribute is set
4. Test CSS in browser DevTools

### Issue: State Not Persisting

**Symptoms:** Favorites/settings reset on reload

**Solutions:**
1. Use `useWidgetState` hook, not `useState`
2. Verify `window.openai.setWidgetState` exists
3. Check state format is serializable
4. Test in actual ChatGPT (not local browser)

---

## 📚 Learning Path

### Level 1: Beginner (0-2 hours)
1. Read WIDGET_TEMPLATE_GUIDE.md
2. Run generator script
3. Build and test example widget
4. Understand basic data flow

### Level 2: Intermediate (2-8 hours)
1. Customize widget UI
2. Add sorting/filtering
3. Implement state persistence
4. Test in ChatGPT

### Level 3: Advanced (8+ hours)
1. Optimize performance
2. Add complex interactions
3. Implement error boundaries
4. Build production-ready widget

---

## 🔗 External Resources

### Official Documentation
- [FastMCP Docs](https://gofastmcp.com)
- [MCP Protocol Spec](https://modelcontextprotocol.io)
- [OpenAI Apps SDK](https://platform.openai.com/docs/mcp)
- [ChatGPT Developer Mode](https://platform.openai.com/docs/guides/developer-mode)

### Example Implementations
- [Property Server](../server_apps_sdk.py) - This project
- [OpenAI Pizzaz Example](https://github.com/openai/pizzaz_server_python) - Official example

### Community
- [FastMCP GitHub](https://github.com/jlowin/fastmcp)
- [MCP Specification](https://spec.modelcontextprotocol.io)

---

## 🤝 Contributing

Found a bug or have an improvement?

1. Test your change with the Property Server
2. Update relevant documentation
3. Add example if applicable
4. Submit with clear description

---

## 📝 Version History

### v1.0 (November 2025)
- ✅ Initial templates based on Property Server
- ✅ Complete documentation suite
- ✅ Project generator script
- ✅ Reusable hooks library
- ✅ Architecture diagrams

---

## 🎓 Next Steps

### If You're New
1. Start with **[WIDGET_TEMPLATE_GUIDE.md](WIDGET_TEMPLATE_GUIDE.md)**
2. Run the generator: `./create-widget-project.sh test-widget`
3. Follow the generated README
4. Join the learning path at Level 1

### If You're Experienced
1. Skim **[REUSABLE_PATTERNS.md](REUSABLE_PATTERNS.md)**
2. Copy reusable hooks
3. Adapt templates to your needs
4. Reference architecture as needed

### If You're Architecting
1. Review **[ARCHITECTURE_DIAGRAM.md](ARCHITECTURE_DIAGRAM.md)**
2. Plan your widget ecosystem
3. Define standards for your team
4. Build on proven patterns

---

## ✨ Success Stories

### Property Server Widget
- **Built in:** 3 days
- **Lines of Code:** ~800 (server + widget)
- **Bundle Size:** 149KB
- **Status:** ✅ Production in ChatGPT
- **Features:** List, sort, filter, favorites, dark mode

**Your widget can achieve similar results!**

---

## 📞 Support

### Documentation Issues
- Check all 4 documentation files
- Review architecture diagrams
- Test with Property Server example

### Technical Issues
- Enable browser DevTools
- Check server logs
- Verify `window.openai` object
- Test locally before ChatGPT

### Questions
- Review FAQ in WIDGET_TEMPLATE_GUIDE.md
- Check debugging tips in REUSABLE_PATTERNS.md
- Examine working example in ../server_apps_sdk.py

---

**Ready to build? Start with [WIDGET_TEMPLATE_GUIDE.md](WIDGET_TEMPLATE_GUIDE.md)!** 🚀
