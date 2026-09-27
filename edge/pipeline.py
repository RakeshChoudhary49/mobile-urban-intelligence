import cv2
import supervision as sv
from detector import Detector
from tracker import Tracker
from anpr import ANPREngine
from event_engine import EventEngine
from gps_simulator import GPSSimulator
from uploader import Uploader
import config

class Pipeline:
    def __init__(self):
        self.detector = Detector()
        self.tracker = Tracker()
        self.anpr = ANPREngine()
        self.event_engine = EventEngine()
        self.gps = GPSSimulator()
        self.uploader = Uploader()

    def run(self, video_path, show_output=False, save_output=False):
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            print(f"Error: Could not open video file {video_path}")
            return

        frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
        frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
        fps = int(cap.get(cv2.CAP_PROP_FPS))
        
        out = None
        if save_output:
            out = cv2.VideoWriter('output.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (frame_width, frame_height))

        # Annotators
        box_annotator = sv.BoxAnnotator()
        label_annotator = sv.LabelAnnotator()

        frame_count = 0
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break
                
            frame_count += 1
            
            # Process only every Nth frame
            if frame_count % config.FRAME_SKIP != 0:
                continue

            # 1. GPS
            gps_data = self.gps.get_position(frame_count)

            # 2. Detection
            raw_detections = self.detector.detect(frame)

            # 3. Tracking
            tracked_objects = self.tracker.update(raw_detections)

            # 4. Event Generation
            events = self.event_engine.process_detections(tracked_objects, gps_data)

            # 5. Process Events & ANPR & Upload
            for event in events:
                bbox = event.pop('_bbox')
                tid = event.pop('_track_id')
                
                # Check for ANPR on vehicles or vehicle-related incidents
                if event['event_type'] in ['car', 'truck', 'bus', 'motorcycle', 'rash_driving', 'hit_and_run']:
                    x1, y1, x2, y2 = map(int, bbox)
                    h, w = frame.shape[:2]
                    x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
                    crop = frame[y1:y2, x1:x2]
                    plate_data = self.anpr.read_plate(crop)
                    if plate_data:
                        event['plate_number'] = plate_data['plate_text']
                        event['plate_confidence'] = plate_data['confidence']
                        print(f"🔍 Found plate: {plate_data['plate_text']} for track {tid}")

                # Save evidence
                evidence_path = self.uploader.save_evidence(frame, bbox, event['event_type'])
                event['evidence_path'] = evidence_path
                
                # Upload
                print(f"🚨 EVENT DETECTED: {event['event_type']} (Conf: {event['confidence']:.2f})")
                self.uploader.upload_event(event)

            # 6. Visualization
            if show_output or save_output:
                if tracked_objects:
                    import numpy as np
                    xyxy = np.array([obj['bbox'] for obj in tracked_objects])
                    track_id = np.array([obj['track_id'] for obj in tracked_objects])
                    class_id = np.array([obj['class_id'] for obj in tracked_objects])
                    
                    labels = [f"#{tid} {obj['class_name']} {obj['confidence']:.2f}" for tid, obj in zip(track_id, tracked_objects)]
                    
                    sv_dets = sv.Detections(xyxy=xyxy, tracker_id=track_id, class_id=class_id)
                    
                    annotated_frame = box_annotator.annotate(scene=frame.copy(), detections=sv_dets)
                    annotated_frame = label_annotator.annotate(scene=annotated_frame, detections=sv_dets, labels=labels)
                else:
                    annotated_frame = frame.copy()

                # Draw GPS
                cv2.putText(annotated_frame, f"GPS: {gps_data['latitude']:.4f}, {gps_data['longitude']:.4f} | {gps_data['speed_kmph']} km/h", 
                           (20, 40), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

                if show_output:
                    cv2.imshow("Urban Intelligence Pipeline", annotated_frame)
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        break
                        
                if save_output:
                    out.write(annotated_frame)

        cap.release()
        if out:
            out.release()
        cv2.destroyAllWindows()
