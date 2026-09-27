class TrafficAnalyzer:
    def analyze(self, tracks, speed_kmph):
        vehicle_count = len(tracks)
        classes = {}
        for track in tracks:
            classes[track["label"]] = classes.get(track["label"], 0) + 1
        density = min(100, round(vehicle_count / 20 * 100))
        bottleneck = density >= 75 or (speed_kmph < 10 and vehicle_count >= 10)
        return {"vehicle_count": vehicle_count, "density_percent": density, "average_speed": round(speed_kmph, 1), "bottleneck": bottleneck, "class_counts": classes}
