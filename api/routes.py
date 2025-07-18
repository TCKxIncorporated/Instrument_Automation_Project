from fastapi import APIRouter, HTTPException
from models.schema import PowerSupplySettings, OutputControl
#from services import instrument, monitor
from utils.helpers import current_timestamp
import grpc_client as instrument
from services.instrument import instrument  as inst
from services import monitor
from pydantic import BaseModel
from typing import List
from pydantic import BaseModel

class ChannelInput(BaseModel):
    channel: int

router = APIRouter()

device_status = {
    "connected": False,
    "device_info": None,
    "last_settings": {},
    "output_state": False,
    "timestamp": "",
    "current_channel": 1
}

class DeviceListResponse(BaseModel):
    devices: List[str]

@router.post("/api/set-channel")
def set_channel(payload: ChannelInput):
    device_status["current_channel"] = payload.channel
    return {"message": f"Channel set to {payload.channel}"}


@router.get("/devices", response_model=DeviceListResponse)
def get_devices():
    return DeviceListResponse(devices=instrument.list_devices())

@router.post("/connect")
def connect(request: dict):
    address = request.get("device_address")
    if not address:
        raise HTTPException(400, "Missing address")

    idn = instrument.connect_remote_device(address)
    device_status.update({"connected": True, "device_info": idn})
    instrument.start_monitoring(1)
    return {"device_info": idn}


@router.post("/settings")
def set_settings(settings: PowerSupplySettings):
    success, message = instrument.set_channel_settings(
        channel=settings.channel,
        limit=settings.voltage_limit,
        voltage=settings.voltage_set,
        current=settings.current
    )

    if not success:
        raise HTTPException(status_code=500, detail=message)

    device_status["last_settings"] = settings.dict()
    device_status["current_channel"] = settings.channel

    return {"success": True, "message": message}

@router.get("/plot-data")
def plot_data():
    ch = device_status["current_channel"]
    print(f"[DEBUG] current_channel = {ch}, type = {type(ch)}")
    return instrument.get_plot_data(int(ch))  # force cast to int to be safe

@router.post("/clear-data")
def clear_plot():
    instrument.clear_data()
    return {"message": "Data cleared"}

@router.get("/status")
def get_status():
    """Return the current device status"""
    device_status["timestamp"] = current_timestamp()
    return device_status

@router.post("/output")
def control_output(control: OutputControl):
    print(f"Received control: {control}")
    if not device_status["connected"]:
        raise HTTPException(status_code=400, detail="No device connected")

    try:
        for channel in [1, 2, 3]:
            success, message = instrument.set_output(channel, control.state)
            if not success:
                raise HTTPException(status_code=500, detail=f"Channel {channel} failed: {message}")


        device_status["output_state"] = control.state
        device_status["timestamp"] = current_timestamp()

        return {
            "success": True,
            "message": f"All channels output {'ON' if control.state else 'OFF'}"
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to control output: {str(e)}")
