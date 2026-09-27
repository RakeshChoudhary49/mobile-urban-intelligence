from fastapi import APIRouter, Depends
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Bus, Event

router = APIRouter(prefix="/api/summary", tags=["summary"])

@router.get("")
def summary(db: Session = Depends(get_db)):
    total_events = db.scalar(select(func.count(Event.id))) or 0
    critical_events = db.scalar(select(func.count(Event.id)).where(Event.severity == "critical")) or 0
    high_events = db.scalar(select(func.count(Event.id)).where(Event.severity == "high")) or 0
    active_buses = db.scalar(select(func.count(Bus.id)).where(Bus.status == "ACTIVE")) or 0
    road_defects = db.scalar(select(func.count(Event.id)).where(Event.event_type.in_(["pothole", "waterlogging", "missing_sign", "missing_zebra", "missing_divider"]))) or 0
    traffic_events = db.scalar(select(func.count(Event.id)).where(Event.event_type == "traffic_bottleneck")) or 0
    return {
        "total_events": total_events, 
        "critical_events": critical_events, 
        "high_events": high_events, 
        "active_buses": active_buses,
        "road_defects": road_defects,
        "traffic_events": traffic_events
    }
