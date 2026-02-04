/* ============================================================
   MOCK API — Simulates Jetson Backend + ESP32 Commands
   Replace this file later with real network calls.
============================================================ */

export async function fetchMetrics() {
    console.log("[MOCK API] fetchMetrics()");
    const data = await import("../mock-api/robot.json");
    await delay(200); // simulate latency
    return data.default;
}

export async function fetchChatLogs() {
    console.log("[MOCK API] fetchChatLogs()");
    const data = await import("../mock-api/chat.json");
    await delay(150);
    return data.default;
}

export async function fetchSystemStatus() {
    console.log("[MOCK API] fetchSystemStatus()");
    const data = await import("../mock-api/status.json");
    await delay(100);
    return data.default;
}

export async function fetchCameraFrame() {
    console.log("[MOCK API] fetchCameraFrame()");
    const data = await import("../mock-api/camera.txt");
    await delay(100);
    return data.default;
}

export async function sendCommand(cmd: string) {
    console.log(`[MOCK API] SEND COMMAND → ${cmd}`);
    await delay(120);
    return { ok: true };
}

/* Utility */
function delay(ms: number) {
    return new Promise(res => setTimeout(res, ms));
}
