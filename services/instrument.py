import pyvisa

rm = None
instrument = None

def initialize_visa():
    global rm
    try:
        rm = pyvisa.ResourceManager()
        return True
    except Exception as e:
        print(f"[VISA ERROR] {e}")
        return False

def list_devices():
    return rm.list_resources() if rm else []

def connect_device(address):
    global instrument
    instrument = rm.open_resource(address)
    return instrument.query("*IDN?").strip()

def disconnect_device():
    global instrument
    if instrument:
        instrument.close()
        instrument = None
