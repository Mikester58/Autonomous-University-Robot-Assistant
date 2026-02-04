# Website/backend/camera_api.py
import os
import time
import threading
from pathlib import Path

import cv2
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

# Always load Website/.env regardless of where uvicorn is launched from
load_dotenv(Path(__file__).resolve().parents[1] / ".env")

APP_HOST = os.getenv("CAMERA_API_HOST", "127.0.0.1")
APP_PORT = int(os.getenv("CAMERA_API_PORT", "9000"))

ALLOWED_ORIGINS = [o.strip() for o in os.getenv("ALLOWED_ORIGINS", "").split(",") if o.strip()]
ALLOWED_IPS = {ip.strip() for ip in os.getenv("ALLOWED_IPS", "").split(",") if ip.strip()}
API_TOKEN = os.getenv("API_TOKEN", "")

CAMERA_INDEX = os.getenv("CAMERA_INDEX", "0")
CAMERA_FPS = int(os.getenv("CAMERA_FPS", "10"))
CAMERA_JPEG_QUALITY = int(os.getenv("CAMERA_JPEG_QUALITY", "70"))
CAMERA_WIDTH = int(os.getenv("CAMERA_WIDTH", "640"))
CAMERA_HEIGHT = int(os.getenv("CAMERA_HEIGHT", "480"))

# ------------------------------------------------------------
# Security helpers
# ------------------------------------------------------------
def get_client_ip(request: Request) -> str:
    # NOTE: If you later put this behind a reverse proxy/tunnel,
    # you'd want to validate and possibly use X-Forwarded-For.
    return request.client.host


def require_ip_allowlist(request: Request):
    if not ALLOWED_IPS:
        return  # if empty, allow all (not recommended)
    ip = get_client_ip(request)
    if ip not in ALLOWED_IPS:
        raise HTTPException(status_code=403, detail=f"IP not allowed: {ip}")


def require_bearer_token(request: Request):
    if not API_TOKEN:
        raise HTTPException(status_code=500, detail="Server missing API_TOKEN")
    auth = request.headers.get("authorization", "")
    if auth != f"Bearer {API_TOKEN}":
        raise HTTPException(status_code=401, detail="Invalid token")


# ------------------------------------------------------------
# Camera manager (keeps camera open to avoid flicker)
# ------------------------------------------------------------
_cam_lock = threading.Lock()
_cam = None


def _open_camera_inner():
    src = CAMERA_INDEX
    if src.isdigit():
        src = int(src)

    # Windows: DirectShow is usually the most reliable.
    # On Jetson/Linux, CAP_DSHOW is ignored; OpenCV will use V4L2.
    cap = cv2.VideoCapture(src, cv2.CAP_DSHOW)

    if not cap.isOpened():
        raise RuntimeError(f"Could not open camera: {CAMERA_INDEX}")

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
    cap.set(cv2.CAP_PROP_FPS, CAMERA_FPS)

    # Warm-up
    time.sleep(0.2)
    return cap


def get_camera():
    global _cam
    with _cam_lock:
        if _cam is not None and _cam.isOpened():
            return _cam

        # (Re)open camera
        _cam = _open_camera_inner()
        return _cam


def read_frame():
    cap = get_camera()

    # Try multiple reads; prevents intermittent blank frames
    for _ in range(20):
        ok, frame = cap.read()
        if ok and frame is not None:
            return frame
        time.sleep(0.05)

    # If it fails, release and try to recover next call
    global _cam
    with _cam_lock:
        try:
            if _cam is not None:
                _cam.release()
        finally:
            _cam = None

    raise RuntimeError("Failed to read frame from camera")


# ------------------------------------------------------------
# FastAPI app
# ------------------------------------------------------------
app = FastAPI()

if ALLOWED_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["Authorization", "Content-Type"],
    )


@app.get("/health")
def health():
    return {"ok": True}


@app.get("/camera/snapshot")
def snapshot(request: Request):
    require_ip_allowlist(request)
    require_bearer_token(request)

    try:
        frame = read_frame()
        ok, jpg = cv2.imencode(
            ".jpg",
            frame,
            [int(cv2.IMWRITE_JPEG_QUALITY), CAMERA_JPEG_QUALITY],
        )
        if not ok:
            raise HTTPException(status_code=500, detail="Failed to encode JPEG")

        return Response(content=jpg.tobytes(), media_type="image/jpeg")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/camera/stream")
def stream(request: Request):
    require_ip_allowlist(request)
    require_bearer_token(request)

    frame_delay = 1.0 / max(CAMERA_FPS, 1)

    def gen():
        while True:
            try:
                frame = read_frame()
                ok, jpg = cv2.imencode(
                    ".jpg",
                    frame,
                    [int(cv2.IMWRITE_JPEG_QUALITY), CAMERA_JPEG_QUALITY],
                )
                if not ok:
                    time.sleep(frame_delay)
                    continue

                yield (
                    b"--frame\r\n"
                    b"Content-Type: image/jpeg\r\n\r\n" + jpg.tobytes() + b"\r\n"
                )
                time.sleep(frame_delay)
            except Exception:
                # brief backoff, then continue (allows recovery if camera hiccups)
                time.sleep(0.2)

    return StreamingResponse(
        gen(),
        media_type="multipart/x-mixed-replace; boundary=frame",
    )
