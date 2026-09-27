import {API_BASE} from "./api";
export function connectEventSocket(onMessage){const ws=new WebSocket(API_BASE.replace(/^http/,"ws")+"/ws/events");ws.onopen=()=>ws.send("dashboard-connected");ws.onmessage=e=>{try{onMessage(JSON.parse(e.data))}catch{}};return ws}
