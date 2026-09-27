import { useEffect, useState } from "react";
import { api, API_BASE } from "../services/api";

const SeverityBadge = ({ severity }) => {
  const styles = {
    critical: "bg-red-500/20 text-red-400",
    high: "bg-amber-500/20 text-amber-400",
    medium: "bg-blue-500/20 text-blue-400",
    low: "bg-green-500/20 text-green-400"
  };
  const className = styles[severity] || "bg-slate-500/20 text-slate-400";
  return (
    <span className={`px-2 py-1 rounded text-xs font-semibold uppercase ${className}`}>
      {severity}
    </span>
  );
};

export default function Evidence() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    api.events("?limit=200").then(setEvents);
  }, []);

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Evidence Vault</h2>
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {events.map((e) => (
          <article key={e.id} className="rounded-xl border border-slate-800 bg-slate-900 overflow-hidden flex flex-col">
            <div className="h-48 bg-slate-800 flex items-center justify-center overflow-hidden">
              {e.evidence_path ? (
                <img 
                  src={`${API_BASE}/evidence/${e.evidence_path}`} 
                  alt={e.event_type}
                  className="w-full h-full object-cover transition-transform hover:scale-105" 
                />
              ) : (
                <span className="text-slate-500">No image available</span>
              )}
            </div>
            <div className="p-4 flex-1 flex flex-col">
              <div className="flex justify-between items-start mb-2">
                <h3 className="font-semibold text-lg">{e.event_type}</h3>
                <SeverityBadge severity={e.severity} />
              </div>
              <div className="text-xs text-slate-400 mb-4 space-y-1">
                <p>Bus: <span className="text-slate-300">{e.bus_code}</span></p>
                <p>Time: <span className="text-slate-300">{new Date(e.timestamp).toLocaleString()}</span></p>
                <p>Confidence: <span className="text-slate-300">{(e.confidence * 100).toFixed(0)}%</span></p>
                <p>GPS: <span className="text-slate-300">{e.latitude?.toFixed(4)}, {e.longitude?.toFixed(4)}</span></p>
              </div>
            </div>
          </article>
        ))}
      </div>
    </div>
  );
}
