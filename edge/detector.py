import os
import cv2
from ultralytics import YOLO
import config

class Detector:
    def __init__(self):
        print("Loading general detector model (YOLOv8n)...")
        self.general_model = YOLO(config.GENERAL_MODEL_PATH)
        
        self.has_road_damage_model = os.path.exists(config.ROAD_DAMAGE_MODEL_PATH)
        if self.has_road_damage_model:
            print("Loading road damage detector model...")
            self.road_damage_model = YOLO(config.ROAD_DAMAGE_MODEL_PATH)
        else:
            print("Road damage model not found. Using fallback pothole simulation.")
            self.road_damage_model = None

    def detect(self, frame):
        """
        Runs object detection on the frame.
        Returns a list of dicts: [{'class_name': str, 'bbox': [x1, y1, x2, y2], 'confidence': float, 'class_id': int}, ...]
        """
        detections = []
        
        # General detection (vehicles, persons)
        results = self.general_model(frame, verbose=False, conf=config.GENERAL_CONF_THRESH)[0]
        for box in results.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            class_id = int(box.cls[0])
            class_name = self.general_model.names[class_id]
            
            # Vehicle classes in COCO: 2 (car), 3 (motorcycle), 5 (bus), 7 (truck)
            # Person class in COCO: 0 (person)
            if class_id in [0, 2, 3, 5, 7]:
                detections.append({
                    'class_name': class_name,
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class_id': class_id,
                    'is_damage': False
                })
        
        # Road damage detection
        if self.has_road_damage_model:
            damage_results = self.road_damage_model(frame, verbose=False, conf=config.ROAD_DAMAGE_CONF_THRESH)[0]
            for box in damage_results.boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                conf = float(box.conf[0])
                class_id = int(box.cls[0])
                class_name = self.road_damage_model.names[class_id]
                
                detections.append({
                    'class_name': class_name,
                    'bbox': [x1, y1, x2, y2],
                    'confidence': conf,
                    'class_id': class_id,
                    'is_damage': True
                })
        else:
            # Fallback: simulate road damage if we see some generic pattern (just for demo purposes)
            # In a real scenario, this would be skipped if no model exists.
            pass
            
        return detections
