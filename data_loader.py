import json
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

# Data file paths
LISTINGS_FILE = "data/listings.jsonl"
CLIENTS_FILE = "data/clients.jsonl"

def load_jsonl(filepath: str) -> List[Dict[str, Any]]:
    """
    Generic JSONL loader - loads all records from a JSONL file into memory.
    """
    data = []
    print(f"Attempting to load data from {filepath}...")
    try:
        with open(filepath, 'r') as f:
            for line in f:
                try:
                    data.append(json.loads(line))
                except json.JSONDecodeError:
                    print(f"Warning: Skipping invalid JSON line: {line[:50]}...")
        print(f"✅ Successfully loaded {len(data)} records from {filepath}")
    except FileNotFoundError:
        print(f"⚠️  File not found: {filepath}")
        print(f"   Creating empty dataset...")
    
    return data

def save_jsonl(filepath: str, data: List[Dict[str, Any]]) -> bool:
    """
    Save data to JSONL file (overwrites existing file).
    """
    try:
        with open(filepath, 'w') as f:
            for record in data:
                f.write(json.dumps(record) + '\n')
        print(f"✅ Saved {len(data)} records to {filepath}")
        return True
    except Exception as e:
        print(f"❌ Error saving to {filepath}: {e}")
        return False

# --- Load data ONCE when server starts ---
listings_data = load_jsonl(LISTINGS_FILE)
clients_data = load_jsonl(CLIENTS_FILE)

def get_listings_data() -> List[Dict[str, Any]]:
    """Get all property listings."""
    return listings_data

def get_clients_data() -> List[Dict[str, Any]]:
    """Get all client records."""
    return clients_data

def add_client(client: Dict[str, Any]) -> bool:
    """Add a new client record and persist to file."""
    clients_data.append(client)
    return save_jsonl(CLIENTS_FILE, clients_data)

def update_client(client_id: str, updates: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Update an existing client record and persist to file."""
    for i, client in enumerate(clients_data):
        if client.get("client_id") == client_id:
            clients_data[i].update(updates)
            save_jsonl(CLIENTS_FILE, clients_data)
            return clients_data[i]
    return None

def get_client_by_id(client_id: str) -> Optional[Dict[str, Any]]:
    """Find a client by ID."""
    for client in clients_data:
        if client.get("client_id") == client_id:
            return client
    return None

def get_next_client_id() -> str:
    """Generate next client ID (C0001, C0002, etc.)."""
    if not clients_data:
        return "C0001"
    
    # Extract numeric part from existing IDs
    max_num = 0
    for client in clients_data:
        client_id = client.get("client_id", "")
        if client_id.startswith("C"):
            try:
                num = int(client_id[1:])
                max_num = max(max_num, num)
            except ValueError:
                continue
    
    return f"C{max_num + 1:04d}"

def get_next_viewing_id() -> str:
    """Generate next viewing ID (V1001, V1002, etc.)."""
    max_num = 1000
    
    # Check all viewings across all clients
    for client in clients_data:
        for viewing in client.get("viewings", []):
            viewing_id = viewing.get("viewing_id", "")
            if viewing_id.startswith("V"):
                try:
                    num = int(viewing_id[1:])
                    max_num = max(max_num, num)
                except ValueError:
                    continue
    
    return f"V{max_num + 1}"