import grpc
import instrument_pb2
import instrument_pb2_grpc
from instrument_pb2 import DeviceRequest, Empty

GRPC_ADDRESS = '172.20.10.5:50051'

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

def main():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel)
        get_status(stub)
        set_channel(stub, channel=1, voltage=5.0, current=1.0)

if __name__ == "__main__":
    main()
