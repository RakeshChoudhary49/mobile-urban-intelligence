import numpy as np
import supervision as sv

class Tracker:
    def __init__(self):
        self.byte_tracker = sv.ByteTrack()

    def update(self, raw_detections):
        """
        Updates the tracker with new detections.
        raw_detections: list of dicts from Detector.detect
        Returns a list of dictionaries with track_ids included.
        """
        if not raw_detections:
            # Create empty sv.Detections to update tracker even when nothing detected
            empty_detections = sv.Detections(
                xyxy=np.empty((0, 4)),
                confidence=np.empty((0,)),
                class_id=np.empty((0,))
            )
            self.byte_tracker.update_with_detections(empty_detections)
            return []

        # Convert raw_detections to supervision Detections format
        xyxy = np.array([d['bbox'] for d in raw_detections])
        confidence = np.array([d['confidence'] for d in raw_detections])
        class_id = np.array([d['class_id'] for d in raw_detections])
        
        # Storing additional info to retrieve later
        custom_data = np.array([d['class_name'] for d in raw_detections])
        is_damage = np.array([d['is_damage'] for d in raw_detections])

        sv_detections = sv.Detections(
            xyxy=xyxy,
            confidence=confidence,
            class_id=class_id,
            data={'class_name': custom_data, 'is_damage': is_damage}
        )

        # Update tracker
        tracked_sv_detections = self.byte_tracker.update_with_detections(sv_detections)
        
        tracked_objects = []
        for i in range(len(tracked_sv_detections)):
            tracker_id = tracked_sv_detections.tracker_id[i]
            bbox = tracked_sv_detections.xyxy[i].tolist()
            conf = float(tracked_sv_detections.confidence[i])
            cid = int(tracked_sv_detections.class_id[i])
            
            c_name = tracked_sv_detections.data['class_name'][i]
            damage_flag = tracked_sv_detections.data['is_damage'][i]

            tracked_objects.append({
                'track_id': tracker_id,
                'bbox': bbox,
                'confidence': conf,
                'class_id': cid,
                'class_name': c_name,
                'is_damage': damage_flag
            })

        return tracked_objects
