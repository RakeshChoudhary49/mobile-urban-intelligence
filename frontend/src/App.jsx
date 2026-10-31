import {useState} from "react";
import {BrowserRouter,Navigate,Route,Routes} from "react-router-dom";
import Layout from "./layout/Layout.jsx";
import Login from "./pages/Login.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import LiveMap from "./pages/LiveMap.jsx";
import TrafficAnalytics from "./pages/TrafficAnalytics.jsx";
import RoadConditions from "./pages/RoadConditions.jsx";
import Incidents from "./pages/Incidents.jsx";
import Fleet from "./pages/Fleet.jsx";
import Evidence from "./pages/Evidence.jsx";
import Admin from "./pages/Admin.jsx";

export default function App(){
  const [role,setRole]=useState(localStorage.getItem("urban_role")||"");
  const login=r=>{localStorage.setItem("urban_role",r);setRole(r)};
  if(!role)return <Login onLogin={login}/>;
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout role={role}/>}>
          <Route path="/" element={<Dashboard/>}/>
          <Route path="/map" element={<LiveMap/>}/>
          <Route path="/traffic" element={<TrafficAnalytics/>}/>
          <Route path="/roads" element={<RoadConditions/>}/>
          <Route path="/incidents" element={<Incidents/>}/>
          <Route path="/fleet" element={<Fleet/>}/>
          <Route path="/evidence" element={<Evidence/>}/>
          <Route path="/admin" element={<Admin/>}/>
          <Route path="*" element={<Navigate to="/" replace/>}/>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}