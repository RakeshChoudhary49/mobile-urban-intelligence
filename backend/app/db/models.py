from datetime import datetime
from sqlalchemy import Boolean, DateTime, Float, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from app.db.database import Base

class Bus(Base):
    __tablename__ = "buses"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bus_code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    route_name: Mapped[str] = mapped_column(String(100), default="Route A")
    driver_name: Mapped[str] = mapped_column(String(100), default="Unknown")
    status: Mapped[str] = mapped_column(String(30), default="ACTIVE")
    latitude: Mapped[float] = mapped_column(Float, default=26.9124)
    longitude: Mapped[float] = mapped_column(Float, default=75.7873)
    speed_kmph: Mapped[float] = mapped_column(Float, default=0.0)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Event(Base):
    __tablename__ = "events"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    bus_code: Mapped[str] = mapped_column(String(50), index=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    severity: Mapped[str] = mapped_column(String(20), default="medium")
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    latitude: Mapped[float] = mapped_column(Float)
    longitude: Mapped[float] = mapped_column(Float)
    speed_kmph: Mapped[float] = mapped_column(Float, default=0.0)
    plate_number: Mapped[str | None] = mapped_column(String(30), nullable=True)
    plate_confidence: Mapped[float | None] = mapped_column(Float, nullable=True)
    message: Mapped[str] = mapped_column(Text, default="")
    evidence_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    source_camera: Mapped[str] = mapped_column(String(30), default="front")
    acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
