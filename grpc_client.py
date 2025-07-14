import grpc
import instrument_pb2
import instrument_pb2_grpc

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

def main():
    with grpc.insecure_channel('172.20.10.5:50051') as channel:
        stub = instrument_pb2_grpc.InstrumentServiceStub(channel)
        get_status(stub)
        set_channel(stub, channel=1, voltage=5.0, current=1.0)

if __name__ == "__main__":
    main()