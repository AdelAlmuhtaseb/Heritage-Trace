import { createContext, useContext, useState } from "react";
import client from "../api/client";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [token, setToken] = useState(null);
  const [user, setUser] = useState(null);

  const login = async (email, password) => {
    const res = await client.post("/auth/login", { email, password });
    setToken(res.data.token);
    setUser(res.data.user);
    client.defaults.headers.common["Authorization"] = `Bearer ${res.data.token}`;
  };

  const logout = () => {
    setToken(null);
    setUser(null);
    delete client.defaults.headers.common["Authorization"];
  };

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);