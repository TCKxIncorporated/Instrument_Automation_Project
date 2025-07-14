from fastapi import APIRouter, HTTPException
from models.schema import PowerSupplySettings, OutputControl
from services import instrument, monitor

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
    # Instrument control commands go here
    return {"success": True}

@router.get("/plot-data")
def plot_data():
    return monitor.get_plot_data(device_status["current_channel"])

@router.post("/clear-data")
def clear_plot():
    monitor.clear_data()
    return {"message": "Data cleared"}
