import json
from typing import List, Dict, Any

# We assume your data file is in a 'data' subfolder.
# You can change this path if it's somewhere else.
DATA_FILE = "data/listings.jsonl"

def load_data() -> List[Dict[str, Any]]:
    """
    Loads all listings from the JSONL file into a list in memory.
    """
    data = []
    print(f"Attempting to load data from {DATA_FILE}...")
    try:
        with open(DATA_FILE, 'r') as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Warning: Skipping a line that wasn't valid JSON: {line}")
        print(f"Successfully loaded {len(data)} listings.")
    except FileNotFoundError:
        print(f"Error: Data file not found at {DATA_FILE}.")
        print("Please create a 'data' folder and put 'listings.jsonl' inside it.")
        # We'll return an empty list so the server doesn't crash
    
    return data

# --- This is the important part ---
# We load the data ONCE when the server starts.
# This makes all future queries super fast instead of reading the file every time.
listings_data = load_data()

def get_listings_data() -> List[Dict[str, Any]]:
    """A simple 'getter' function to safely access the loaded data from other files."""
    return listings_data