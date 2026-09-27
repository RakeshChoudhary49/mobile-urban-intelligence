class IncidentDetector:
    def analyze(self, speed_kmph, previous_speed_kmph, pedestrian_risk=False, scenario=None):
        if scenario == "hit_and_run":
            return {"event_type": "hit_and_run", "severity": "critical", "confidence": 0.93, "message": "Potential hit-and-run incident detected"}
        if scenario == "rash_driving":
            return {"event_type": "rash_driving", "severity": "high", "confidence": 0.91, "message": "Potential hazardous driving detected"}
        if pedestrian_risk or scenario == "pedestrian_risk":
            return {"event_type": "pedestrian_risk", "severity": "high", "confidence": 0.89, "message": "Vulnerable pedestrian interaction detected"}
        if speed_kmph - previous_speed_kmph <= -25:
            return {"event_type": "rash_driving", "severity": "high", "confidence": 0.88, "message": "Sudden deceleration detected"}
        return None
