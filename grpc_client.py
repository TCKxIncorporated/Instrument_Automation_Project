import grpc
import instrument_pb2
import instrument_pb2_grpc
from instrument_pb2 import DeviceRequest, Empty
from instrument_pb2_grpc import InstrumentServiceStub
import asyncio

GRPC_ADDRESS = '192.168.216.103:50051'

def initialize_visa():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        print('initialize_visa from grpc_client')
        stub = InstrumentServiceStub(channel)
        response = stub.InitializeVISA(Empty())
        print(f"InitializeVISA: success={response.success}, message={response.message}")
        return response.success

def list_devices():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel:
        print('list_devices from grpc_client')
        stub = InstrumentServiceStub(channel)
        response = stub.ListDevices(Empty())
        print("Devices:", response.devices)
        return response.devices
    
def get_status(stub):
    request = instrument_pb2.StatusRequest()
    response = stub.GetStatus(request)
    print(f"Status: {response.status}")

def set_channel_settings(channel: int, limit: float, voltage: float, current: float):
    with grpc.insecure_channel(GRPC_ADDRESS) as channel_conn:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel_conn)
        request = instrument_pb2.ChannelRequest(
            channel=channel,
            voltage_limit=limit,
            voltage=voltage,
            current=current
        )
        response = stub.SetChannel(request)
        print(f"SetChannel via gRPC: success={response.success}, message={response.message}")
        return response.success, response.message

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
    
def set_output(channel, state):
    import instrument_pb2
    import instrument_pb2_grpc
    from instrument_pb2 import OutputRequest

    with grpc.insecure_channel(GRPC_ADDRESS) as channel_conn:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel_conn)
        request = OutputRequest(channel=channel, state=state)
        response = stub.SetOutput(request)
        return response.success, response.message

def start_monitoring(channel):
    with grpc.insecure_channel(GRPC_ADDRESS) as channel_conn:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel_conn)
        request = instrument_pb2.ReadChannel(channel=channel)
        response = stub.StartMonitoring(request)
        return instrument_pb2.Empty()
    

def get_plot_data(channel: int):
    chan = grpc.insecure_channel(GRPC_ADDRESS)
    stub = instrument_pb2_grpc.InstrumentServiceStub(chan)
    reading = stub.MonitorVoltage(instrument_pb2.ReadChannel(channel=channel))
    return {
        "time":    reading.timestamp,
        "voltage": reading.voltage,
        "channel": reading.channel,
    }

def stop_monitoring():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel_conn:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel_conn)
        request = instrument_pb2.Empty()  # channel is not used in this case
        response = stub.StopMonitoring(request)
        return instrument_pb2.Empty()

def clear_data():
    with grpc.insecure_channel(GRPC_ADDRESS) as channel_conn:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel_conn)
        response = stub.ClearData(Empty())
        return instrument_pb2.Empty()

async def main():
    ok = initialize_visa()
    if not ok:
        return

if __name__ == "__main__":
    asyncio.run(main())   # correct way
