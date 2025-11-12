# Lead Capture Feature

**Status:** ✅ Implemented and tested  
**Date:** November 12, 2025

## Overview

The Property MCP Server now includes **lead capture and CRM functionality** to demonstrate MCP's value for estate agents. This feature adds 4 new tools that enable ChatGPT to capture leads, match clients to properties, schedule viewings, and manage the sales pipeline.

---

## New Tools

### 1. **capture_lead**
Captures new buyer or seller leads from ChatGPT conversations.

**Use cases:**
- "I'm interested in buying a property"
- "I want to sell my house"
- User provides contact information

**Parameters:**
- `full_name` (required): Client's full name
- `email` (required): Email address
- `mobile` (required): Mobile phone number
- `role` (required): "buyer" or "seller"
- `stage`: Lead stage - "hot", "warm", "cold", "instructed", "completed" (default: "warm")
- `budget_max`: Maximum budget for buyers
- `min_bedrooms`: Minimum bedrooms for buyers
- `interested_property_id`: Property ID buyer is interested in
- `selling_property_id`: Property ID seller is selling (required for sellers)
- `asking_price`: Asking price for sellers (required for sellers)

**Returns:**
- New client record with auto-generated `client_id`
- Persisted to `data/clients.jsonl`

**Example:**
```json
{
  "client_id": "C0011",
  "role": "buyer",
  "full_name": "Sarah Mitchell",
  "contact": {
    "email": "sarah.mitchell@example.com",
    "mobile": "+44 7700 900001"
  },
  "lead_source": "ChatGPT",
  "stage": "hot",
  "budget_max": 95000,
  "min_bedrooms": 2,
  "interested_property_ids": [],
  "viewings": [],
  "created_at": "2025-11-12T18:30:00Z"
}
```

---

### 2. **match_client**
Finds properties matching a buyer's preferences and budget.

**Use cases:**
- "Show properties for client C0001"
- "Find matches for Sarah"
- "What properties fit this buyer's needs?"

**Parameters:**
- `client_id` (required): Buyer's client ID (e.g., "C0001")
- `limit`: Maximum results (default: 10)

**Returns:**
- Matching properties in **property widget format** (reuses existing widget)
- Filters out sold properties
- Matches based on `budget_max` and `min_bedrooms`

**Validation:**
- Only works for buyers (not sellers)
- Returns error if client not found

---

### 3. **schedule_viewing**
Books a property viewing for a buyer.

**Use cases:**
- "Book a viewing for property 34203646"
- "Schedule viewing for client C0001"
- "Arrange property visit"

**Parameters:**
- `property_id` (required): Property ID to view
- `buyer_client_id` (required): Buyer's client ID
- `datetime_iso` (required): Viewing datetime in ISO format (e.g., "2025-11-20T14:00:00Z")
- `notes`: Optional notes

**Returns:**
- Viewing confirmation with `viewing_id`
- Updates **both** buyer and seller records

**Validation:**
- ✅ Checks property exists
- ✅ Checks property is not sold
- ✅ Checks for datetime conflicts (1-hour window)
- ✅ Validates buyer exists and is a buyer (not seller)

**Example viewing record:**
```json
{
  "viewing_id": "V1004",
  "property_id": "34203646",
  "datetime": "2025-11-25T15:00:00Z",
  "status": "booked",
  "notes": "First viewing"
}
```

---

### 4. **view_leads**
Views and filters client leads for estate agents.

**Use cases:**
- "Show me all hot leads"
- "List buyer leads"
- "Show sellers"
- "View my pipeline"

**Parameters:**
- `role`: Filter by "buyer" or "seller" (optional)
- `stage`: Filter by stage (optional)
- `limit`: Maximum results (default: 20)

**Returns:**
- Filtered list of client records
- Summary statistics (total buyers, sellers, hot leads)
- Sorted by `created_at` (newest first)

**Example response:**
```json
{
  "message": "Found 6 leads matching criteria",
  "leads": [...],
  "total_results": 6,
  "showing": 6,
  "summary": {
    "total_buyers": 6,
    "total_sellers": 4,
    "hot_leads": 3,
    "total_clients": 10
  }
}
```

---

## Data Schema

### Client Record Structure

