from fastapi import APIRouter, Depends, HTTPException, Query, File, UploadFile, Form
import re
from pathlib import Path
from datetime import datetime
from app.config import settings
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Event
from app.schemas import EventCreate, EventOut
from app.services.event_service import create_event

router = APIRouter(prefix="/api/events", tags=["events"])

INCIDENT_TYPES = ["hit_and_run", "rash_driving", "pedestrian_risk"]
HAZARD_TYPES = ["pothole", "waterlogging", "missing_sign", "missing_zebra", "missing_divider"]

@router.get("", response_model=list[EventOut])
def list_events(
    limit: int = Query(100, ge=1, le=500),
    severity: str | None = None,
    event_type: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db)
):
    query = select(Event).order_by(Event.timestamp.desc()).limit(limit)
    if severity:
        query = query.where(Event.severity == severity)
    if event_type:
        query = query.where(Event.event_type == event_type)
    if category == "incidents":
        query = query.where(Event.event_type.in_(INCIDENT_TYPES))
    elif category == "hazards":
        query = query.where(Event.event_type.in_(HAZARD_TYPES))
    elif category == "traffic":
        query = query.where(Event.event_type == "traffic_bottleneck")
    return db.scalars(query).all()

@router.post("", response_model=EventOut)
async def create_event_endpoint(payload: EventCreate, db: Session = Depends(get_db)):
    return await create_event(db, payload)

@router.patch("/{event_id}/acknowledge", response_model=EventOut)
def acknowledge_event(event_id: int, db: Session = Depends(get_db)):
    event = db.get(Event, event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Event not found")
    event.acknowledged = True
    db.commit()
    db.refresh(event)
    return event

@router.post("/with-evidence", response_model=EventOut)
async def create_event_with_evidence(
    bus_code: str = Form(...),
    event_type: str = Form(...),
    severity: str = Form("medium"),
    confidence: float = Form(0.0),
    latitude: float = Form(...),
    longitude: float = Form(...),
    speed_kmph: float = Form(0.0),
    plate_number: str | None = Form(None),
    plate_confidence: float | None = Form(None),
    message: str = Form(""),
    source_camera: str = Form("front"),
    evidence: UploadFile | None = File(None),
    db: Session = Depends(get_db),
):
    safe_bus_code = re.sub(r'[^A-Za-z0-9_-]', '', bus_code) or "BUS-101"
    safe_event_type = re.sub(r'[^A-Za-z0-9_-]', '', event_type) or "event"

    evidence_path = None
    if evidence:
        base_dir = Path(settings.evidence_dir).resolve()
        bus_dir = (base_dir / safe_bus_code).resolve()
        
        # Enforce containment within evidence dir
        if not str(bus_dir).startswith(str(base_dir)):
            raise HTTPException(status_code=400, detail="Invalid bus identifier")

        bus_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{datetime.utcnow():%Y%m%d_%H%M%S}_{safe_event_type}.jpg"
        dest = bus_dir / filename
        
        with open(dest, "wb") as f:
            while chunk := evidence.file.read(65536):
                f.write(chunk)
        evidence_path = f"{safe_bus_code}/{filename}"

    payload = EventCreate(
        bus_code=safe_bus_code,
        event_type=safe_event_type,
        severity=severity,
        confidence=confidence,
        latitude=latitude,
        longitude=longitude,
        speed_kmph=speed_kmph,
        plate_number=plate_number,
        plate_confidence=plate_confidence,
        message=message,
        evidence_path=evidence_path,
        source_camera=source_camera
    )
    return await create_event(db, payload)
