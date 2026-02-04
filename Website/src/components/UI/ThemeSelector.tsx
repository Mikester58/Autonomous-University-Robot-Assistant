// src/components/UI/ThemeSelector.tsx

import { useEffect, useState } from "react";
import {
  loadTheme,
  saveTheme,
  applyTheme,
} from "../../services/themeStore";

import type { ThemeOption } from "../../services/themeStore";
import "../../styles/theme.css";

// Simple dropdown that controls the global COLOR theme.
// Dashboard layout is handled separately.
export default function ThemeSelector() {
  const [theme, setTheme] = useState<ThemeOption>(() => loadTheme());

  // Whenever the theme changes, apply it + persist it.
  useEffect(() => {
    applyTheme(theme);
    saveTheme(theme);
  }, [theme]);

  return (
    <div className="theme-selector">
      <label htmlFor="theme-select">Color Theme</label>
      <select
        id="theme-select"
        value={theme}
        onChange={(e) => setTheme(e.target.value as ThemeOption)}
      >
        <option value="tamu">TAMU (Maroon)</option>
        <option value="robotic">Robotic</option>
        <option value="dark">Dark</option>
        <option value="light">Light</option>
      </select>
    </div>
  );
}
