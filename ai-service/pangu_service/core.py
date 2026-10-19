from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import tempfile
from datetime import date, datetime, time, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

UTC = timezone.utc
KST = ZoneInfo("Asia/Seoul")
LEVELS = [1000, 925, 850, 700, 600, 500, 400, 300, 250, 200, 150, 100, 50]
SURFACE_IDS = [151, 165, 166, 167]  # MSLP, U10, V10, T2M
UPPER_IDS = [129, 133, 130, 131, 132]  # Z (not height), Q, T, U, V
SURFACE_SHAPE = (4, 721, 1440)
UPPER_SHAPE = (5, 13, 721, 1440)
ATTRIBUTION = "Input: ECMWF IFS Open Data (CC BY 4.0). Model: Huawei Pangu-Weather."


def iso(value: datetime) -> str:
    if value.tzinfo is None:
        raise ValueError("Timezone is required.")
    return value.astimezone(UTC).isoformat().replace("+00:00", "Z")


def utc_time(value: str) -> datetime:
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamp must include timezone.")
    return parsed.astimezone(UTC)


def atomic_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2, allow_nan=False)
        os.replace(name, path)
    finally:
        Path(name).unlink(missing_ok=True)


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def read_stations(path: Path) -> list[dict]:
    stations, seen = [], set()
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"station_id", "latitude", "longitude"}.issubset(reader.fieldnames or []):
            raise ValueError("stations CSV requires station_id, latitude, longitude.")
        for row in reader:
            station_id = int(row["station_id"])
            lat, lon = float(row["latitude"]), float(row["longitude"])
            if station_id <= 0 or station_id in seen:
                raise ValueError("Station IDs must be positive and unique.")
            if not (math.isfinite(lat) and math.isfinite(lon) and -90 <= lat <= 90 and -180 <= lon <= 180):
                raise ValueError(f"Invalid station coordinates: {station_id}")
            stations.append({"station_id": station_id,
                             "station_name": (row.get("station_name") or str(station_id)).strip(),
                             "latitude": lat, "longitude": lon})
            seen.add(station_id)
    if not stations:
        raise ValueError("No stations found; blank coordinates are not silently removed.")
    return stations


def now_utc() -> datetime:
    return datetime.now(UTC)


def initialization_cutoff(now: datetime) -> datetime:
    """Today's 09 KST must be a positive forecast lead, not the input field."""
    yesterday = now.astimezone(KST).date() - timedelta(days=1)
    return datetime.combine(yesterday, time(), UTC)


def sample_grid(field, latitude: float, longitude: float) -> float:
    """Bilinear interpolation on the global north-to-south periodic grid."""
    if tuple(field.shape) != SURFACE_SHAPE[1:]:
        raise ValueError("Unexpected global grid shape.")
    if not (math.isfinite(latitude) and math.isfinite(longitude)
            and -90 <= latitude <= 90 and -180 <= longitude <= 180):
        raise ValueError("Invalid location.")
    height, width = field.shape
    y = (90 - latitude) / (180 / (height - 1))
    x = (longitude % 360) / (360 / width)
    i0, j0 = int(math.floor(y)), int(math.floor(x)) % width
    i1, j1 = min(i0 + 1, height - 1), (j0 + 1) % width
    wy, wx = y - i0, x - math.floor(x)
    value = ((1-wy) * ((1-wx)*float(field[i0, j0]) + wx*float(field[i0, j1]))
             + wy * ((1-wx)*float(field[i1, j0]) + wx*float(field[i1, j1])))
    if not math.isfinite(value):
        raise ValueError("Nonfinite interpolated value.")
    return value


def surface_weather(surface, latitude: float, longitude: float) -> dict:
    mslp, u, v, kelvin = [sample_grid(field, latitude, longitude) for field in surface]
    if not 100 < kelvin < 400 or mslp <= 0:
        raise ValueError("Invalid temperature or mean sea-level pressure.")
    speed = math.hypot(u, v)
    # Meteorological FROM direction: N=0, E=90, S=180, W=270.
    direction = None if speed < 0.05 else (180 + math.degrees(math.atan2(u, v))) % 360
    return {"temperature_c": round(kelvin - 273.15, 3),
            "wind_speed_ms": round(speed, 3),
            "wind_direction_deg": None if direction is None else round(direction, 2) % 360,
            "is_calm": direction is None, "sea_level_pressure_hpa": round(mslp / 100, 3)}
