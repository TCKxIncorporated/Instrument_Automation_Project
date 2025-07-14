from datetime import datetime
import pyvisa

def current_timestamp():
    return datetime.now().isoformat()
