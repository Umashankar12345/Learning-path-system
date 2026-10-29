import React, { createContext, useContext, useState, useEffect } from "react";
import api from "../api/client";

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      const token = localStorage.getItem("access_token");
      const storedUser = localStorage.getItem("user");

      if (token && storedUser) {
        try {
          setUser(JSON.parse(storedUser));
          // Refresh user profile from backend
          const res = await api.get("/auth/me/");
          setUser(res.data);
          localStorage.setItem("user", JSON.stringify(res.data));
        } catch (err) {
          console.error("Auth initialization failed:", err);
          logout();
        }
      }
      setLoading(false);
    };

    initAuth();
  }, []);

  const login = async (username, password) => {
    const res = await api.post("/auth/login/", { username, password });
    const { access, refresh } = res.data;
    localStorage.setItem("access_token", access);
    localStorage.setItem("refresh_token", refresh);

    // Fetch user details
    const meRes = await api.get("/auth/me/");
    setUser(meRes.data);
    localStorage.setItem("user", JSON.stringify(meRes.data));
    return meRes.data;
  };

  const signup = async (username, email, password, passwordConfirm) => {
    const res = await api.post("/auth/signup/", {
      username,
      email,
      password,
      password_confirm: passwordConfirm,
    });
    const { user: newUser, token } = res.data;
    localStorage.setItem("access_token", token.access);
    localStorage.setItem("refresh_token", token.refresh);
    setUser(newUser);
    localStorage.setItem("user", JSON.stringify(newUser));
    return newUser;
  };

  const logout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    localStorage.removeItem("user");
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        loading,
        isAuthenticated: !!user,
        login,
        signup,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
};
