from typing import List, Dict, Any, Optional
from datetime import datetime
from data_loader import (
    get_listings_data,
    get_clients_data,
    add_client,
    update_client,
    get_client_by_id,
    get_next_client_id,
    get_next_viewing_id
)

def get_schema() -> Dict[str, str]:
    """
    Returns the data schema (a dictionary of field names and their types) 
    to help the AI understand what can be queried.
    """
    return {
        "property_id": "string",
        "price_amount": "number",
        "bedrooms": "number",
        "bathrooms": "number",
        "property_type": "string",
        "postcode": "string",
        "garden": "boolean",
        "parking": "boolean",
        "status": "string (e.g., 'Sold Subject to Contract')",
        "overview": "list of strings",
        "description": "string"
    }

def query_listings(
    postcode: Optional[str] = None, 
    property_type: Optional[str] = None,
    max_price: Optional[int] = None, 
    min_bedrooms: Optional[int] = None,
    has_garden: Optional[bool] = None,
    has_parking: Optional[bool] = None,
    limit: int = 5
) -> Dict[str, Any]:
    """
    Use this when the user wants to find, search, or browse properties for sale.
    Searches 475 property listings and filters by location, price, bedrooms, garden, and parking.
    Returns up to 5 matching properties by default.

    Args:
        postcode: Partial or full UK postcode (e.g., "LE65" matches "LE65 1DA", "LE65 2AY", etc. or "DY4" for all DY4 postcodes). Case-insensitive.
        property_type: Type of property (e.g., "Flat", "House", "Cottage", "Apartment"). Partial matches work (e.g., "flat" matches "Flat - Ground Floor").
        max_price: Maximum price in GBP (e.g., 200000 for £200,000). Only returns properties at or below this price.
        min_bedrooms: Minimum number of bedrooms (e.g., 2 returns properties with 2 or more bedrooms).
        has_garden: Set to True to only show properties with a garden. Set to False to only show properties without a garden. Leave None to include both.
        has_parking: Set to True to only show properties with parking. Set to False to only show properties without parking. Leave None to include both.
        limit: Maximum number of results to return (default: 5, increase for more results).
    """
    print(f"Tool: Received query with criteria: postcode={postcode}, max_price={max_price}, min_bedrooms={min_bedrooms}, garden={has_garden}, parking={has_parking}")
    
    # Get the full list of data
    all_listings = get_listings_data()
    
    # This is our "fat server" logic. We filter the data here in Python.
    filtered_results = []
    for listing in all_listings:
        # Apply filters one by one
        if max_price is not None and listing.get('price_amount', 0) > max_price:
            continue
        if min_bedrooms is not None and listing.get('bedrooms', 0) < min_bedrooms:
            continue
        if has_garden is not None and listing.get('garden') != has_garden:
            continue
        if has_parking is not None and listing.get('parking') != has_parking:
            continue
            
        # For string-based searches, we can check if it's 'contained'
        # Postcode: check if listing postcode starts with the search term (e.g., "LE65" matches "LE65 1DA")
        if postcode is not None:
            listing_postcode = listing.get('postcode', '')
            if not listing_postcode.upper().startswith(postcode.upper()):
                continue
        if property_type is not None and property_type.lower() not in listing.get('property_type', '').lower():
            continue
            
        # If all checks passed, add it to the list
        filtered_results.append(listing)
    
    # Return enhanced response structure for widget
    payload = {
        "properties": filtered_results[:limit],
        "filters_applied": {
            "postcode": postcode,
            "property_type": property_type,
            "max_price": max_price,
            "min_bedrooms": min_bedrooms,
            "has_garden": has_garden,
            "has_parking": has_parking,
        },
        "total_results": len(filtered_results),
        "showing": min(limit, len(filtered_results)),
    }

    # For Apps SDK, ChatGPT hydrates the component from `structuredContent`.
    # Keep top-level keys for backwards-compatibility with existing tests.
    payload["structuredContent"] = {
        "properties": payload["properties"],
        "filters_applied": payload["filters_applied"],
        "total_results": payload["total_results"],
        "showing": payload["showing"],
    }

    return payload


