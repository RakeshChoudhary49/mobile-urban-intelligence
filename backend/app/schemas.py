from datetime import datetime
from pydantic import BaseModel, ConfigDict

class BusOut(BaseModel):
    id: int
    bus_code: str
    route_name: str
    driver_name: str
    status: str
    latitude: float
    longitude: float
    speed_kmph: float
    updated_at: datetime
    model_config = ConfigDict(from_attributes=True)

class EventCreate(BaseModel):
    bus_code: str
    event_type: str
    severity: str = "medium"
    confidence: float = 0.0
    latitude: float
    longitude: float
    speed_kmph: float = 0.0
    plate_number: str | None = None
    plate_confidence: float | None = None
    message: str = ""
    evidence_path: str | None = None
    source_camera: str = "front"

class EventOut(EventCreate):
    id: int
    acknowledged: bool
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)
