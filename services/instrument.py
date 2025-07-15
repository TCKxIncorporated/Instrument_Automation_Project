import pyvisa

rm = None
instrument = None

def initialize_visa():
    global rm
    try:
        rm = pyvisa.ResourceManager()
        print("[VISA] Resource Manager initialized")
        return True
    except Exception as e:
        print(f"[VISA ERROR] {e}")
        return False

def list_devices():
    try:
        return rm.list_resources() if rm else []
    except Exception as e:
        print(f"[VISA ERROR] {e}")
        return []

def connect_device(address):
    global instrument
    try:
        instrument = rm.open_resource(address)
        idn = instrument.query("*IDN?").strip()
        print(f"[VISA] Connected to: {idn}")
        return idn
    except Exception as e:
        print(f"[VISA ERROR] Could not connect: {e}")
        return None

def disconnect_device():
    global instrument
    try:
        if instrument:
            instrument.close()
            instrument = None
            print("[VISA] Device disconnected")
            return True
        return False
    except Exception as e:
        print(f"[VISA ERROR] Could not disconnect: {e}")
        return False

def set_channel_settings(channel, voltage, current):
    """
    Set the voltage and current for a specific channel on the instrument.
    This is for local VISA-based control (on the gRPC server).
    Returns (success: bool, message: str)
    """
    try:
        if instrument is None:
            return False, "Instrument not connected"
        
        instrument.write(f"INST:NSEL {channel}")
        instrument.write(f"VOLT {voltage}")
        instrument.write(f"CURR {current}")
        
        print(f"[VISA] Set channel {channel}: {voltage}V, {current}A")
        return True, f"Channel {channel} set to {voltage}V, {current}A"
    except Exception as e:
        print(f"[VISA ERROR] {e}")
        return False, str(e)
