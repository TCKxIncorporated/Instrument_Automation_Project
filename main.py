from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from api.routes import router as api_router
from services.monitor import start_monitoring, stop_monitoring
from services.instrument import initialize_visa
from grpc_client import get_status, set_channel  # Import client functions
import grpc
import instrument_pb2_grpc
import instrument_pb2

app = FastAPI(
    title="Keithley 2230G Remote Controller",
    description="Remote control API for Keithley 2230G Power Supply",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def on_startup():
    initialize_visa()

    # Run gRPC client logic
    try:
        with grpc.insecure_channel('172.20.10.5:50051') as channel:
            stub = instrument_pb2_grpc.InstrumentServiceStub(channel)
            get_status(stub)
            
    except Exception as e:
        print("gRPC client failed:", e)

@app.on_event("shutdown")
async def on_shutdown():
    stop_monitoring()

@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", "r") as file:
        return file.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)
