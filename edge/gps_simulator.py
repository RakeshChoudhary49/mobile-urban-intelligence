import config
import math

class GPSSimulator:
    def __init__(self):
        self.route = config.JAIPUR_ROUTE
        self.num_waypoints = len(self.route)
        self.frames_per_waypoint = 300 # Assume it takes 300 frames to travel between waypoints
        self.current_frame = 0

    def get_position(self, frame_number=None):
        if frame_number is not None:
            self.current_frame = frame_number
        else:
            self.current_frame += 1

        total_frames = self.num_waypoints * self.frames_per_waypoint
        
        # Loop route if we exceed it
        loop_frame = self.current_frame % total_frames
        
        waypoint_idx = loop_frame // self.frames_per_waypoint
        progress = (loop_frame % self.frames_per_waypoint) / self.frames_per_waypoint
        
        idx1 = waypoint_idx
        idx2 = (waypoint_idx + 1) % self.num_waypoints
        
        lat1, lon1 = self.route[idx1]
        lat2, lon2 = self.route[idx2]
        
        # Linear interpolation
        lat = lat1 + (lat2 - lat1) * progress
        lon = lon1 + (lon2 - lon1) * progress
        
        # Calculate mock heading based on direction
        heading = math.degrees(math.atan2(lon2 - lon1, lat2 - lat1))
        if heading < 0:
            heading += 360
            
        return {
            "latitude": round(lat, 6),
            "longitude": round(lon, 6),
            "speed_kmph": 35.5,
            "heading": round(heading, 2)
        }
