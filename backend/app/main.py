from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from app.api.analytics import router as analytics_router
from app.api.buses import router as buses_router
from app.api.events import router as events_router
from app.api.simulator import router as simulator_router
from app.api.summary import router as summary_router
from app.api.system import router as system_router
from app.config import settings
from app.db.database import Base, engine
from app.db.models import Bus, Event
from app.services.ws_manager import manager
from app.sim.simulator import FleetSimulator

@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    app.state.simulator = FleetSimulator()
    yield
    await app.state.simulator.stop()

app = FastAPI(title=settings.app_name, version="1.0.0", lifespan=lifespan)
app.add_middleware(CORSMiddleware, allow_origins=settings.cors_origin_list, allow_credentials=True, allow_methods=["*"], allow_headers=["*"])
app.include_router(events_router); app.include_router(buses_router); app.include_router(analytics_router); app.include_router(summary_router); app.include_router(simulator_router); app.include_router(system_router)

from fastapi.staticfiles import StaticFiles
from pathlib import Path

Path(settings.evidence_dir).mkdir(parents=True, exist_ok=True)
app.mount("/evidence", StaticFiles(directory=settings.evidence_dir), name="evidence")

@app.get("/")
def root():
    return {"name": settings.app_name, "status": "running", "docs": "/docs"}

@app.websocket("/ws/events")
async def websocket_events(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()
    except Exception:
        manager.disconnect(websocket)
