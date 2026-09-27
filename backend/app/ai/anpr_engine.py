class ANPREngine:
    # Simulation ANPR. Replace with plate detection + OCR model inference.
    def extract(self, frame=None, enabled=True):
        if not enabled:
            return None
        return {"plate_number": "RJ14CD4821", "plate_confidence": 0.94}
