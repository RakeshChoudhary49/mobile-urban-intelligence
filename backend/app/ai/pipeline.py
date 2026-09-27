from app.ai.anpr_engine import ANPREngine
from app.ai.detector import VehicleDetector
from app.ai.event_generator import EventGenerator
from app.ai.hazard_detector import HazardDetector
from app.ai.incident_detector import IncidentDetector
from app.ai.tracker import SimpleTracker
from app.ai.traffic_analyzer import TrafficAnalyzer

class EdgeAIPipeline:
    # detector -> tracker -> hazard_detector -> traffic_analyzer -> incident_detector -> anpr_engine -> event_generator
    def __init__(self):
        self.detector = VehicleDetector()
        self.tracker = SimpleTracker()
        self.hazard_detector = HazardDetector()
        self.traffic_analyzer = TrafficAnalyzer()
        self.incident_detector = IncidentDetector()
        self.anpr = ANPREngine()
        self.generator = EventGenerator()

    def process(self, *, bus_code, latitude, longitude, speed_kmph, previous_speed_kmph, scenario=None, vehicle_count=None, camera="front"):
        detections = self.detector.detect(simulated_count=vehicle_count)
        tracks = self.tracker.update(detections)
        traffic = self.traffic_analyzer.analyze(tracks, speed_kmph)
        hazard = self.hazard_detector.analyze(scenario=scenario)
        incident = self.incident_detector.analyze(speed_kmph=speed_kmph, previous_speed_kmph=previous_speed_kmph, scenario=scenario)
        event_data = None
        if hazard:
            event_data = self.generator.generate(bus_code=bus_code, latitude=latitude, longitude=longitude, speed_kmph=speed_kmph, event_type=hazard["event_type"], confidence=hazard["confidence"], message=hazard["message"], source_camera=camera)
        elif incident:
            plate = self.anpr.extract(enabled=incident["event_type"] == "hit_and_run")
            event_data = self.generator.generate(bus_code=bus_code, latitude=latitude, longitude=longitude, speed_kmph=speed_kmph, event_type=incident["event_type"], confidence=incident["confidence"], message=incident["message"], source_camera=camera, plate_number=plate["plate_number"] if plate else None, plate_confidence=plate["plate_confidence"] if plate else None, severity=incident["severity"])
        elif traffic["bottleneck"]:
            event_data = self.generator.generate(bus_code=bus_code, latitude=latitude, longitude=longitude, speed_kmph=speed_kmph, event_type="traffic_bottleneck", confidence=0.90, message="Traffic bottleneck detected", source_camera=camera)
        return {"traffic": traffic, "tracks": tracks, "event": event_data}
