from dataclasses import dataclass
import random

@dataclass
class Detection:
    object_id: int
    label: str
    confidence: float
    bbox: tuple[int, int, int, int]

class VehicleDetector:
    VEHICLES = ("car", "bus", "truck", "motorcycle", "auto")
    def detect(self, frame=None, simulated_count: int | None = None):
        count = simulated_count if simulated_count is not None else random.randint(4, 18)
        return [Detection(i + 1, random.choice(self.VEHICLES), round(random.uniform(0.72, 0.98), 3), (random.randint(0, 900), random.randint(0, 450), 120, 90)) for i in range(count)]
