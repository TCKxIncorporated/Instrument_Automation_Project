from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class PowerSupplySettings(BaseModel):
    channel: int = Field(..., ge=1, le=3)
    voltage_limit: float = Field(..., ge=0, le=30)
    voltage_set: float = Field(..., ge=0, le=30)
    current: float = Field(..., ge=0, le=5)

class OutputControl(BaseModel):
    state: bool

class DeviceStatus(BaseModel):
    connected: bool
    device_info: Optional[str] = None
    last_settings: Optional[Dict[str, Any]] = None
    output_state: bool
    timestamp: str
    current_channel: int

class VoltageReading(BaseModel):
    timestamp: str
    voltage: float
    channel: int
