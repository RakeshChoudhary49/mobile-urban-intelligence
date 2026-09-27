import os
from pathlib import Path

# Base Paths
BASE_DIR = Path(__file__).resolve().parent
EVIDENCE_DIR = BASE_DIR / "evidence"

# Ensure evidence directory exists
os.makedirs(EVIDENCE_DIR, exist_ok=True)

# API Configuration
API_URL = os.getenv("API_URL", "http://localhost:8000/api/events")
BUS_CODE = os.getenv("BUS_CODE", "BUS-101")

# Video Processing Configuration
FRAME_SKIP = 6

# Confidence Thresholds
GENERAL_CONF_THRESH = 0.5
ROAD_DAMAGE_CONF_THRESH = 0.3
ANPR_CONF_THRESH = 0.6

# Models
GENERAL_MODEL_PATH = "yolov8n.pt"
ROAD_DAMAGE_MODEL_PATH = BASE_DIR / "models" / "road_damage.pt"

# GPS Route Coordinates (Jaipur route simulation)
# List of (latitude, longitude) waypoints
JAIPUR_ROUTE = [
    (26.9124, 75.7873),
    (26.9140, 75.7890),
    (26.9155, 75.7905),
    (26.9170, 75.7920),
    (26.9185, 75.7935),
    (26.9200, 75.7950),
    (26.9215, 75.7965),
    (26.9230, 75.7980),
    (26.9245, 75.7995),
    (26.9260, 75.8010),
    (26.9275, 75.8025),
    (26.9290, 75.8040),
    (26.9305, 75.8055),
    (26.9320, 75.8070),
    (26.9335, 75.8085),
    (26.9350, 75.8100),
    (26.9365, 75.8115),
    (26.9380, 75.8130),
    (26.9395, 75.8145),
    (26.9410, 75.8160)
]
