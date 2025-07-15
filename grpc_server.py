import grpc
from concurrent import futures
from services.instrument import get_status, set_channel_settings
import instrument_pb2
import instrument_pb2_grpc

from instrument_pb2 import DeviceListResponse, DeviceRequest, ConnectionResponse, Empty
from services.instrument import list_devices, connect_device, disconnect_device, initialize_visa

class InstrumentServiceServicer(instrument_pb2_grpc.InstrumentServiceServicer):

    def InitializeVISA(self, request, context):
        try:
            success = initialize_visa()
            message = "VISA initialized" if success else "Failed to initialize VISA"
            return ConnectionResponse(success=success, message=message)
        except Exception as e:
            return ConnectionResponse(success=False, message=str(e))

    def GetStatus(self, request, context):
        # Call your actual status logic
        status = get_status()  # Should return a string or dict with status info
        return instrument_pb2.StatusResponse(status=str(status))

    def SetChannel(self, request, context):
        # Call your actual channel setting logic
        try:
            result = set_channel_settings(
                channel=request.channel,
                voltage=request.voltage,
                current=request.current
            )  # Should return (success: bool, message: str)
            return instrument_pb2.ChannelResponse(success=result[0], message=result[1])
        except Exception as e:
            return instrument_pb2.ChannelResponse(success=False, message=str(e))
        
    def ListDevices(self, request, context):
        try:
            devices = list_devices()
            return DeviceListResponse(devices=devices)
        except Exception as e:
            return DeviceListResponse(devices=[f"[Error] {e}"])

    def ConnectDevice(self, request, context):
        try:
            idn = connect_device(request.address)
            return ConnectionResponse(success=bool(idn), message=idn or "Failed to connect")
        except Exception as e:
            return ConnectionResponse(success=False, message=str(e))

    def DisconnectDevice(self, request, context):
        try:
            success = disconnect_device()
            return ConnectionResponse(success=success, message="Disconnected" if success else "No device connected")
        except Exception as e:
            return ConnectionResponse(success=False, message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    instrument_pb2_grpc.add_InstrumentServiceServicer_to_server(InstrumentServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()