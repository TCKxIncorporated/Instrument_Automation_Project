from fastapi import APIRouter, HTTPException
from models.schema import PowerSupplySettings, OutputControl
#from services import instrument, monitor
from utils.helpers import current_timestamp
import grpc_client as instrument
from services import monitor

router = APIRouter()

device_status = {
    "connected": False,
    "device_info": None,
    "last_settings": {},
    "output_state": False,
    "timestamp": "",
    "current_channel": 1
}

@router.get("/devices")
def get_devices():
    return instrument.list_devices()

@router.post("/connect")
def connect(request: dict):
    address = request.get("device_address")
    if not address:
        raise HTTPException(400, "Missing address")

    idn = instrument.connect_device(address)
    device_status.update({"connected": True, "device_info": idn})
    monitor.start_monitoring(instrument.instrument, 1, True)
    return {"device_info": idn}


@router.post("/settings")
def set_settings(settings: PowerSupplySettings):
    from services.instrument import instrument  # import the global instrument instance

    if not instrument:
        raise HTTPException(status_code=400, detail="No device connected")

    if settings.voltage_set > settings.voltage_limit:
        raise HTTPException(status_code=400, detail="Set voltage cannot exceed voltage limit")

    try:
        # Select the channel
        instrument.write(f"INST:NSEL {settings.channel}")

        # Apply settings
        instrument.write(f"SOUR:VOLT:LIM {settings.voltage_limit}")
        instrument.write("SOUR:VOLT:LIM:STAT ON")
        instrument.write(f"SOUR:VOLT {settings.voltage_set}")
        instrument.write(f"SOUR:CURR {settings.current}")

        # Optionally update global status object
        device_status["last_settings"] = settings.dict()
        device_status["current_channel"] = settings.channel

        return {"success": True, "message": f"Settings applied to channel {settings.channel}"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to apply settings: {str(e)}")


@router.get("/plot-data")
def plot_data():
    return monitor.get_plot_data(device_status["current_channel"])

@router.post("/clear-data")
def clear_plot():
    monitor.clear_data()
    return {"message": "Data cleared"}

@router.get("/status")
def get_status():
    """Return the current device status"""
    device_status["timestamp"] = current_timestamp()
    return device_status

@router.post("/output")
def control_output(control: OutputControl):
    from services.instrument import instrument  # shared instrument instance

    if not instrument:
        raise HTTPException(status_code=400, detail="No device connected")

    try:
        for channel in [1, 2, 3]:
            instrument.write(f"INST:NSEL {channel}")
            instrument.write(f"OUTP {'ON' if control.state else 'OFF'}")

        device_status["output_state"] = control.state
        device_status["timestamp"] = current_timestamp()

        return {
            "success": True,
            "message": f"All channels output {'ON' if control.state else 'OFF'}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to control output: {str(e)}")
