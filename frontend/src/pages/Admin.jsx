import { useEffect, useState } from "react";
import { api } from "../services/api";

export default function Admin() {
  const [health, setHealth] = useState(null);
  const [sim, setSim] = useState(null);
  const [loading, setLoading] = useState(false);
  const [triggerMsg, setTriggerMsg] = useState("");

  const load = async () => {
    try {
      const [h, s] = await Promise.allSettled([
        api.health(),
        api.simulatorStatus()
      ]);
      setHealth(h.status === "fulfilled" ? h.value : { status: "offline", error: "Cannot reach :8000" });
      setSim(s.status === "fulfilled" ? s.value : { running: false });
    } catch (err) {
      console.error(err);
      setHealth({ status: "offline" });
    }
  };

  useEffect(() => {
    load();
    const interval = setInterval(load, 4000);
    return () => clearInterval(interval);
  }, []);

  const start = async () => {
    setLoading(true);
    try {
      await api.startSimulator();
      await load();
    } finally {
      setLoading(false);
    }
  };

  const stop = async () => {
    setLoading(true);
    try {
      await api.stopSimulator();
      await load();
    } finally {
      setLoading(false);
    }
  };

  const triggerTest = async (type) => {
    try {
      setTriggerMsg(`Injecting ${type}...`);
      const res = await api.triggerIncident(type, "BUS-101");
      setTriggerMsg(`✓ Incident [${res.event_type}] successfully broadcasted! Plate: ${res.plate_number || "N/A"}`);
      setTimeout(() => setTriggerMsg(""), 5000);
    } catch (err) {
      setTriggerMsg(`⚠️ Injection failed: ${err.message}`);
    }
  };

  const isHealthy = health?.status === "ok";

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-bold">Admin & System Operations</h2>
        <p className="text-sm text-slate-400">Control edge simulation, backend telemetry, and diagnostics.</p>
      </div>

      {triggerMsg && (
        <div className="p-3 rounded-lg bg-cyan-950 border border-cyan-500/50 text-cyan-300 text-xs font-mono">
          {triggerMsg}
        </div>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Backend Node Status */}
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <div className="flex justify-between items-start">
            <h3 className="font-semibold text-slate-200">FastAPI Backend Node</h3>
            <span
              className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                isHealthy
                  ? "bg-emerald-500/20 text-emerald-400 border border-emerald-500/30"
                  : "bg-rose-500/20 text-rose-400 border border-rose-500/30"
              }`}
            >
              {health?.status || "CHECKING"}
            </span>
          </div>
          <div className="mt-4 space-y-2 text-xs text-slate-400">
            <p>Port: <b className="text-slate-200">8000 (REST + WebSocket /ws/events)</b></p>
            <p>Database: <b className="text-slate-200">SQLite (urban_intelligence.db)</b></p>
            <p>Evidence Mount: <b className="text-slate-200">/evidence</b></p>
          </div>
          <button
            onClick={load}
            className="mt-4 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 px-3 py-1.5 text-xs font-medium transition-colors"
          >
            Refresh Health Probe
          </button>
        </section>

        {/* Fleet & Incident Simulator */}
        <section className="rounded-xl border border-slate-800 bg-slate-900 p-5">
          <div className="flex justify-between items-start">
            <h3 className="font-semibold text-slate-200">Fleet AI Simulator</h3>
            <span
              className={`px-2 py-0.5 rounded text-xs font-bold uppercase ${
                sim?.running
                  ? "bg-cyan-500/20 text-cyan-300 border border-cyan-500/30"
                  : "bg-slate-800 text-slate-400"
              }`}
            >
              {sim?.running ? "RUNNING (4 Buses Active)" : "STOPPED"}
            </span>
          </div>
          <p className="mt-2 text-xs text-slate-400">
            Simulates 4 public transit buses driving through Jaipur, emitting GPS drift, speed anomalies, road hazards, and incidents.
          </p>
          <div className="mt-4 flex gap-2">
            <button
              onClick={start}
              disabled={loading || sim?.running}
              className="rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white font-semibold px-4 py-2 text-xs transition-colors disabled:opacity-40"
            >
              Start Simulator
            </button>
            <button
              onClick={stop}
              disabled={loading || !sim?.running}
              className="rounded-lg bg-rose-600 hover:bg-rose-500 text-white font-semibold px-4 py-2 text-xs transition-colors disabled:opacity-40"
            >
              Stop Simulator
            </button>
          </div>
        </section>
      </div>

      {/* Incident Demo Simulator Box */}
      <section className="rounded-xl border border-slate-800 bg-slate-900 p-5">
        <h3 className="font-semibold text-slate-200 mb-1">Instant Incident Generator (For SIH Demonstration)</h3>
        <p className="text-xs text-slate-400 mb-4">
          Click to immediately generate a high-priority incident with ANPR plate extraction, GPS coordinate sync, and visual evidence overlay.
        </p>
        <div className="flex flex-wrap gap-3">
          <button
            onClick={() => triggerTest("hit_and_run")}
            className="rounded-lg bg-rose-600/80 hover:bg-rose-500 text-white px-4 py-2 text-xs font-semibold flex items-center gap-2"
          >
            <span>🚨</span> Trigger Hit & Run Incident
          </button>
          <button
            onClick={() => triggerTest("rash_driving")}
            className="rounded-lg bg-amber-600/80 hover:bg-amber-500 text-white px-4 py-2 text-xs font-semibold flex items-center gap-2"
          >
            <span>⚠️</span> Trigger Rash Driving Incident
          </button>
          <button
            onClick={() => triggerTest("pedestrian_risk")}
            className="rounded-lg bg-fuchsia-600/80 hover:bg-fuchsia-500 text-white px-4 py-2 text-xs font-semibold flex items-center gap-2"
          >
            <span>🚶</span> Trigger Pedestrian Safety Alert
          </button>
        </div>
      </section>
    </div>
  );
}
