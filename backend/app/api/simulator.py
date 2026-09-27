from fastapi import APIRouter, Request, HTTPException
from pydantic import BaseModel
from app.schemas import EventOut

router = APIRouter(prefix="/api/simulator", tags=["simulator"])

class TriggerIncidentRequest(BaseModel):
    incident_type: str = "hit_and_run"
    bus_code: str | None = "BUS-101"

@router.post("/start")
async def start_simulator(request: Request):
    sim = request.app.state.simulator
    if sim.running:
        return {"running": True, "message": "Simulator already running"}
    await sim.start()
    return {"running": True, "message": "Simulator started"}

@router.post("/stop")
async def stop_simulator(request: Request):
    sim = request.app.state.simulator
    await sim.stop()
    return {"running": False, "message": "Simulator stopped"}

@router.get("/status")
def simulator_status(request: Request):
    sim = getattr(request.app.state, "simulator", None)
    return {"running": sim.running if sim else False}

@router.post("/trigger-incident", response_model=EventOut)
async def trigger_incident(payload: TriggerIncidentRequest, request: Request):
    sim = getattr(request.app.state, "simulator", None)
    if not sim:
        raise HTTPException(status_code=500, detail="Simulator service not initialized")
    
    event = await sim.trigger_incident(
        incident_type=payload.incident_type,
        bus_code=payload.bus_code
    )
    return event
