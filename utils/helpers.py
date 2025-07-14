from datetime import datetime
import pyvisa

def current_timestamp():
    return datetime.now().isoformat()

def initialize_visa():
    """Initialize VISA resource manager"""
    global rm
    try:
        rm = pyvisa.ResourceManager()
        return True
    except Exception as e:
        print(f"Failed to initialize VISA: {e}")
        return False