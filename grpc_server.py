import grpc
from concurrent import futures
from services.instrument import set_channel_settings
import instrument_pb2
import instrument_pb2_grpc
from api import routes

from instrument_pb2 import DeviceListResponse, DeviceRequest, ConnectionResponse, Empty
from services.instrument import list_devices, connect_device, disconnect_device, initialize_visa
import services.instrument as instr_module
from services import monitor


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
        status = routes.get_status()  # Should return a string or dict with status info
        return instrument_pb2.StatusResponse(status=str(status))

    def SetChannel(self, request, context):
        # Call your actual channel setting logic
        try:
            result = set_channel_settings(
                channel=request.channel,
                limit=request.voltage_limit,
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
            print(f"[gRPC] Connecting to {request.address}")
            idn = connect_device(request.address)
            print(f"[gRPC] Connected: {idn}, inst: {instr_module.instrument}")
            return ConnectionResponse(success=bool(idn), message=idn or "Failed to connect")
        except Exception as e:
            return ConnectionResponse(success=False, message=str(e))

    def DisconnectDevice(self, request, context):
        try:
            success = disconnect_device()
            return ConnectionResponse(success=success, message="Disconnected" if success else "No device connected")
        except Exception as e:
            return ConnectionResponse(success=False, message=str(e))
        
    def SetOutput(self, request, context):

        if instr_module.instrument is None:
            return instrument_pb2.OutputResponse(success=False, message="Instrument not connected")

        try:
            channel = request.channel
            state = request.state

            instr_module.instrument.write(f"INST:NSEL {channel}")
            instr_module.instrument.write(f"OUTP {'ON' if state else 'OFF'}")

            if instr_module.instrument.query("OUTP?") == {'OFF'}:
                monitor.stop_monitoring()
            else:
                monitor.start_monitoring(instr_module.instrument, channel, True)

            return instrument_pb2.OutputResponse(success=True, message="Output updated")

        except Exception as e:
            return instrument_pb2.OutputResponse(success=False, message=str(e))
        
    def StartMonitoring(self, request, context):
        monitor.start_monitoring(instr_module.instrument, request.channel, True)
        return instrument_pb2.Empty()
        
    def MonitorVoltage(self, request, context):
        reading = monitor.get_plot_data(request.channel)
        return instrument_pb2.VoltageReading(
            timestamp=reading["time"],
            voltage=reading["voltage"],
            channel=reading["channel"]
        )

    def ClearData(self, request, context):
        monitor.clear_data()
        return instrument_pb2.Empty()


def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    instrument_pb2_grpc.add_InstrumentServiceServicer_to_server(InstrumentServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()