```json
{
  "client_id": "C0001",
  "role": "buyer" | "seller",
  "full_name": "Sarah Mitchell",
  "contact": {
    "email": "sarah.mitchell@example.com",
    "mobile": "+44 7700 900001"
  },
  "lead_source": "ChatGPT",
  "stage": "hot" | "warm" | "cold" | "instructed" | "completed",
  
  // BUYER-SPECIFIC (only if role="buyer")
  "budget_max": 95000,
  "min_bedrooms": 2,
  "interested_property_ids": ["34187182"],
  
  // SELLER-SPECIFIC (only if role="seller")
  "selling_property_id": "32926983",
  "asking_price": 81995,
  
  // SHARED
  "viewings": [
    {
      "viewing_id": "V1001",
      "property_id": "32926983",
      "datetime": "2025-11-20T14:00:00Z",
      "status": "booked" | "attended" | "cancelled" | "no_show"
    }
  ],
  "created_at": "2025-11-01T10:30:00Z"
}
```

---

## Implementation Details

### Files Modified

1. **`data/clients.jsonl`** (NEW)
   - 10 sample client records (6 buyers, 4 sellers)
   - Persisted client data

2. **`data_loader.py`**
   - Added `load_jsonl()` and `save_jsonl()` functions
   - Added `get_clients_data()`, `add_client()`, `update_client()`
   - Added `get_client_by_id()`, `get_next_client_id()`, `get_next_viewing_id()`

3. **`tools.py`**
   - Added 4 new tool functions
   - All tools return `{content, structuredContent, _meta}` format
   - Proper error handling and validation

4. **`server_apps_sdk.py`**
   - Registered 4 new tools with Apps SDK metadata
   - Added handlers in `_call_tool_request()`
   - Proper `readOnlyHint` annotations (False for write operations)

### Data Persistence

- All client data stored in `data/clients.jsonl`
- **Write operations** (`capture_lead`, `schedule_viewing`) persist immediately
- **Read operations** (`match_client`, `view_leads`) use in-memory data
- Auto-incrementing IDs: `C0001`, `C0002`, etc.
- Auto-incrementing viewing IDs: `V1001`, `V1002`, etc.

### Widget Integration

- **`match_client`** reuses the existing **property widget** (same format as `query_listings`)
- **`view_leads`** returns structured data (could add dedicated widget later)
- **`capture_lead`** and **`schedule_viewing`** return confirmation messages

---

## Testing

Run the test suite:

```bash
python3 test_lead_tools.py
```

**Test coverage:**
- ✅ View existing leads
- ✅ Filter by role (buyer/seller)
- ✅ Filter by stage (hot/warm/cold)
- ✅ Match client to properties
- ✅ Capture new lead
- ✅ Schedule viewing
- ✅ Conflict detection (1-hour window)
- ✅ Sold property validation

---

## ChatGPT Usage Examples

### Example 1: Capture Lead
**User:** "I'm interested in buying a property. My name is John Smith, email john@example.com, mobile +44 7700 123456. My budget is £120,000 and I need at least 2 bedrooms."

**ChatGPT calls:** `capture_lead(full_name="John Smith", email="john@example.com", mobile="+44 7700 123456", role="buyer", budget_max=120000, min_bedrooms=2)`

**Result:** New client C0012 created

---

### Example 2: Match Client
**User:** "Show me properties for client C0001"

**ChatGPT calls:** `match_client(client_id="C0001")`

**Result:** Property widget displays with matching properties

---

### Example 3: Schedule Viewing
**User:** "Book a viewing for property 34203646 for client C0001 on November 25th at 3pm"

**ChatGPT calls:** `schedule_viewing(property_id="34203646", buyer_client_id="C0001", datetime_iso="2025-11-25T15:00:00Z")`

**Result:** Viewing V1005 created, both buyer and seller records updated

---

### Example 4: View Pipeline
**User:** "Show me all hot leads"

**ChatGPT calls:** `view_leads(stage="hot")`

**Result:** List of 3 hot leads with details

---

## Business Value

This feature demonstrates how MCP can:

1. **Capture leads naturally** from conversations
2. **Match clients to inventory** automatically
3. **Manage viewings** with conflict detection
4. **Track pipeline** with stage-based filtering
5. **Persist data** for CRM functionality
6. **Reuse widgets** (property widget for matching)

---

## Future Enhancements

Potential additions:
- [ ] Dedicated leads widget (client cards UI)
- [ ] Email/SMS notifications for viewings
- [ ] Offer management
- [ ] Viewing feedback capture
- [ ] Agent assignment and routing
- [ ] Lead scoring based on engagement
- [ ] Integration with external CRM systems

---

## Notes

- All lead sources are "ChatGPT" (server only works with ChatGPT Apps SDK)
- Simplified schema (removed unnecessary fields from original mock data)
- 1-hour conflict window for viewings (configurable)
- Sold properties automatically excluded from matching and viewing scheduling
- Client IDs auto-increment from existing max
- Viewing IDs start at V1001 and increment

---

**Ready for ChatGPT deployment!** 🚀
