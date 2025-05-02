import os
import json
from datetime import datetime

def get_session_file_path():
    """Get the path to the session token file in the Documents/Ressync/session directory."""
    home_dir = os.path.expanduser("~")
    session_dir = os.path.join(home_dir, "Documents", "Ressync", "session")
    os.makedirs(session_dir, exist_ok=True)
    return os.path.join(session_dir, "session_token.json")

def store_session_token(token_data):
    """Store session token data in the session file."""
    session_file = get_session_file_path()
    with open(session_file, 'w') as f:
        json.dump(token_data, f)

def get_session_token():
    """Retrieve the stored session token data."""
    session_file = get_session_file_path()
    if not os.path.exists(session_file):
        return None
    
    try:
        with open(session_file, 'r') as f:
            data = json.load(f)
            
        # Check if token is expired
        expiry_str = data.get('expiry')
        if expiry_str and datetime.fromisoformat(expiry_str) < datetime.utcnow():
            return None
            
        return data
    except (json.JSONDecodeError, FileNotFoundError):
        return None

def clear_session_token():
    """Clear the stored session token by deleting the file."""
    session_file = get_session_file_path()
    try:
        if os.path.exists(session_file):
            os.remove(session_file)
    except OSError:
        pass