"""
Test script for lead capture tools
"""
import tools
import json

print("=" * 60)
print("TESTING LEAD CAPTURE TOOLS")
print("=" * 60)

# Test 1: View existing leads
print("\n1. VIEW EXISTING LEADS")
print("-" * 60)
result = tools.view_leads()
print(f"Total leads: {result['total_results']}")
print(f"Summary: {json.dumps(result['summary'], indent=2)}")

# Test 2: View only buyers
print("\n2. VIEW BUYER LEADS ONLY")
print("-" * 60)
result = tools.view_leads(role="buyer")
print(f"Total buyers: {result['total_results']}")
for lead in result['leads'][:3]:
    print(f"  - {lead['full_name']} ({lead['client_id']}) - Stage: {lead['stage']}")

# Test 3: View hot leads
print("\n3. VIEW HOT LEADS")
print("-" * 60)
result = tools.view_leads(stage="hot")
print(f"Total hot leads: {result['total_results']}")
for lead in result['leads']:
    print(f"  - {lead['full_name']} ({lead['role']}) - Budget: £{lead.get('budget_max', 'N/A')}")

# Test 4: Match client to properties
print("\n4. MATCH CLIENT TO PROPERTIES")
print("-" * 60)
result = tools.match_client(client_id="C0001", limit=5)
if "error" not in result:
    print(f"Client: {result['filters_applied']['client_name']}")
    print(f"Budget: £{result['filters_applied']['max_price']}")
    print(f"Min bedrooms: {result['filters_applied']['min_bedrooms']}")
    print(f"Matching properties: {result['total_results']}")
    for prop in result['properties'][:3]:
        print(f"  - {prop['property_id']}: £{prop['price_amount']} - {prop['bedrooms']} bed {prop['property_type']}")
else:
    print(f"Error: {result['error']}")

# Test 5: Capture new lead (buyer)
print("\n5. CAPTURE NEW BUYER LEAD")
print("-" * 60)
result = tools.capture_lead(
    full_name="Test Buyer",
    email="test.buyer@example.com",
    mobile="+44 7700 999999",
    role="buyer",
    stage="hot",
    budget_max=100000,
    min_bedrooms=2
)
if "error" not in result:
    print(f"✅ {result['message']}")
    print(f"Client ID: {result['client']['client_id']}")
else:
    print(f"Error: {result['error']}")

# Test 6: Schedule viewing
print("\n6. SCHEDULE VIEWING")
print("-" * 60)
result = tools.schedule_viewing(
    property_id="32926983",
    buyer_client_id="C0001",
    datetime_iso="2025-11-25T15:00:00Z",
    notes="First viewing"
)
if "error" not in result:
    print(f"✅ {result['message']}")
    print(f"Viewing ID: {result['viewing_id']}")
    print(f"Buyer: {result['buyer']}")
    print(f"Date: {result['datetime']}")
else:
    print(f"Error: {result['error']}")

# Test 7: Try to schedule conflicting viewing
print("\n7. TEST CONFLICT DETECTION")
print("-" * 60)
result = tools.schedule_viewing(
    property_id="32926983",
    buyer_client_id="C0003",
    datetime_iso="2025-11-25T15:30:00Z",  # Within 1 hour of previous
    notes="Should conflict"
)
if "error" in result:
    print(f"✅ Conflict detected correctly: {result['error']}")
else:
    print(f"❌ Should have detected conflict!")

# Test 8: Try to schedule on sold property
print("\n8. TEST SOLD PROPERTY VALIDATION")
print("-" * 60)
# First, find a sold property
from data_loader import get_listings_data
sold_property = None
for listing in get_listings_data():
    if "sold" in listing.get("status", "").lower():
        sold_property = listing["property_id"]
        break

if sold_property:
    result = tools.schedule_viewing(
        property_id=sold_property,
        buyer_client_id="C0001",
        datetime_iso="2025-11-26T10:00:00Z"
    )
    if "error" in result:
        print(f"✅ Sold property check works: {result['error']}")
    else:
        print(f"❌ Should have rejected sold property!")
else:
    print("⚠️  No sold properties found in dataset")

print("\n" + "=" * 60)
print("TESTS COMPLETE")
print("=" * 60)
