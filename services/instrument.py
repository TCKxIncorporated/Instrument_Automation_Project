import grpc
from instrument_pb2 import (
    StatusRequest,
    ChannelRequest,
    DeviceRequest,
    Empty,
)
from instrument_pb2_grpc import InstrumentServiceStub

GRPC_ADDRESS = "172.20.10.5:50051"

def get_status():
    try:
        with grpc.insecure_channel(GRPC_ADDRESS) as channel:
            stub = InstrumentServiceStub(channel)
            response = stub.GetStatus(StatusRequest())
            return response.status
    except Exception as e:
        return f"[gRPC ERROR] {e}"

def set_channel_settings(channel, voltage, current):
    """
    Sends gRPC request to set voltage and current remotely.
    Returns (success: bool, message: str)
    """
    try:
        with grpc.insecure_channel(GRPC_ADDRESS) as channel:
            stub = InstrumentServiceStub(channel)
            request = ChannelRequest(
                channel=channel,
                voltage=voltage,
                current=current
            )
            response = stub.SetChannel(request)
            return response.success, response.message
    except Exception as e:
        return False, f"[gRPC ERROR] {e}"

def list_devices():
    try:
        with grpc.insecure_channel(GRPC_ADDRESS) as channel:
            stub = InstrumentServiceStub(channel)
            response = stub.ListDevices(Empty())
            return response.devices
    except Exception as e:
        return [f"[gRPC ERROR] {e}"]

def connect_device(address):
    try:
        with grpc.insecure_channel(GRPC_ADDRESS) as channel:
            stub = InstrumentServiceStub(channel)
            request = DeviceRequest(address=address)
            response = stub.ConnectDevice(request)
            return response.success, response.message
    except Exception as e:
        return False, f"[gRPC ERROR] {e}"

def disconnect_device():
    try:
        with grpc.insecure_channel(GRPC_ADDRESS) as channel:
            stub = InstrumentServiceStub(channel)
            response = stub.DisconnectDevice(Empty())
            return response.success, response.message
    except Exception as e:
        return False, f"[gRPC ERROR] {e}"
