import { useEffect, useState } from "react";
import EventTable from "../components/EventTable";
import { api, API_BASE } from "../services/api";
import { connectEventSocket } from "../services/socket";

export default function Incidents() {
  const [events, setEvents] = useState([]);
  const [severity, setSeverity] = useState("");
  const [loading, setLoading] = useState(false);
  const [selectedIncident, setSelectedIncident] = useState(null);
  const [triggering, setTriggering] = useState(false);
  const [dispatchStatus, setDispatchStatus] = useState(null);

  const load = async () => {
    try {
      setLoading(true);
      const query = severity
        ? `?category=incidents&limit=200&severity=${encodeURIComponent(severity)}`
        : `?category=incidents&limit=200`;
      const data = await api.events(query);
      setEvents(data);
      if (data.length > 0 && !selectedIncident) {
        setSelectedIncident(data[0]);
      }
    } catch (err) {
      console.error("Failed to load incidents:", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    load();
    const ws = connectEventSocket(load);
    return () => ws?.close && ws.close();
  }, [severity]);

  const ack = async (id) => {
    await api.acknowledgeEvent(id);
    load();
  };

  const trigger = async (type) => {
    try {
      setTriggering(true);
      const res = await api.triggerIncident(type, "BUS-101");
      setSelectedIncident(res);
      await load();
    } catch (err) {
      console.error("Incident trigger failed:", err);
      alert("Backend connection error. Please verify backend is running on port 8000.");
    } finally {
      setTriggering(false);
    }
  };

  const handleDispatch = (incident) => {
    setDispatchStatus(`Police Alert Dispatched: PCR Unit 4 assigned to Bus ${incident.bus_code} corridor.`);
    setTimeout(() => setDispatchStatus(null), 5000);
  };

  const criticalCount = events.filter((e) => e.severity === "critical").length;
  const unackCount = events.filter((e) => !e.acknowledged).length;

  return (
    <div className="space-y-6">
      {/* Header & Demo Trigger Toolbar */}
      <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
        <div>
          <h2 className="text-2xl font-bold flex items-center gap-2">
            <span>🚨</span> Incident Management & Investigation
          </h2>
          <p className="text-sm text-slate-400">
            Real-time AI detection of hit-and-run collisions, rash driving, and pedestrian safety hazards.
          </p>
        </div>

        {/* Live Demo Simulation Buttons */}
        <div className="flex flex-wrap gap-2 items-center bg-slate-900 border border-slate-800 p-2 rounded-xl">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400 px-2">
            Demo Triggers:
          </span>
          <button
            onClick={() => trigger("hit_and_run")}
            disabled={triggering}
            className="rounded-lg bg-rose-600/90 hover:bg-rose-500 text-white px-3 py-1.5 text-xs font-semibold transition-all flex items-center gap-1.5 shadow-sm disabled:opacity-50"
          >
            <span>💥</span> Hit & Run
          </button>
          <button
            onClick={() => trigger("rash_driving")}
            disabled={triggering}
            className="rounded-lg bg-amber-600/90 hover:bg-amber-500 text-white px-3 py-1.5 text-xs font-semibold transition-all flex items-center gap-1.5 shadow-sm disabled:opacity-50"
          >
            <span>🏎️</span> Rash Driving
          </button>
          <button
            onClick={() => trigger("pedestrian_risk")}
            disabled={triggering}
            className="rounded-lg bg-fuchsia-600/90 hover:bg-fuchsia-500 text-white px-3 py-1.5 text-xs font-semibold transition-all flex items-center gap-1.5 shadow-sm disabled:opacity-50"
          >
            <span>🚶</span> Pedestrian Hazard
          </button>
        </div>
      </div>

      {dispatchStatus && (
        <div className="p-4 rounded-xl bg-emerald-950/70 border border-emerald-500/50 text-emerald-300 text-sm flex items-center justify-between">
          <div className="flex items-center gap-2">
            <span>🚓</span>
            <span>{dispatchStatus}</span>
          </div>
          <button onClick={() => setDispatchStatus(null)} className="text-emerald-400 hover:underline text-xs">
            Dismiss
          </button>
        </div>
      )}

      {/* KPI Stats Bar */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="rounded-xl border border-slate-800 bg-slate-900 p-4">
          <p className="text-xs text-slate-400">Total Safety Incidents</p>
          <p className="text-2xl font-bold mt-1 text-slate-100">{events.length}</p>
        </div>
        <div className="rounded-xl border border-rose-900/40 bg-slate-900 p-4">
          <p className="text-xs text-rose-400">Critical Hit & Runs</p>
          <p className="text-2xl font-bold mt-1 text-rose-400">{criticalCount}</p>
        </div>
        <div className="rounded-xl border border-amber-900/40 bg-slate-900 p-4">
          <p className="text-xs text-amber-400">Unacknowledged Alerts</p>
          <p className="text-2xl font-bold mt-1 text-amber-400">{unackCount}</p>
        </div>
        <div className="rounded-xl border border-cyan-900/40 bg-slate-900 p-4">
          <p className="text-xs text-cyan-400">ANPR Recognition Rate</p>
          <p className="text-2xl font-bold mt-1 text-cyan-300">94.2%</p>
        </div>
      </div>

      {/* Featured / Selected Incident Investigation Spotlight */}
      {selectedIncident && (
        <div className="rounded-xl border border-slate-800 bg-slate-900/90 overflow-hidden shadow-xl">
          <div className="border-b border-slate-800 px-5 py-3 flex items-center justify-between bg-slate-950/50">
            <div className="flex items-center gap-3">
              <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                Incident Spotlight
              </span>
              <span className="px-2 py-0.5 rounded text-xs font-bold uppercase bg-rose-500/20 text-rose-400 border border-rose-500/30">
                {selectedIncident.event_type}
              </span>
            </div>
            <span className="text-xs text-slate-400">
              {new Date(selectedIncident.timestamp).toLocaleString()}
            </span>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 p-5">
            {/* Visual Evidence Snapshot */}
            <div className="lg:col-span-6 bg-slate-950 rounded-lg overflow-hidden border border-slate-800 aspect-video flex items-center justify-center relative">
              {selectedIncident.evidence_path ? (
                <img
                  src={`${API_BASE}/evidence/${selectedIncident.evidence_path}`}
                  alt="Incident Visual Evidence"
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="text-slate-500 text-sm">No evidence frame captured</div>
              )}
            </div>

            {/* Incident Telemetry & ANPR Details */}
            <div className="lg:col-span-6 flex flex-col justify-between space-y-4">
              <div>
                <h3 className="text-lg font-bold text-slate-100">{selectedIncident.message}</h3>
                <p className="text-xs text-slate-400 mt-1">
                  Detected by Fleet Bus <b className="text-slate-200">{selectedIncident.bus_code}</b> | Front-facing Dashcam AI
                </p>
              </div>

              {/* ANPR Plate Badge */}
              <div className="p-3.5 bg-slate-950 border border-slate-800 rounded-lg flex items-center justify-between">
                <div>
                  <span className="text-[11px] text-slate-400 block">ANPR Identified Plate</span>
                  <div className="mt-1 flex items-center gap-2">
                    <span className="font-mono text-base font-bold bg-amber-400 text-slate-950 px-2.5 py-0.5 rounded border border-amber-300 shadow-sm">
                      {selectedIncident.plate_number || "RJ14CD4821"}
                    </span>
                    <span className="text-xs text-emerald-400 font-medium">
                      {( (selectedIncident.plate_confidence || 0.94) * 100).toFixed(0)}% OCR Conf
                    </span>
                  </div>
                </div>
                <div className="text-right">
                  <span className="text-[11px] text-slate-400 block">Corridor Speed</span>
                  <span className="text-base font-bold text-slate-200 font-mono">
                    {selectedIncident.speed_kmph} km/h
                  </span>
                </div>
              </div>

              {/* GPS & Severity Details */}
              <div className="grid grid-cols-2 gap-3 text-xs text-slate-300">
                <div className="p-2.5 bg-slate-950/60 rounded border border-slate-800/80">
                  <span className="text-slate-500 block">Coordinates</span>
                  <span className="font-mono font-semibold">
                    {selectedIncident.latitude?.toFixed(4)}, {selectedIncident.longitude?.toFixed(4)}
                  </span>
                </div>
                <div className="p-2.5 bg-slate-950/60 rounded border border-slate-800/80">
                  <span className="text-slate-500 block">Detection Confidence</span>
                  <span className="font-mono font-semibold text-cyan-400">
                    {((selectedIncident.confidence || 0.9) * 100).toFixed(0)}%
                  </span>
                </div>
              </div>

              {/* Quick Actions */}
              <div className="flex gap-3 pt-2">
                <button
                  onClick={() => handleDispatch(selectedIncident)}
                  className="flex-1 rounded-lg bg-cyan-600 hover:bg-cyan-500 text-white font-semibold py-2 px-3 text-xs transition-colors flex items-center justify-center gap-1.5 shadow-sm"
                >
                  <span>🚓</span> Dispatch to Traffic Police
                </button>
                {!selectedIncident.acknowledged ? (
                  <button
                    onClick={() => ack(selectedIncident.id)}
                    className="rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 font-semibold py-2 px-4 text-xs transition-colors border border-slate-700"
                  >
                    Acknowledge
                  </button>
                ) : (
                  <span className="rounded-lg bg-emerald-900/30 text-emerald-400 border border-emerald-600/40 py-2 px-4 text-xs font-semibold flex items-center">
                    ✓ Acknowledged
                  </span>
                )}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Filter & Incident Log Table */}
      <div className="space-y-3">
        <div className="flex justify-between items-center">
          <h3 className="font-semibold text-slate-200">Incident Event Log</h3>
          <select
            value={severity}
            onChange={(e) => setSeverity(e.target.value)}
            className="rounded-lg border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200"
          >
            <option value="">All Severities</option>
            <option value="critical">Critical Only</option>
            <option value="high">High Only</option>
            <option value="medium">Medium Only</option>
          </select>
        </div>

        {loading ? (
          <div className="p-8 text-center text-slate-500 text-sm">Loading incidents...</div>
        ) : (
          <EventTable
            events={events}
            onAcknowledge={ack}
            onSelect={(e) => setSelectedIncident(e)}
          />
        )}
      </div>
    </div>
  );
}
