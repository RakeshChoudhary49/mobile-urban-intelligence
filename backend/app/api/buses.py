from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import Bus
from app.schemas import BusOut

router = APIRouter(prefix="/api/buses", tags=["buses"])

@router.get("", response_model=list[BusOut])
def list_buses(db: Session = Depends(get_db)):
    return db.scalars(select(Bus).order_by(Bus.bus_code)).all()
