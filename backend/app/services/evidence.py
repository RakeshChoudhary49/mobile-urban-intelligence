from pathlib import Path
from datetime import datetime
import re
from app.config import settings

def ensure_evidence_dir() -> Path:
    path = Path(settings.evidence_dir).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path

def generate_hud_svg(bus_code: str, event_type: str, timestamp_str: str, plate_number: str | None = None) -> str:
    """Generates a high-tech dashcam HUD SVG visual evidence frame."""
    color = "#ef4444" if event_type in ("hit_and_run", "rash_driving") else "#f59e0b"
    plate_badge = f'<rect x="250" y="270" width="140" height="34" rx="4" fill="#000" stroke="#facc15" stroke-width="2"/>' \
                  f'<text x="320" y="293" fill="#facc15" font-family="monospace" font-weight="bold" font-size="16" text-anchor="middle">{plate_number}</text>' if plate_number else ""
    
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 360" width="100%" height="100%">
  <defs>
    <linearGradient id="skyGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#0f172a"/>
      <stop offset="50%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#090d16"/>
    </linearGradient>
    <linearGradient id="roadGrad" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#1e293b"/>
      <stop offset="100%" stop-color="#020617"/>
    </linearGradient>
  </defs>

  <!-- Sky & Road Horizon -->
  <rect width="640" height="200" fill="url(#skyGrad)"/>
  <rect y="180" width="640" height="180" fill="url(#roadGrad)"/>

  <!-- Road perspective lanes -->
  <polygon points="320,180 320,180 200,360 140,360" fill="#334155" opacity="0.3"/>
  <polygon points="320,180 320,180 440,360 500,360" fill="#334155" opacity="0.3"/>
  <line x1="320" y1="180" x2="320" y2="360" stroke="#fbbf24" stroke-width="4" stroke-dasharray="16,12" opacity="0.7"/>

  <!-- Camera HUD Borders & Target Box -->
  <rect x="210" y="190" width="220" height="130" fill="none" stroke="{color}" stroke-width="2.5" stroke-dasharray="6,4" rx="6"/>
  <rect x="210" y="165" width="170" height="25" rx="3" fill="{color}"/>
  <text x="218" y="182" fill="#ffffff" font-family="sans-serif" font-weight="bold" font-size="12">{event_type.upper()}</text>
  
  {plate_badge}

  <!-- HUD Reticles -->
  <circle cx="320" cy="180" r="12" fill="none" stroke="#22d3ee" stroke-width="1.5" opacity="0.6"/>
  <line x1="300" y1="180" x2="340" y2="180" stroke="#22d3ee" stroke-width="1" opacity="0.6"/>
  <line x1="320" y1="160" x2="320" y2="200" stroke="#22d3ee" stroke-width="1" opacity="0.6"/>

  <!-- Telemetry Overlay Banner -->
  <rect x="0" y="0" width="640" height="42" fill="#000000" opacity="0.75"/>
  <circle cx="20" cy="21" r="6" fill="#ef4444"/>
  <text x="32" y="26" fill="#ef4444" font-family="monospace" font-weight="bold" font-size="13">REC [FRONT-DASH-01]</text>
  <text x="240" y="26" fill="#38bdf8" font-family="monospace" font-weight="bold" font-size="13">FLEET: {bus_code}</text>
  <text x="460" y="26" fill="#e2e8f0" font-family="monospace" font-size="12">{timestamp_str}</text>

  <!-- Bottom Telemetry HUD -->
  <rect x="0" y="325" width="640" height="35" fill="#000000" opacity="0.75"/>
  <text x="16" y="347" fill="#22c55e" font-family="monospace" font-size="11">GPS: 26.9124N, 75.7873E | SPEED: 36.4 KM/H</text>
  <text x="480" y="347" fill="#94a3b8" font-family="monospace" font-size="11">BEL EDGE-AI v1.0</text>
</svg>"""

def create_simulated_evidence(bus_code: str, event_type: str, plate_number: str | None = None) -> str:
    """Generates viewable SVG visual evidence and returns a web-relative path."""
    safe_bus = re.sub(r'[^A-Za-z0-9_-]', '', bus_code) or "BUS-101"
    directory = ensure_evidence_dir() / safe_bus
    directory.mkdir(parents=True, exist_ok=True)
    
    timestamp = datetime.utcnow()
    filename = f"{timestamp:%Y%m%d_%H%M%S}_{event_type}.svg"
    path = directory / filename
    
    svg_content = generate_hud_svg(safe_bus, event_type, timestamp.strftime("%Y-%m-%d %H:%M:%S UTC"), plate_number)
    path.write_text(svg_content, encoding="utf-8")
    
    return f"{safe_bus}/{filename}"

def save_evidence_image(image_bytes: bytes, bus_code: str, event_type: str) -> str:
    """Save raw evidence bytes and return relative web path."""
    safe_bus = re.sub(r'[^A-Za-z0-9_-]', '', bus_code) or "BUS-101"
    directory = ensure_evidence_dir() / safe_bus
    directory.mkdir(parents=True, exist_ok=True)
    
    filename = f"{datetime.utcnow():%Y%m%d_%H%M%S}_{event_type}.jpg"
    path = directory / filename
    path.write_bytes(image_bytes)
    return f"{safe_bus}/{filename}"
