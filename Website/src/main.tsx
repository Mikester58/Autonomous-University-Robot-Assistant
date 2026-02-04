// src/main.tsx

import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import AppRouter from "./router/AppRouter";
import { AuthProvider } from "./services/authService";
import { loadTheme, applyTheme } from "./services/themeStore";

import "./styles/index.css";
import "./styles/theme.css";

// Apply saved theme (or default TAMU) BEFORE React renders anything
const initialTheme = loadTheme();
applyTheme(initialTheme);

ReactDOM.createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <AppRouter />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
