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
) -> List[Dict[str, Any]]:
    """
    Searches and filters property listings based on specific criteria.
    Returns a list of matching listings, limited to 5 by default.

    Args:
        postcode: The postcode to filter by (e.g., "DY4 7LG").
        property_type: The type of property (e.g., "Flat", "Apartment - First Floor").
        max_price: The maximum price (e.g., 100000).
        min_bedrooms: The minimum number of bedrooms (e.g., 1).
        has_garden: Must have a garden.
        has_parking: Must have parking.
        limit: The maximum number of listings to return. Defaults to 5.
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
        if postcode is not None and listing.get('postcode') != postcode:
            continue
        if property_type is not None and property_type.lower() not in listing.get('property_type', '').lower():
            continue
            
        # If all checks passed, add it to the list
        filtered_results.append(listing)
    
    # Always return a limited number of results!
    # This saves tokens and keeps the AI response focused.
    return filtered_results[:limit]


def calculate_average_price(
    postcode: Optional[str] = None,
    property_type: Optional[str] = None
) -> Dict[str, Any]:
    """
    Calculates the average price for listings that match the given criteria.
    You must provide at least one filter (e.g., postcode or property_type).

    Args:
        postcode: The postcode to calculate for (e.g., "DY4 7LG").
        property_type: The type of property (e.g., "Flat").
    """
    all_listings = get_listings_data()
    
    total_price = 0
    count = 0

    for listing in all_listings:
        # Check if the listing matches our filters
        if postcode is not None and listing.get('postcode') != postcode:
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