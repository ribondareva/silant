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
    setUser({ username });
  }

  function logout() {
    localStorage.removeItem("access");
    localStorage.removeItem("refresh");
    localStorage.removeItem("username");
    setUser(null);
  }

  const value = { user, login, logout };
  return <AuthCtx.Provider value={value}>{children}</AuthCtx.Provider>;
}
