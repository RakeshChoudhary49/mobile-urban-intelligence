const API_BASE = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

async function request(path, options = {}) {
  const r = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...(options.headers || {}) },
    ...options
  });
  if (!r.ok) throw new Error(await r.text() || `HTTP ${r.status}`);
  return r.json();
}

export const api = {
  summary: () => request("/api/summary"),
  events: (q = "") => request(`/api/events${q}`),
  buses: () => request("/api/buses"),
  traffic: () => request("/api/analytics/traffic"),
  roadConditions: () => request("/api/analytics/road-conditions"),
  simulatorStatus: () => request("/api/simulator/status"),
  startSimulator: () => request("/api/simulator/start", { method: "POST" }),
  stopSimulator: () => request("/api/simulator/stop", { method: "POST" }),
  triggerIncident: (incident_type = "hit_and_run", bus_code = "BUS-101") =>
    request("/api/simulator/trigger-incident", {
      method: "POST",
      body: JSON.stringify({ incident_type, bus_code })
    }),
  health: () => request("/api/system/health"),
  acknowledgeEvent: (id) => request(`/api/events/${id}/acknowledge`, { method: "PATCH" }),
  heatmap: () => request("/api/analytics/heatmap"),
  eventTrends: (hours = 24) => request(`/api/analytics/event-trends?hours=${hours}`)
};

export { API_BASE };
