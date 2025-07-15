import grpc
import instrument_pb2
import instrument_pb2_grpc
from instrument_pb2 import DeviceRequest, Empty
import grpc
from instrument_pb2 import Empty, DeviceRequest
from instrument_pb2_grpc import InstrumentServiceStub

GRPC_ADDRESS = '172.20.10.5:50051'

def initialize_visa():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = InstrumentServiceStub(channel)
        response = stub.InitializeVISA(Empty())
        print(f"InitializeVISA: success={response.success}, message={response.message}")
        return response.success

def list_devices():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = InstrumentServiceStub(channel)
        response = stub.ListDevices(Empty())
        print("Devices:", response.devices)
        return response.devices
    
def get_status(stub):
    request = instrument_pb2.StatusRequest()
    response = stub.GetStatus(request)
    print(f"Status: {response.status}")

def set_channel(stub, channel, voltage, current):
    request = instrument_pb2.ChannelRequest(
        channel=channel,
        voltage=voltage,
        current=current
    )
    response = stub.SetChannel(request)
    print(f"SetChannel success: {response.success}, message: {response.message}")

def list_remote_devices():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel)
        response = stub.ListDevices(Empty())
        return response.devices

def connect_remote_device(address):
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel)
        response = stub.ConnectDevice(DeviceRequest(address=address))
        return response.success, response.message

def disconnect_remote_device():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel)
        response = stub.DisconnectDevice(Empty())
        return response.success, response.message

async def main():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel)
        

if __name__ == "__main__":
    main()
