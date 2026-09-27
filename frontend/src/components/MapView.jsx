import { MapContainer, Marker, Popup, TileLayer, CircleMarker } from "react-leaflet";
import { API_BASE } from "../services/api";

const EVENT_COLORS = {
  pothole: "#ef4444",
  waterlogging: "#3b82f6",
  traffic_bottleneck: "#f59e0b",
  hit_and_run: "#a855f7",
  rash_driving: "#a855f7",
  missing_sign: "#f97316",
  missing_zebra: "#f97316",
  missing_divider: "#f97316",
  pedestrian_risk: "#ec4899",
  default: "#6b7280"
};

const SEVERITY_RADIUS = {
  critical: 14,
  high: 12,
  medium: 10,
  low: 8
};

const getEventColor = (type) => EVENT_COLORS[type] || EVENT_COLORS.default;
const getSeverityRadius = (severity) => SEVERITY_RADIUS[severity] || 10;

const SeverityBadge = ({ severity }) => {
  const colors = {
    critical: "text-red-500 font-bold",
    high: "text-amber-500 font-semibold",
    medium: "text-blue-500 font-semibold",
    low: "text-green-500 font-semibold"
  };
  return <span className={colors[severity] || "text-slate-400"}>{severity}</span>;
};

export default function MapView({ buses = [], events = [] }) {
  return (
    <div className="h-full w-full min-h-[400px] overflow-hidden rounded-xl border border-slate-800">
      <MapContainer center={[26.9124, 75.7873]} zoom={13} scrollWheelZoom className="h-full w-full min-h-[400px]">
        <TileLayer 
          attribution='&copy; OpenStreetMap contributors' 
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" 
        />
        {buses.map((b) => (
          <CircleMarker 
            key={b.bus_code} 
            center={[b.latitude, b.longitude]} 
            radius={8} 
            pathOptions={{ color: "#06b6d4", fillColor: "#06b6d4", fillOpacity: 0.8 }}
          >
            <Popup>
              <strong>{b.bus_code}</strong><br />
              Route: {b.route_name}<br />
              Speed: {b.speed_kmph} km/h
            </Popup>
          </CircleMarker>
        ))}
        {events.map((e) => (
          <CircleMarker 
            key={`event-${e.id}`} 
            center={[e.latitude, e.longitude]} 
            radius={getSeverityRadius(e.severity)}
            pathOptions={{ color: getEventColor(e.event_type), fillColor: getEventColor(e.event_type), fillOpacity: 0.6 }}
          >
            <Popup>
              <strong>{e.event_type}</strong><br />
              Bus: {e.bus_code}<br />
              Time: {new Date(e.timestamp).toLocaleString()}<br />
              Severity: <SeverityBadge severity={e.severity} /><br />
              Confidence: {(e.confidence * 100).toFixed(0)}%
              {e.evidence_path && (
                <div>
                  <img src={`${API_BASE}/evidence/${e.evidence_path}`} alt="Evidence" style={{ width: "200px", borderRadius: "8px", marginTop: "8px" }} />
                </div>
              )}
            </Popup>
          </CircleMarker>
        ))}
      </MapContainer>
    </div>
  );
}
