import React from "react";
import { createContext, useContext, useState } from "react";
import api from "../api/axios";

const AuthCtx = createContext(null);
export const useAuth = () => useContext(AuthCtx);

export default function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    const username = localStorage.getItem("username");
    return username ? { username } : null;
  });

  async function login(username, password) {
    const { data } = await api.post("/api/auth/jwt/create/", { username, password });
    localStorage.setItem("access", data.access);
    localStorage.setItem("refresh", data.refresh);
    localStorage.setItem("username", username);

    const me = (await api.get("/api/auth/me/")).data;
    const g = me.groups || [];
    const pref = g.includes("manager") ? "manager" : g.includes("service") ? "service" : g.includes("client") ? "client" : null;
    if (pref) localStorage.setItem("active_role", pref);

    setUser({ username });
  }

  function logout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("username");
    localStorage.removeItem("active_role");
    setUser(null);
  }

  return <AuthCtx.Provider value={{ user, login, logout }}>{children}</AuthCtx.Provider>;
}
