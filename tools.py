from typing import List, Dict, Any, Optional
from data_loader import get_listings_data # Import our data loader

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