import { useEffect, useRef, useState } from "react";

const BASE = import.meta.env.VITE_CAMERA_API_BASE;
const TOKEN = import.meta.env.VITE_API_TOKEN;

export default function CameraFeedSecure() {
  const [src, setSrc] = useState<string>("");
  const busy = useRef(false);
  const alive = useRef(true);

  useEffect(() => {
    alive.current = true;

    const intervalMs = 16; // 60fps target
    const tick = async () => {
      if (!alive.current || busy.current) return;
      busy.current = true;

      try {
        const res = await fetch(`${BASE}/camera/snapshot`, {
          headers: { Authorization: `Bearer ${TOKEN}` },
          cache: "no-store",
        });
        if (!res.ok) return;

        const blob = await res.blob();
        const url = URL.createObjectURL(blob);

        setSrc((prev) => {
          if (prev) URL.revokeObjectURL(prev);
          return url;
        });
      } finally {
        busy.current = false;
      }
    };

    const id = setInterval(tick, intervalMs);
    tick();

    return () => {
      alive.current = false;
      clearInterval(id);
      setSrc((prev) => {
        if (prev) URL.revokeObjectURL(prev);
        return "";
      });
    };
  }, []);

  return (
    <div className="camera-wrap">
      <div className="camera-frame">
        {src ? <img src={src} alt="Camera" /> : <div className="camera-loading">Loading…</div>}
      </div>
    </div>
  );
}
