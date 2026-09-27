class HazardDetector:
    HAZARDS = {
        "pothole": "Road surface defect / pothole",
        "waterlogging": "Waterlogging detected on roadway",
        "missing_zebra": "Possible missing or faded zebra crossing",
        "missing_sign": "Traffic signboard missing/damaged",
        "missing_divider": "Missing/damaged road divider",
    }
    def analyze(self, scenario=None, confidence=0.88):
        if scenario in self.HAZARDS:
            return {"event_type": scenario, "confidence": confidence, "message": self.HAZARDS[scenario]}
        return None
