import { createContext, useContext, useState } from "react";
import type { ReactNode } from "react";

interface User {
  email: string;
}

interface AuthContextType {
  user: User | null;
  login: () => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType>(null!);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(() => {
    const stored = localStorage.getItem("arua-user");
    return stored ? JSON.parse(stored) : null;
  });

  const login = () => {
    console.log("LOGIN CLICKED ✔");
    const newUser = { email: "student@tamu.edu" };
    setUser(newUser);
    localStorage.setItem("arua-user", JSON.stringify(newUser));
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem("arua-user");
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

// ✅ THIS WAS MISSING
export const useAuth = () => useContext(AuthContext);
