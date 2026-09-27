from collections import Counter
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Event

router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/traffic")
def traffic_analytics(db: Session = Depends(get_db)):
    events = db.scalars(select(Event).order_by(Event.timestamp.desc()).limit(200)).all()
    congestion = [e for e in events if e.event_type == "traffic_bottleneck"]
    return {"total_events": len(events), "congestion_events": len(congestion), "recent": [{"timestamp": e.timestamp.isoformat(), "speed": e.speed_kmph, "event_type": e.event_type, "bus_code": e.bus_code} for e in events[:30]]}

@router.get("/road-conditions")
def road_conditions(db: Session = Depends(get_db)):
    events = db.scalars(select(Event)).all()
    allowed = ["pothole", "waterlogging", "missing_zebra", "missing_sign", "missing_divider"]
    counts = Counter(e.event_type for e in events if e.event_type in allowed)
    return {"categories": [{"event_type": key, "count": counts.get(key, 0)} for key in allowed]}

@router.get("/heatmap")
def heatmap(db: Session = Depends(get_db)):
    events = db.scalars(select(Event).order_by(Event.timestamp.desc()).limit(500)).all()
    points = []
    for e in events:
        weight = 0.5
        if e.severity == "critical": weight = 1.0
        elif e.severity == "high": weight = 0.8
        elif e.severity == "medium": weight = 0.5
        else: weight = 0.3
        points.append({"lat": e.latitude, "lng": e.longitude, "weight": weight, "event_type": e.event_type})
    return {"points": points}

@router.get("/event-trends")
def event_trends(hours: int = 24, db: Session = Depends(get_db)):
    cutoff = datetime.utcnow() - timedelta(hours=hours)
    events = db.scalars(select(Event).where(Event.timestamp >= cutoff).order_by(Event.timestamp)).all()
    # Group by hour
    hourly = {}
    for e in events:
        key = e.timestamp.strftime("%Y-%m-%d %H:00")
        if key not in hourly:
            hourly[key] = {"hour": key, "total": 0, "pothole": 0, "traffic_bottleneck": 0, "incident": 0, "other": 0}
        hourly[key]["total"] += 1
        if e.event_type == "pothole":
            hourly[key]["pothole"] += 1
        elif e.event_type == "traffic_bottleneck":
            hourly[key]["traffic_bottleneck"] += 1
        elif e.event_type in ("hit_and_run", "rash_driving", "pedestrian_risk"):
            hourly[key]["incident"] += 1
        else:
            hourly[key]["other"] += 1
    return {"trends": list(hourly.values())}
