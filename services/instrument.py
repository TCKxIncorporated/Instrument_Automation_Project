# services/instrument.py

import pyvisa
from pyvisa import VisaIOError

# Global VISA resource manager and instrument handle
rm = None
instrument = None

def initialize_visa() -> bool:
    """
    Initialize the PyVISA ResourceManager.
    Pass backend='@py' to use pyvisa‑py instead of NI‑VISA.
    """
    global rm
    try:
        # Pick your backend here:
        rm = pyvisa.ResourceManager()
        return True
    except Exception as e:
        print(f"[VISA ERROR] Failed to initialize VISA: {e}")
        return False

def list_devices() -> list[str]:
    """Return a list of available VISA resource strings."""
    try:
        return rm.list_resources() if rm else []
    except VisaIOError as e:
        print(f"[VISA ERROR] list_resources() failed: {e}")
        return []

def connect_device(address: str) -> str | None:
    """
    Open the instrument at `address`, set timeouts/terminators, and query *IDN?.
    Returns the IDN string if successful, or None on error.
    """
    global instrument
    if not rm:
        print("[VISA ERROR] ResourceManager not initialized")
        return None

    print(f"[VISA] Connecting to device at {address}")
    try:
        # Open the resource and configure timing & terminators
        instrument = rm.open_resource(address)
        instrument.timeout = 10_000           # 10 seconds
        instrument.write_termination = '\n'
        instrument.read_termination  = '\n'

        # Test with an *IDN? query
        idn = instrument.query("*IDN?").strip()
        print(f"[VISA] Connected to: {idn}")
        return idn

    except VisaIOError as e:
        print(f"[VISA ERROR] Could not connect (timeout or IO error): {e}")
        return None
    except Exception as e:
        print(f"[VISA ERROR] Unexpected error connecting to {address}: {e}")
        return None

def disconnect_device() -> bool:
    """Close the current instrument session, if any."""
    global instrument
    try:
        if instrument:
            instrument.close()
            instrument = None
            print("[VISA] Device disconnected")
            return True
        return False
    except VisaIOError as e:
        print(f"[VISA ERROR] Could not disconnect: {e}")
        return False

def set_channel_settings(channel: int,
                         limit: float,
                         voltage: float,
                         current: float) -> tuple[bool, str]:
    """Configure the selected channel’s limit, voltage, and current."""
    global instrument
    if instrument is None:
        return False, "Instrument not connected"

    try:
        instrument.write(f"INST:NSEL {channel}")
        instrument.write(f"VOLT:LIMIT {limit}")
        instrument.write(f"VOLT {voltage}")
        instrument.write(f"CURR {current}")
        msg = f"Channel {channel} set to {voltage} V, {current} A (limit {limit} V)"
        print(f"[VISA] {msg}")
        return True, msg

    except VisaIOError as e:
        print(f"[VISA ERROR] set_channel_settings failed: {e}")
        return False, str(e)
    except Exception as e:
        print(f"[VISA ERROR] Unexpected error: {e}")
        return False, str(e)


if __name__ == "__main__":
    # Quick standalone check
    if initialize_visa():
        devs = list_devices()
        print("Resources found:", devs)
        if devs:
            resp = connect_device(devs[0])
            print("IDN response:", resp)
            disconnect_device()
    else:
        print("Failed to initialize VISA backend.")
