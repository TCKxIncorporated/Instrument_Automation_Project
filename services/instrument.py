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

def set_channel_settings(channel, voltage, current):
    """
    Set the voltage and current for a specific channel on the instrument.
    Returns (success: bool, message: str)
    """
    try:
        # Example logic: Replace with actual instrument control code
        # instrument.write(f"INST:NSEL {channel}")
        # instrument.write(f"VOLT {voltage}")
        # instrument.write(f"CURR {current}")
        print(f"Setting channel {channel}: {voltage}V, {current}A")
        return True, f"Channel {channel} set to {voltage}V, {current}A"
    except Exception as e:
        return
