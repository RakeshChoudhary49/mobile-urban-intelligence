class SimpleTracker:
    # Simulation tracker. Replace with ByteTrack/DeepSORT for production.
    def update(self, detections):
        return [{"track_id": d.object_id, "label": d.label, "confidence": d.confidence, "bbox": d.bbox} for d in detections]
