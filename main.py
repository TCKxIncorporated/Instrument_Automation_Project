from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from api.routes import router as api_router
from services.monitor import start_monitoring, stop_monitoring
from services.instrument import initialize_visa

app = FastAPI(
    title="Keithley 2230G Remote Controller",
    description="Remote control API for Keithley 2230G Power Supply",
    version="1.0.0"
)

app.include_router(api_router, prefix="/api")

@app.on_event("startup")
async def on_startup():
    initialize_visa()

@app.on_event("shutdown")
async def on_shutdown():
    stop_monitoring()

# Optional root
@app.get("/", response_class=HTMLResponse)
def root():
    with open("static/index.html", "r") as file:
        return file.read()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000)