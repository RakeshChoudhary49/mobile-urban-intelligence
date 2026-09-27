import json
import sqlite3
import requests
import os
import cv2
from datetime import datetime
from pathlib import Path
import config

class Uploader:
    def __init__(self):
        self.api_url = config.API_URL
        self.evidence_api_url = self.api_url.rstrip("/") + "/with-evidence"
        self.db_path = config.BASE_DIR / "offline_buffer.db"
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS events
                     (id INTEGER PRIMARY KEY AUTOINCREMENT,
                      payload TEXT,
                      image_path TEXT,
                      status TEXT,
                      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.commit()
        conn.close()

    def save_evidence(self, frame, bbox, event_type):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{event_type}.jpg"
        
        bus_dir = config.EVIDENCE_DIR / config.BUS_CODE
        os.makedirs(bus_dir, exist_ok=True)
        filepath = bus_dir / filename
        
        evidence_frame = frame.copy()
        x1, y1, x2, y2 = map(int, bbox)
        h, w = frame.shape[:2]
        x1, y1, x2, y2 = max(0, x1), max(0, y1), min(w, x2), min(h, y2)
        cv2.rectangle(evidence_frame, (x1, y1), (x2, y2), (0, 0, 255), 2)
        cv2.putText(evidence_frame, event_type.upper(), (x1, max(20, y1 - 8)),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
        
        cv2.imwrite(str(filepath), evidence_frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return str(filepath)

    def upload_event(self, event_dict, local_image_path=None):
        payload_clean = {k: v for k, v in event_dict.items() if not k.startswith('_')}

        # 1. Try multipart upload with evidence image if path is available
        img_to_upload = local_image_path or event_dict.get("evidence_path")
        if img_to_upload and os.path.exists(img_to_upload):
            try:
                form_data = {
                    "bus_code": payload_clean.get("bus_code", config.BUS_CODE),
                    "event_type": payload_clean.get("event_type", "incident"),
                    "severity": payload_clean.get("severity", "medium"),
                    "confidence": str(payload_clean.get("confidence", 0.0)),
                    "latitude": str(payload_clean.get("latitude", 26.9124)),
                    "longitude": str(payload_clean.get("longitude", 75.7873)),
                    "speed_kmph": str(payload_clean.get("speed_kmph", 0.0)),
                    "plate_number": payload_clean.get("plate_number") or "",
                    "plate_confidence": str(payload_clean.get("plate_confidence") or 0.0),
                    "message": payload_clean.get("message", ""),
                    "source_camera": payload_clean.get("source_camera", "front")
                }
                with open(img_to_upload, "rb") as f:
                    files = {"evidence": (os.path.basename(img_to_upload), f, "image/jpeg")}
                    response = requests.post(self.evidence_api_url, data=form_data, files=files, timeout=6)
                if response.status_code in [200, 201]:
                    print(f"✅ Successfully uploaded event with evidence: {payload_clean['event_type']}")
                    return True
            except Exception as e:
                print(f"⚠️ Multipart upload failed: {e}. Trying JSON upload...")

        # 2. Fallback JSON upload
        try:
            response = requests.post(self.api_url, json=payload_clean, timeout=5)
            if response.status_code in [200, 201]:
                print(f"✅ Successfully uploaded event JSON: {payload_clean['event_type']}")
                return True
        except Exception as e:
            print(f"⚠️ Upload failed (Network error): {e}. Event buffered locally.")

        # 3. Buffer to SQLite
        try:
            conn = sqlite3.connect(self.db_path)
            c = conn.cursor()
            c.execute("INSERT INTO events (payload, image_path, status) VALUES (?, ?, 'pending')",
                      (json.dumps(payload_clean), str(img_to_upload) if img_to_upload else "",))
            conn.commit()
            conn.close()
        except Exception as db_err:
            print(f"Failed to buffer to local DB: {db_err}")
            
        return False
