import React from "react"
import { Routes, Route } from "react-router-dom";
import PrivateRoute from "./auth/PrivateRoute";
import AppShell from "./pages/AppShell";
import PublicLookup from "./pages/PublicLookup";
import Login from "./pages/Login";
import Machines from "./pages/Machines";
import Maintenance from "./pages/Maintenance";
import Complaints from "./pages/Complaints";

export default function App(){
  return (
    <Routes>
      <Route path="/" element={<PublicLookup/>} />
      <Route path="/login" element={<Login/>} />
      <Route element={<PrivateRoute/>}>
        <Route path="/app" element={<AppShell/>}>
          <Route path="machines" element={<Machines/>} />
          <Route path="maintenance" element={<Maintenance/>} />
          <Route path="complaints" element={<Complaints/>} />
          <Route index element={<Machines/>} />
        </Route>
      </Route>
    </Routes>
  );
}
