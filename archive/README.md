# Archive - Old Implementations

This directory contains previous server implementations and test files that are no longer used.

**Current Active Server:** `server_apps_sdk.py` (in root directory)

---

## Old Servers (`old_servers/`)

### server.py
**Status:** Superseded  
**Description:** Original FastMCP server implementation  
**Why Archived:** Didn't support Apps SDK widget metadata properly

### server_mcp_sdk.py
**Status:** Superseded  
**Description:** Attempt using official MCP SDK  
**Why Archived:** Couldn't get Apps SDK format working correctly

### server_chatgpt_compatible.py
**Status:** Superseded  
**Description:** Tools-only version for ChatGPT  
**Why Archived:** No widget support, text-only responses

### main.py
**Status:** Unknown/Unused  
**Description:** Unknown purpose  
**Why Archived:** Not referenced anywhere

---

## Old Tests (`old_tests/`)

### test_server.py
**Status:** Outdated  
**Description:** Tests for old server.py  
**Why Archived:** Tests old implementation

### test_fastmcp_response.py
**Status:** Experimental  
**Description:** FastMCP response format testing  
**Why Archived:** Debugging tool, no longer needed

### test_resource_response.py
**Status:** Experimental  
**Description:** Resource response testing  
**Why Archived:** Debugging tool, no longer needed

### mcp_client_example.py
**Status:** Example  
**Description:** MCP client example code  
**Why Archived:** Not used in production

---

## What's Currently Active

### Root Directory Files

**Production:**
- `server_apps_sdk.py` - ✅ **MAIN SERVER** (ChatGPT Apps SDK with widgets)
- `tools.py` - Business logic for property queries
- `data_loader.py` - Loads property data from JSONL

**Scripts:**
- `deploy_apps_sdk.sh` - Deployment script
- `test_endpoints.sh` - Endpoint testing script

**Configuration:**
- `pyproject.toml` - Project metadata
- `requirements.txt` - Python dependencies
- `pytest.ini` - Pytest configuration

---

## Migration History

**Date:** November 12, 2025

**Reason:** Successful ChatGPT Apps SDK widget integration achieved with `server_apps_sdk.py`

**Changes:**
1. Moved 4 old server implementations to `archive/old_servers/`
2. Moved 4 test files to `archive/old_tests/`
3. Kept only 3 active Python files in root

**Result:** Clean, focused codebase with single source of truth

---

## If You Need These Files

These files are preserved in git history and in this archive directory. They can be:
- Referenced for learning purposes
- Restored if needed
- Used for comparison with current implementation

To restore a file:
```bash
git mv archive/old_servers/server.py ./
```

---

## Key Learnings from Old Implementations

### What Didn't Work

1. **server.py (FastMCP)**
   - Standard FastMCP decorators don't support `_meta` fields
   - Resource format wasn't Apps SDK compatible

2. **server_mcp_sdk.py (Official SDK)**
   - Tried to encode Apps SDK data as JSON in TextContent
   - Didn't use `stateless_http=True`
   - Wrong transport type

3. **server_chatgpt_compatible.py**
   - Tools-only, no widget support
   - Acknowledged ChatGPT limitations but didn't solve them

### What Finally Worked (server_apps_sdk.py)

1. ✅ FastMCP with `stateless_http=True`
2. ✅ Custom request handlers for `_meta` fields
3. ✅ Streamable HTTP transport
4. ✅ Proper Apps SDK annotations
5. ✅ CSS injection for styling
6. ✅ Based on official OpenAI example

---

## Documentation

For current implementation details, see:
- `CHATGPT_WIDGET_GUIDE.md` - Complete guide
- `WIDGET_RENDERING.md` - Success story
- `README_APPS_SDK.md` - Apps SDK reference

---

## Old Documentation (`old_docs/`)

### Widget Documentation (6 files)
**Status:** Superseded  
**Why Archived:** All widget documentation consolidated into `CHATGPT_WIDGET_GUIDE.md`

- `WIDGET_DEPLOYMENT.md` - Deployment guide
- `WIDGET_FIX_SUMMARY.md` - Fix summary
- `WIDGET_IMPLEMENTATION_PLAN.md` - Implementation plan
- `WIDGET_NOT_RENDERING_DIAGNOSIS.md` - Troubleshooting
- `WIDGET_QUICK_START.md` - Quick start
- `WIDGET_SUMMARY.md` - Summary

### Project Documentation (3 files)
**Status:** Outdated  
**Why Archived:** Reference old `server.py`, superseded by current implementation

- `CHATGPT_SETUP.md` - Old ChatGPT setup (references old ngrok URL)
- `MCP_LEARNINGS.md` - MCP learnings (still useful for reference)
- `SUMMARY.md` - Old project summary (references `server.py`)

### Testing Documentation (1 file)
**Status:** Outdated  
**Why Archived:** Problem already solved in `server_apps_sdk.py`

- `TESTING_APPS_SDK.md` - Apps SDK testing (discusses problems we solved)

### Deployment Documentation (7 files)

### APPS_SDK_DEPLOYMENT.md
**Status:** Superseded  
**Description:** Step-by-step deployment guide  
**Why Archived:** Consolidated into `CHATGPT_WIDGET_GUIDE.md`

### APPS_SDK_IMPLEMENTATION.md
**Status:** Superseded  
**Description:** Implementation details  
**Why Archived:** Consolidated into `CHATGPT_WIDGET_GUIDE.md`

### FINAL_SETUP.md
**Status:** Superseded  
**Description:** Final setup instructions  
**Why Archived:** Consolidated into `CHATGPT_WIDGET_GUIDE.md`

### QUICK_START_CHATGPT.md
**Status:** Superseded  
**Description:** Quick start guide  
**Why Archived:** Consolidated into `CHATGPT_WIDGET_GUIDE.md`

### README_APPS_SDK.md
**Status:** Superseded  
**Description:** Apps SDK reference  
**Why Archived:** Consolidated into `CHATGPT_WIDGET_GUIDE.md`

### IMPROVEMENTS.md
**Status:** Historical  
**Description:** Tool description improvements  
**Why Archived:** Historical record, improvements already applied

### NEXT_SESSION_PROMPT.md
**Status:** Old Planning  
**Description:** Next session context  
**Why Archived:** Session completed, no longer needed

---

## Current Documentation Structure

**Root Directory:**
- `README.md` - Main project overview
- `CHATGPT_WIDGET_GUIDE.md` - **Complete guide** (single source of truth)
- `SUCCESS.md` - Success story (widget recognition)
- `WIDGET_RENDERING.md` - Success story (widget rendering)
- `NOTES.md` - Development notes and learnings

**All information consolidated into `CHATGPT_WIDGET_GUIDE.md`**
