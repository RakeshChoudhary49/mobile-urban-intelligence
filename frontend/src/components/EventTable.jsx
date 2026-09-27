import { API_BASE } from "../services/api";

const EVENT_ICONS = {
  pothole: "🕳️",
  waterlogging: "💧",
  traffic_bottleneck: "🚗",
  hit_and_run: "🚨",
  rash_driving: "⚠️",
  pedestrian_risk: "🚶",
  missing_sign: "🚧"
};
const getEventIcon = (type) => EVENT_ICONS[type] || "📍";

const SeverityBadge = ({ severity }) => {
  const styles = {
    critical: "bg-red-500/20 text-red-400",
    high: "bg-amber-500/20 text-amber-400",
    medium: "bg-blue-500/20 text-blue-400",
    low: "bg-green-500/20 text-green-400"
  };
  const className = styles[severity] || "bg-slate-500/20 text-slate-400";
  return (
    <span className={`px-2 py-0.5 rounded text-xs font-semibold ${className}`}>
      {severity}
    </span>
  );
};

export default function EventTable({ events = [], onAcknowledge, onSelect }) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-800 bg-slate-900">
      <table className="w-full text-left text-sm">
        <thead className="border-b border-slate-800 text-slate-400">
          <tr>
            {["Time", "Bus", "Event / Detection", "Severity", "Confidence", "Action"].map((x) => (
              <th key={x} className="px-4 py-3">{x}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {events.map((e) => (
            <tr
              key={e.id}
              onClick={() => onSelect?.(e)}
              className="border-b border-slate-800 hover:bg-slate-800/50 cursor-pointer transition-colors"
            >
              <td className="px-4 py-3 whitespace-nowrap text-xs text-slate-300">
                {new Date(e.timestamp).toLocaleString()}
              </td>
              <td className="px-4 py-3 font-medium text-slate-200">{e.bus_code}</td>
              <td className="px-4 py-3">
                <div className="flex items-center gap-2 flex-wrap">
                  <span className="text-base">{getEventIcon(e.event_type)}</span>
                  <span className="font-semibold text-slate-200">{e.event_type}</span>
                  {e.plate_number && (
                    <span className="font-mono text-[11px] bg-amber-400 text-slate-950 px-1.5 py-0.2 rounded font-bold">
                      {e.plate_number}
                    </span>
                  )}
                  {e.evidence_path && (
                    <a
                      href={`${API_BASE}/evidence/${e.evidence_path}`}
                      target="_blank"
                      rel="noreferrer"
                      onClick={(evt) => evt.stopPropagation()}
                      className="text-cyan-400 hover:underline text-xs ml-1"
                    >
                      [View Frame]
                    </a>
                  )}
                </div>
              </td>
              <td className="px-4 py-3 uppercase">
                <SeverityBadge severity={e.severity} />
              </td>
              <td className="px-4 py-3 font-mono text-xs text-slate-300">
                {(e.confidence * 100).toFixed(0)}%
              </td>
              <td className="px-4 py-3" onClick={(evt) => evt.stopPropagation()}>
                {!e.acknowledged ? (
                  <button
                    onClick={() => onAcknowledge?.(e.id)}
                    className="rounded bg-cyan-600 px-3 py-1 text-xs hover:bg-cyan-500 transition-colors text-white font-medium"
                  >
                    Acknowledge
                  </button>
                ) : (
                  <span className="text-xs text-emerald-400 font-medium">✓ Done</span>
                )}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      {!events.length && (
        <div className="p-8 text-center text-slate-500">No events found matching current criteria.</div>
      )}
    </div>
  );
}
