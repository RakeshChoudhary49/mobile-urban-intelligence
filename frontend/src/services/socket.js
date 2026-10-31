const WS_URL = import.meta.env.VITE_API_URL 
  ? import.meta.env.VITE_API_URL.replace(/^http/, 'ws') 
  : "ws://127.0.0.1:8000";   