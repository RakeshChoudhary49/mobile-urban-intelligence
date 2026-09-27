class EventGenerator:
    SEVERITY_DEFAULTS = {
        "pothole": "medium", "waterlogging": "medium", "missing_zebra": "medium",
        "missing_sign": "medium", "missing_divider": "high", "traffic_bottleneck": "medium",
        "pedestrian_risk": "high", "rash_driving": "high", "hit_and_run": "critical",
    }
    def generate(self, *, bus_code, latitude, longitude, speed_kmph, event_type, confidence, message, source_camera="front", plate_number=None, plate_confidence=None, severity=None, evidence_path=None):
        return {
            "bus_code": bus_code, "event_type": event_type,
            "severity": severity or self.SEVERITY_DEFAULTS.get(event_type, "medium"),
            "confidence": confidence, "latitude": latitude, "longitude": longitude,
            "speed_kmph": speed_kmph, "plate_number": plate_number,
            "plate_confidence": plate_confidence, "message": message,
            "evidence_path": evidence_path, "source_camera": source_camera,
        }
