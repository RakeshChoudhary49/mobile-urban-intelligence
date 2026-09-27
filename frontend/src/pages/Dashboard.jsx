import { useEffect, useState } from "react";
import { api } from "../services/api";
import { connectEventSocket } from "../services/socket";
import StatCard from "../components/StatCard";
import EventTable from "../components/EventTable";
import MapView from "../components/MapView";

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

export default function Dashboard() {
  const [summary, setSummary] = useState({});
  const [events, setEvents] = useState([]);
  const [buses, setBuses] = useState([]);

  const load = async () => {
    try {
      const [s, e, b] = await Promise.all([
        api.summary(),
        api.events("?limit=20"),
        api.buses()
      ]);
      setSummary(s);
      setEvents(e);
      setBuses(b);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    load();
    const ws = connectEventSocket(load);
    return () => ws?.close && ws.close();
  }, []);

  const ack = async (id) => {
    await api.acknowledgeEvent(id);
    load();
  };

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Command Center</h2>
        <p className="text-sm text-slate-400">Fleet-wide AI event monitoring.</p>
      </div>
      
      {/* KPI Cards Row */}
      <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-6">
        <StatCard title="Total Events" value={summary.total_events ?? 0} />
        <StatCard title="Critical" value={summary.critical_events ?? 0} />
        <StatCard title="High Severity" value={summary.high_events ?? 0} />
        <StatCard title="Active Buses" value={summary.active_buses ?? 0} />
        <StatCard title="Road Defects" value={summary.road_defects ?? 0} />
        <StatCard title="Traffic Events" value={summary.traffic_events ?? 0} />
      </div>

      {/* Middle section: Feed + Map */}
      <div className="grid gap-6 lg:grid-cols-3">
        {/* Live Event Feed (Auto-scroll) */}
        <div className="lg:col-span-1 border border-slate-800 rounded-xl bg-slate-900 flex flex-col h-[400px]">
          <div className="p-4 border-b border-slate-800">
            <h3 className="font-semibold">Live Feed</h3>
          </div>
          <div className="overflow-y-auto flex-1 p-2 space-y-2 custom-scrollbar">
            {events.slice(0, 10).map((e) => (
              <div key={e.id} className="p-3 bg-slate-800/50 rounded-lg flex items-start gap-3 border border-slate-700/50">
                <span className="text-2xl">{getEventIcon(e.event_type)}</span>
                <div className="flex-1 min-w-0">
                  <div className="flex justify-between items-center mb-1">
                    <span className="font-medium text-sm truncate">{e.event_type}</span>
                    <span className="text-xs text-slate-400">{new Date(e.timestamp).toLocaleTimeString()}</span>
                  </div>
                  <div className="flex justify-between text-xs text-slate-400">
                    <span>Bus: {e.bus_code}</span>
                    <span>{(e.confidence * 100).toFixed(0)}% conf</span>
                  </div>
                </div>
              </div>
            ))}
            {!events.length && (
              <div className="text-center text-slate-500 py-4 text-sm">No live events.</div>
            )}
          </div>
        </div>

        {/* Mini Map */}
        <div className="lg:col-span-2 h-[400px]">
          <div className="h-full rounded-xl overflow-hidden border border-slate-800">
            <MapView buses={buses} events={events} />
          </div>
        </div>
      </div>

      {/* Bottom Table */}
      <EventTable events={events} onAcknowledge={ack} />
    </div>
  );
}
