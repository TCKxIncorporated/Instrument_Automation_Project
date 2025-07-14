import grpc
from concurrent import futures
from api.routes import get_status, set_settings  # You should implement these functions in your services
import instrument_pb2
import instrument_pb2_grpc

class InstrumentServiceServicer(instrument_pb2_grpc.InstrumentServiceServicer):
    def GetStatus(self, request, context):
        # Call your actual status logic
        status = get_status()  # Should return a string or dict with status info
        return instrument_pb2.StatusResponse(status=str(status))

    def SetChannel(self, request, context):
        # Call your actual channel setting logic
        try:
            result = set_settings(
                channel=request.channel,
                voltage=request.voltage,
                current=request.current
            )  # Should return (success: bool, message: str)
            return instrument_pb2.ChannelResponse(success=result[0], message=result[1])
        except Exception as e:
            return instrument_pb2.ChannelResponse(success=False, message=str(e))

def serve():
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
    instrument_pb2_grpc.add_InstrumentServiceServicer_to_server(InstrumentServiceServicer(), server)
    server.add_insecure_port('[::]:50051')
    server.start()
    print("gRPC server started on port 50051")
    server.wait_for_termination()

if __name__ == "__main__":
    serve()