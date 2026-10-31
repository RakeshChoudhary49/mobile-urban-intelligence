const WS_URL = import.meta.env.VITE_API_URL 
  ? import.meta.env.VITE_API_URL.replace(/^http/, 'ws') 
  : "ws://127.0.0.1:8000";

export function connectEventSocket(onMessage) {
  const ws = new WebSocket(`${WS_URL}/ws/events`);
  
  ws.onopen = () => console.log("WebSocket connected");
  
  ws.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data); // Triggers the reload in Dashboard
    } catch (e) {
      console.error("WebSocket message error:", e);
    }
  };

  ws.onerror = (error) => console.error("WebSocket error:", error);
  ws.onclose = () => console.log("WebSocket disconnected");

  return ws;
}