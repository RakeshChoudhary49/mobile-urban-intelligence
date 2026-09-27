import asyncio
import random
from sqlalchemy import select
from app.ai.pipeline import EdgeAIPipeline
from app.db.database import SessionLocal
from app.db.models import Bus
from app.schemas import EventCreate
from app.services.evidence import create_simulated_evidence
from app.services.event_service import create_event

SCENARIOS = [None, None, None, "pothole", "waterlogging", "missing_sign", "missing_zebra", "missing_divider", "traffic_bottleneck", "pedestrian_risk", "rash_driving", "hit_and_run"]

class FleetSimulator:
    def __init__(self):
        self.running = False
        self.task = None
        self.pipeline = EdgeAIPipeline()
        self.positions = {
            "BUS-101": [26.9124, 75.7873],
            "BUS-102": [26.9150, 75.7900],
            "BUS-103": [26.9080, 75.7820],
            "BUS-104": [26.9200, 75.7980]
        }
        self.previous_speed = {code: 25.0 for code in self.positions}

    async def start(self):
        if self.running:
            return
        self.running = True
        self.task = asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False
        if self.task:
            try:
                await asyncio.wait_for(self.task, timeout=2)
            except asyncio.TimeoutError:
                self.task.cancel()
        self.task = None

    async def _loop(self):
        while self.running:
            await self.tick()
            await asyncio.sleep(3)

    async def tick(self):
        db = SessionLocal()
        try:
            for bus_code, position in self.positions.items():
                scenario = random.choice(SCENARIOS)
                position[0] += random.uniform(-0.0015, 0.0015)
                position[1] += random.uniform(-0.0015, 0.0015)
                speed = round(random.uniform(6, 48), 1)
                result = self.pipeline.process(
                    bus_code=bus_code,
                    latitude=position[0],
                    longitude=position[1],
                    speed_kmph=speed,
                    previous_speed_kmph=self.previous_speed[bus_code],
                    scenario=scenario,
                    vehicle_count=random.randint(5, 18),
                    camera="front"
                )
                self.previous_speed[bus_code] = speed
                bus = db.scalar(select(Bus).where(Bus.bus_code == bus_code))
                if bus:
                    bus.latitude, bus.longitude, bus.speed_kmph, bus.status = position[0], position[1], speed, "ACTIVE"
                else:
                    db.add(Bus(
                        bus_code=bus_code,
                        route_name=f"Route {bus_code[-1]}",
                        driver_name=f"Driver {bus_code[-1]}",
                        status="ACTIVE",
                        latitude=position[0],
                        longitude=position[1],
                        speed_kmph=speed
                    ))
                db.commit()
                event = result.get("event")
                if event:
                    event["evidence_path"] = create_simulated_evidence(bus_code, event["event_type"], event.get("plate_number"))
                    payload = EventCreate(**event)
                    await create_event(db, payload)
        finally:
            db.close()

    async def trigger_incident(self, incident_type: str = "hit_and_run", bus_code: str | None = None):
        """Immediately generates and broadcasts a specific high-priority incident for live evaluation."""
        if not bus_code or bus_code not in self.positions:
            bus_code = "BUS-101"
        
        pos = self.positions[bus_code]
        pos[0] += random.uniform(-0.0005, 0.0005)
        pos[1] += random.uniform(-0.0005, 0.0005)

        db = SessionLocal()
        try:
            bus = db.scalar(select(Bus).where(Bus.bus_code == bus_code))
            if not bus:
                bus = Bus(
                    bus_code=bus_code,
                    route_name=f"Route {bus_code[-1]}",
                    driver_name=f"Driver {bus_code[-1]}",
                    status="ACTIVE",
                    latitude=pos[0],
                    longitude=pos[1],
                    speed_kmph=32.0
                )
                db.add(bus)
                db.commit()

            plate_number = "RJ14CD4821" if incident_type in ("hit_and_run", "rash_driving") else None
            plate_conf = 0.94 if plate_number else None
            
            if incident_type == "hit_and_run":
                severity = "critical"
                conf = 0.95
                msg = f"CRITICAL: Hit-and-run collision detected! Offending vehicle plate: {plate_number}. Bus front camera captured impact."
                speed = 42.5
            elif incident_type == "rash_driving":
                severity = "high"
                conf = 0.91
                msg = f"WARNING: Hazardous high-speed cut-in / rash driving by vehicle [{plate_number}]."
                speed = 58.2
            elif incident_type == "pedestrian_risk":
                severity = "high"
                conf = 0.89
                msg = "ALERT: Vulnerable pedestrian detected crossing in bus transit path."
                speed = 24.0
            else:
                severity = "medium"
                conf = 0.85
                msg = f"Incident detected: {incident_type}"
                speed = 30.0

            evidence_path = create_simulated_evidence(bus_code, incident_type, plate_number)
            
            payload = EventCreate(
                bus_code=bus_code,
                event_type=incident_type,
                severity=severity,
                confidence=conf,
                latitude=pos[0],
                longitude=pos[1],
                speed_kmph=speed,
                plate_number=plate_number,
                plate_confidence=plate_conf,
                message=msg,
                evidence_path=evidence_path,
                source_camera="front"
            )
            created_event = await create_event(db, payload)
            return created_event
        finally:
            db.close()
