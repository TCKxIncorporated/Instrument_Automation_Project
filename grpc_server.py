import grpc
from concurrent import futures
import threading
import time

import instrument_pb2
import instrument_pb2_grpc
from instrument_pb2 import DeviceListResponse, ConnectionResponse, Empty

from services.instrument import (
    initialize_visa,
    list_devices,
    connect_device,
    disconnect_device,
    set_channel_settings
)
from services import instrument as inst_module
from services import monitor
from api import routes
from datetime import datetime

# Global lock to serialize all VISA resource access
environment_lock = threading.Lock()

class InstrumentServiceServicer(instrument_pb2_grpc.InstrumentServiceServicer):

    def InitializeVISA(self, request, context):
        try:
            success = initialize_visa()
            message = "VISA initialized" if success else "Failed to initialize VISA"
            return ConnectionResponse(success=success, message=message)
        except Exception as e:
            return ConnectionResponse(success=False, message=str(e))

    def GetStatus(self, request, context):
        status = routes.get_status()
        return instrument_pb2.StatusResponse(status=str(status))

    def SetChannel(self, request, context):
        try:
            with environment_lock:
                ok, msg = set_channel_settings(
                    channel=request.channel,
                    limit=request.voltage_limit,
                    voltage=request.voltage,
                    current=request.current
                )
            return instrument_pb2.ChannelResponse(success=ok, message=msg)
        except Exception as e:
            return instrument_pb2.ChannelResponse(success=False, message=str(e))

    def ListDevices(self, request, context):
        try:
            with environment_lock:
                devices = list_devices()
            return DeviceListResponse(devices=devices)
        except Exception as e:
            return DeviceListResponse(devices=[f"[Error] {e}"])

    def ConnectDevice(self, request, context):
        try:
            with environment_lock:
                idn = connect_device(request.address)
            success = bool(idn)
            return ConnectionResponse(success=success, message=idn or "Failed to connect")
        except Exception as e:
            return ConnectionResponse(success=False, message=str(e))

    def DisconnectDevice(self, request, context):
        try:
            with environment_lock:
                success = disconnect_device()
            return ConnectionResponse(success=success, message="Disconnected" if success else "No device connected")
        except Exception as e:
            return ConnectionResponse(success=False, message=str(e))

    def SetOutput(self, request, context):
        try:
            with environment_lock:
                monitor.current_channel = request.channel
                instr = inst_module.instrument
                instr.write(f"INST:NSEL {request.channel}")
                instr.write(f"OUTP {'ON' if request.state else 'OFF'}")
                if not request.state:
                    monitor.stop_monitoring()
                else:
                    monitor.start_monitoring(instr, request.channel, True)
            return instrument_pb2.OutputResponse(success=True, message="Output updated")
        except Exception as e:
            return instrument_pb2.OutputResponse(success=False, message=str(e))

    def StartMonitoring(self, request, context):
        try:
            with environment_lock:
                monitor.start_monitoring(inst_module.instrument, request.channel, True)
            # let the background thread spin up
            time.sleep(1)
            return Empty()
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return Empty()
        
    # in your InstrumentServiceServicer

    def MonitorVoltage(self, request, context):
        try:
            rd = monitor.get_latest_reading(request.channel)
        except ValueError:
            # no samples yet: return a default "zero" reading
            return instrument_pb2.VoltageReading(
                timestamp=datetime.now(),
                voltage=0.0,
                channel=request.channel,
            )

        return instrument_pb2.VoltageReading(
            timestamp=rd["time"],
            voltage=rd["voltage"],
            channel=rd["channel"],
        )

    
    def ClearData(self, request, context):
        try:
            with environment_lock:
                monitor.clear_data()
            return Empty()
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return Empty()

    def StopMonitoring(self, request, context):
        try:
            with environment_lock:
                monitor.stop_monitoring()
            return Empty()
        except Exception as e:
            context.set_details(str(e))
            context.set_code(grpc.StatusCode.INTERNAL)
            return Empty()

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    instrument_pb2_grpc.add_InstrumentServiceServicer_to_server(
        InstrumentServiceServicer(), server
    )
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == '__main__':
    serve()