def calculate_average_price(
    postcode: Optional[str] = None,
    property_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Use this when the user asks about average prices, price trends, or typical costs in an area.
    Calculates the average price for properties matching the given postcode or property type.
    Provide at least one filter (postcode or property_type).

    Args:
        postcode: Partial or full UK postcode (e.g., "LE65" for all LE65 postcodes, "DY4 7LG" for specific area). Case-insensitive.
        property_type: Type of property (e.g., "Flat", "House", "Cottage"). Partial matches work.
    """
    all_listings = get_listings_data()
    
    total_price = 0
    count = 0

    for listing in all_listings:
        # Check if the listing matches our filters
        # Postcode: check if listing postcode starts with the search term
        if postcode is not None:
            listing_postcode = listing.get('postcode', '')
            if not listing_postcode.upper().startswith(postcode.upper()):
                continue
        if property_type is not None and property_type.lower() not in listing.get('property_type', '').lower():
            continue
        
        # Add its price to the total
        if 'price_amount' in listing:
            total_price += listing['price_amount']
            count += 1
    
    if count == 0:
        return {"message": "No listings found matching criteria.", "average_price": None, "count": 0}
        
    avg_price = total_price / count
    
    return {
        "message": f"Found {count} matching listings.",
        "average_price": round(avg_price, 2),
        "count": count
    }


# ============================================================================
# LEAD CAPTURE TOOLS
# ============================================================================

def capture_lead(
    full_name: str,
    email: str,
    mobile: str,
    role: str,
    stage: str = "warm",
    budget_max: Optional[int] = None,
    min_bedrooms: Optional[int] = None,
    interested_property_id: Optional[str] = None,
    selling_property_id: Optional[str] = None,
    asking_price: Optional[int] = None
) -> Dict[str, Any]:
    """
    Capture a new lead from ChatGPT conversation. Creates a new client record.
    Use this when someone expresses interest in buying or selling property.
    
    Args:
        full_name: Client's full name (e.g., "Sarah Mitchell")
        email: Email address
        mobile: Mobile phone number (e.g., "+44 7700 900001")
        role: Either "buyer" or "seller"
        stage: Lead stage - "hot", "warm", "cold", "instructed", or "completed" (default: "warm")
        budget_max: Maximum budget for buyers (e.g., 95000 for £95,000)
        min_bedrooms: Minimum bedrooms required for buyers (e.g., 2)
        interested_property_id: Property ID buyer is interested in (optional)
        selling_property_id: Property ID seller is selling (required for sellers)
        asking_price: Asking price for sellers (required for sellers)
    
    Returns:
        New client record with generated client_id
    """
    # Validate role
    if role not in ["buyer", "seller"]:
        return {"error": "Role must be 'buyer' or 'seller'"}
    
    # Validate seller requirements
    if role == "seller" and (not selling_property_id or not asking_price):
        return {"error": "Sellers must provide selling_property_id and asking_price"}
    
    # Generate new client ID
    client_id = get_next_client_id()
    
    # Build client record
    client = {
        "client_id": client_id,
        "role": role,
        "full_name": full_name,
        "contact": {
            "email": email,
            "mobile": mobile
        },
        "lead_source": "ChatGPT",
        "stage": stage,
        "viewings": [],
        "created_at": datetime.utcnow().isoformat() + "Z"
    }
    
    # Add buyer-specific fields
    if role == "buyer":
        if budget_max:
            client["budget_max"] = budget_max
        if min_bedrooms:
            client["min_bedrooms"] = min_bedrooms
        
        interested_ids = []
        if interested_property_id:
            interested_ids.append(interested_property_id)
        client["interested_property_ids"] = interested_ids
    
    # Add seller-specific fields
    if role == "seller":
        client["selling_property_id"] = selling_property_id
        client["asking_price"] = asking_price
    
    # Save to database
    success = add_client(client)
    
    if success:
        return {
            "message": f"✅ Lead captured successfully! Client ID: {client_id}",
            "client": client,
            "structuredContent": {"client": client}
        }
    else:
        return {"error": "Failed to save client record"}


def match_client(
    client_id: str,
    limit: int = 10
) -> Dict[str, Any]:
    """
    Find properties matching a buyer's preferences and budget.
    Returns results in the property widget format for display.
    
    Args:
        client_id: The buyer's client ID (e.g., "C0001")
        limit: Maximum number of matching properties to return (default: 10)
    
    Returns:
        Matching properties in widget format (reuses property widget)
    """
    # Get client record
    client = get_client_by_id(client_id)
    if not client:
        return {"error": f"Client {client_id} not found"}
    
    # Validate it's a buyer
    if client.get("role") != "buyer":
        return {"error": f"Client {client_id} is a seller, not a buyer. Only buyers can be matched to properties."}
    
    # Extract buyer preferences
    budget_max = client.get("budget_max")
    min_bedrooms = client.get("min_bedrooms")
    
    # Get all properties
    all_listings = get_listings_data()
    
    # Filter properties
    matches = []
    for listing in all_listings:
        # Skip sold properties
        status = listing.get("status", "").lower()
        if "sold" in status:
            continue
        
        # Check budget
        if budget_max and listing.get("price_amount", 0) > budget_max:
            continue
        
        # Check bedrooms
        if min_bedrooms and listing.get("bedrooms", 0) < min_bedrooms:
            continue
        
        matches.append(listing)
    
    # Return in property widget format (reuse existing widget)
    payload = {
        "properties": matches[:limit],
        "filters_applied": {
            "client_id": client_id,
            "client_name": client.get("full_name"),
            "max_price": budget_max,
            "min_bedrooms": min_bedrooms,
        },
        "total_results": len(matches),
        "showing": min(limit, len(matches)),
    }
    
    payload["structuredContent"] = {
        "properties": payload["properties"],
        "filters_applied": payload["filters_applied"],
        "total_results": payload["total_results"],
        "showing": payload["showing"],
    }
    
    return payload


def schedule_viewing(
    property_id: str,
    buyer_client_id: str,
    datetime_iso: str,
    notes: Optional[str] = None
) -> Dict[str, Any]:
    """
    Schedule a property viewing for a buyer. Updates both buyer and seller records.
    Validates property availability and datetime conflicts.
    
    Args:
        property_id: Property ID to view (e.g., "32926983")
        buyer_client_id: Buyer's client ID (e.g., "C0001")
        datetime_iso: Viewing datetime in ISO format (e.g., "2025-11-20T14:00:00Z")
        notes: Optional notes about the viewing
    
    Returns:
        Confirmation with viewing_id and updated records
    """
    # Validate buyer exists
    buyer = get_client_by_id(buyer_client_id)
    if not buyer:
        return {"error": f"Buyer {buyer_client_id} not found"}
    
    if buyer.get("role") != "buyer":
        return {"error": f"Client {buyer_client_id} is not a buyer"}
    
    # Find property
    all_listings = get_listings_data()
    property_listing = None
    for listing in all_listings:
        if listing.get("property_id") == property_id:
            property_listing = listing
            break
    
    if not property_listing:
        return {"error": f"Property {property_id} not found"}
    
    # Check if property is sold
    status = property_listing.get("status", "").lower()
    if "sold" in status:
        return {"error": f"Cannot schedule viewing - property {property_id} is already sold"}
    
    # Find seller for this property
    seller = None
    all_clients = get_clients_data()
    for client in all_clients:
        if client.get("role") == "seller" and client.get("selling_property_id") == property_id:
            seller = client
            break
    
    # Parse datetime
    try:
        viewing_datetime = datetime.fromisoformat(datetime_iso.replace("Z", "+00:00"))
    except ValueError:
        return {"error": "Invalid datetime format. Use ISO format like '2025-11-20T14:00:00Z'"}
    
    # Check for datetime conflicts on this property
    if seller:
        for viewing in seller.get("viewings", []):
            if viewing.get("property_id") == property_id:
                existing_dt_str = viewing.get("datetime", "")
                try:
                    existing_dt = datetime.fromisoformat(existing_dt_str.replace("Z", "+00:00"))
                    # Check if within 1 hour window
                    time_diff = abs((viewing_datetime - existing_dt).total_seconds())
                    if time_diff < 3600:  # 1 hour = 3600 seconds
                        return {
                            "error": f"Viewing conflict - another viewing scheduled at {existing_dt_str}. Please choose a different time."
                        }
                except ValueError:
                    continue
    
    # Generate viewing ID
    viewing_id = get_next_viewing_id()
    
    # Create viewing record
    viewing_record = {
        "viewing_id": viewing_id,
        "property_id": property_id,
        "datetime": datetime_iso,
        "status": "booked"
    }
    
    if notes:
        viewing_record["notes"] = notes
    
    # Update buyer record
    buyer_viewings = buyer.get("viewings", [])
    buyer_viewings.append(viewing_record)
    update_client(buyer_client_id, {"viewings": buyer_viewings})
    
    # Update seller record (if exists)
    if seller:
        seller_viewings = seller.get("viewings", [])
        seller_viewings.append(viewing_record)
        update_client(seller["client_id"], {"viewings": seller_viewings})
    
    return {
        "message": f"✅ Viewing scheduled successfully!",
        "viewing_id": viewing_id,
        "property_id": property_id,
        "buyer": buyer.get("full_name"),
        "datetime": datetime_iso,
        "status": "booked",
        "structuredContent": {
            "viewing_id": viewing_id,
            "property_id": property_id,
            "buyer_name": buyer.get("full_name"),
            "buyer_contact": buyer.get("contact"),
            "datetime": datetime_iso,
            "status": "booked",
            "notes": notes
        }
    }


def view_leads(
    role: Optional[str] = None,
    stage: Optional[str] = None,
    limit: int = 20
) -> Dict[str, Any]:
    """
    View and filter client leads. Internal tool for estate agents.
    Returns structured client data for review.
    
    Args:
        role: Filter by role - "buyer" or "seller" (optional, shows all if not specified)
        stage: Filter by stage - "hot", "warm", "cold", "instructed", "completed" (optional)
        limit: Maximum number of leads to return (default: 20)
    
    Returns:
        Filtered list of client records
    """
    all_clients = get_clients_data()
    
    # Filter clients
    filtered = []
    for client in all_clients:
        # Apply role filter
        if role and client.get("role") != role:
            continue
        
        # Apply stage filter
        if stage and client.get("stage") != stage:
            continue
        
        filtered.append(client)
    
    # Sort by created_at (newest first)
    filtered.sort(key=lambda x: x.get("created_at", ""), reverse=True)
    
    # Build summary stats
    total_buyers = sum(1 for c in all_clients if c.get("role") == "buyer")
    total_sellers = sum(1 for c in all_clients if c.get("role") == "seller")
    hot_leads = sum(1 for c in all_clients if c.get("stage") == "hot")
    
    return {
        "message": f"Found {len(filtered)} leads matching criteria",
        "leads": filtered[:limit],
        "total_results": len(filtered),
        "showing": min(limit, len(filtered)),
        "summary": {
            "total_buyers": total_buyers,
            "total_sellers": total_sellers,
            "hot_leads": hot_leads,
            "total_clients": len(all_clients)
        },
        "structuredContent": {
            "leads": filtered[:limit],
            "total_results": len(filtered),
            "showing": min(limit, len(filtered)),
            "summary": {
                "total_buyers": total_buyers,
                "total_sellers": total_sellers,
                "hot_leads": hot_leads,
                "total_clients": len(all_clients)
            }
        }
    }