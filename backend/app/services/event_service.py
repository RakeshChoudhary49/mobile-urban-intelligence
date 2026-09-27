from sqlalchemy.orm import Session
from app.db.models import Event
from app.schemas import EventCreate
from app.services.ws_manager import manager

async def create_event(db: Session, payload: EventCreate):
    event = Event(**payload.model_dump())
    db.add(event)
    db.commit()
    db.refresh(event)
    await manager.broadcast({"type": "event", "event": serialize_event(event)})
    return event

def serialize_event(event: Event):
    return {
        "id": event.id,
        "bus_code": event.bus_code,
        "event_type": event.event_type,
        "severity": event.severity,
        "confidence": event.confidence,
        "latitude": event.latitude,
        "longitude": event.longitude,
        "speed_kmph": event.speed_kmph,
        "plate_number": event.plate_number,
        "plate_confidence": event.plate_confidence,
        "message": event.message,
        "evidence_path": event.evidence_path,
        "source_camera": event.source_camera,
        "acknowledged": event.acknowledged,
        "timestamp": event.timestamp.isoformat(),
    }
