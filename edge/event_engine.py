import math
import config
from datetime import datetime

class EventEngine:
    def __init__(self):
        # track_id -> frame_count
        self.temporal_tracker = {}
        # List of past events to avoid duplicates: [{'type': str, 'lat': float, 'lon': float, 'time': datetime}]
        self.recent_events = []
        self.min_frames = 3
        self.spatial_dedup_dist_m = 30.0  # meters
        self.temporal_dedup_sec = 45.0   # seconds

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        # Calculate distance in meters between two GPS points
        R = 6371000  # radius of Earth in meters
        phi1 = math.radians(lat1)
        phi2 = math.radians(lat2)
        delta_phi = math.radians(lat2 - lat1)
        delta_lambda = math.radians(lon2 - lon1)
        
        a = math.sin(delta_phi / 2.0) ** 2 + \
            math.cos(phi1) * math.cos(phi2) * \
            math.sin(delta_lambda / 2.0) ** 2
        
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        return R * c

    def _is_duplicate(self, event_type, lat, lon):
        now = datetime.now()
        # Clean up old events
        self.recent_events = [e for e in self.recent_events if (now - e['time']).total_seconds() < self.temporal_dedup_sec]
        
        for e in self.recent_events:
            if e['type'] == event_type:
                dist = self._haversine_distance(lat, lon, e['lat'], e['lon'])
                if dist < self.spatial_dedup_dist_m:
                    return True
        return False

    def process_detections(self, tracked_objects, gps_data):
        """
        Process tracked objects, apply temporal & spatial verification, generate events.
        """
        events = []
        current_track_ids = set([obj['track_id'] for obj in tracked_objects])
        
        # Clean up lost tracks
        tracks_to_delete = [tid for tid in self.temporal_tracker if tid not in current_track_ids]
        for tid in tracks_to_delete:
            del self.temporal_tracker[tid]

        # 1. Inspect tracked objects for road hazards and safety incidents
        for obj in tracked_objects:
            tid = obj['track_id']
            if tid not in self.temporal_tracker:
                self.temporal_tracker[tid] = 1
            else:
                self.temporal_tracker[tid] += 1

            # Process once object is tracked stably
            if self.temporal_tracker[tid] == self.min_frames:
                event_type = None
                severity = "medium"
                message = ""
                
                if obj.get('is_damage', False):
                    event_type = obj['class_name'].lower()
                    severity = "high" if obj['confidence'] > 0.6 else "medium"
                    message = f"Road surface defect ({event_type}) detected"
                elif obj['class_name'] == 'person':
                    event_type = "pedestrian_risk"
                    severity = "high"
                    message = "Pedestrian detected in vehicle transit corridor"
                elif obj['class_name'] in ['car', 'motorcycle', 'truck', 'bus']:
                    # For vehicles, check if speed or density warrants incident classification
                    if gps_data.get('speed_kmph', 0) > 45:
                        event_type = "rash_driving"
                        severity = "high"
                        message = f"High-speed cut-in / rash driving hazard ({obj['class_name']})"
                
                if event_type:
                    lat, lon = gps_data['latitude'], gps_data['longitude']
                    if not self._is_duplicate(event_type, lat, lon):
                        event = {
                            "bus_code": config.BUS_CODE,
                            "event_type": event_type,
                            "severity": severity,
                            "confidence": round(float(obj['confidence']), 2),
                            "latitude": lat,
                            "longitude": lon,
                            "speed_kmph": float(gps_data.get('speed_kmph', 35.0)),
                            "plate_number": None,
                            "plate_confidence": None,
                            "message": message,
                            "source_camera": "front",
                            "_bbox": obj['bbox'],
                            "_track_id": tid
                        }
                        events.append(event)
                        self.recent_events.append({
                            'type': event_type,
                            'lat': lat,
                            'lon': lon,
                            'time': datetime.now()
                        })

        # 2. Check for traffic congestion / bottleneck
        vehicles = [o for o in tracked_objects if o['class_name'] in ['car', 'bus', 'truck', 'motorcycle']]
        if len(vehicles) >= 7:
            lat, lon = gps_data['latitude'], gps_data['longitude']
            if not self._is_duplicate("traffic_bottleneck", lat, lon):
                events.append({
                    "bus_code": config.BUS_CODE,
                    "event_type": "traffic_bottleneck",
                    "severity": "high" if len(vehicles) > 10 else "medium",
                    "confidence": 0.91,
                    "latitude": lat,
                    "longitude": lon,
                    "speed_kmph": float(gps_data.get('speed_kmph', 15.0)),
                    "plate_number": None,
                    "plate_confidence": None,
                    "message": f"Traffic bottleneck detected ({len(vehicles)} vehicles in corridor)",
                    "source_camera": "front",
                    "_bbox": vehicles[0]['bbox'],
                    "_track_id": 0
                })
                self.recent_events.append({
                    'type': "traffic_bottleneck",
                    'lat': lat,
                    'lon': lon,
                    'time': datetime.now()
                })

        return events
