"""Read precomputed Pangu file snapshots; HTTP requests never run inference."""
from __future__ import annotations

import os
import json
import secrets
from contextlib import asynccontextmanager
from datetime import date, datetime
from pathlib import Path
from typing import Annotated, Callable, Literal

from fastapi import Depends, FastAPI, HTTPException, Query, Request, Response
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader
from pydantic import BaseModel

from .core import ATTRIBUTION, KST, now_utc, read_stations, surface_weather, utc_time
from .storage import find_window, list_runs, load_surface


class Location(BaseModel):
    latitude: float
    longitude: float
    station_id: int | None = None
    station_name: str | None = None


class ForecastPoint(BaseModel):
    day: Literal["today", "tomorrow", "day_after_tomorrow"]
    date: date
    valid_time_kst: datetime
    lead_hours: int
    temperature_c: float
    wind_speed_ms: float
    wind_direction_deg: float | None
    is_calm: bool
    sea_level_pressure_hpa: float
    is_past_valid_time: bool


class ForecastResponse(BaseModel):
    model: Literal["Pangu-Weather"] = "Pangu-Weather"
    run_id: str
    location: Location
    today_kst: date
    days: Literal[3] = 3
    timezone: Literal["Asia/Seoul"] = "Asia/Seoul"
    daily_time: Literal["09:00"] = "09:00"
    forecast_init_utc: datetime
    published_at_utc: datetime
    input_source: str
    model_variant: str
    model_sha256: str
    initialization_age_hours: float
    forecasts: list[ForecastPoint]
    attribution: str = ATTRIBUTION


def create_app(data_dir: Path | None = None, api_key: str | None = None,
               station_csv: Path | None = None,
               clock: Callable[[], datetime] = now_utc) -> FastAPI:
    root = (data_dir or Path(os.environ.get("PANGU_DATA_DIR", "data"))).resolve()
    station_file = (station_csv or Path(os.environ.get("PANGU_STATIONS_CSV", "stations.csv"))).resolve()

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        key = api_key if api_key is not None else os.environ.get("PANGU_API_KEY", "")
        if len(key) < 16:
            raise RuntimeError("Set PANGU_API_KEY to a random string with at least 16 characters.")
        app.state.api_key = key
        yield

    app = FastAPI(title="Pangu today/tomorrow/day-after forecast API", version="2.0.0", lifespan=lifespan,
                  description="No database. Returns three 09:00 KST predictions from one saved initialization. "
                              "Choose latitude/longitude OR station_id. No inference runs in HTTP requests.")
    header = APIKeyHeader(name="X-API-Key", auto_error=False)

    def authorize(key: str | None = Depends(header)):
        if key is None or not secrets.compare_digest(key.encode(), app.state.api_key.encode()):
            raise HTTPException(status_code=401, detail="Missing or invalid X-API-Key")

    def stations():
        try:
            return read_stations(station_file)
        except (OSError, ValueError, KeyError):
            raise HTTPException(status_code=503, detail="Station CSV unavailable or invalid.") from None

    def runs():
        try:
            result = list_runs(root)
        except (OSError, ValueError, KeyError, TypeError):
            raise HTTPException(status_code=503, detail="Forecast files are invalid or unreadable.") from None
        if not result:
            raise HTTPException(status_code=503, detail="No published forecast files. Run pipeline update first.")
        return result

    def window_for(today):
        window = find_window(runs(), today)
        if window is None:
            raise HTTPException(status_code=404, detail={"code": "TODAY_WINDOW_NOT_AVAILABLE",
                "message": "No single saved run covers today, tomorrow and the day after at 09 KST. Run pipeline update.",
                "today_kst": today.isoformat()})
        return window

    @app.get("/health", tags=["health"])
    def health():
        today = clock().astimezone(KST).date()
        try:
            window = window_for(today)
            for point in window["points"]:
                if not (window["folder"] / point["file"]).is_file():
                    raise HTTPException(status_code=503)
        except HTTPException:
            return JSONResponse(status_code=503, content={"status": "not_ready", "today_kst": today.isoformat()})
        return {"status": "ready", "today_kst": today, "storage": "files",
                "forecast_init_utc": window["manifest"]["forecast_init_utc"]}

    @app.get("/v1/stations", response_model=list[Location], dependencies=[Depends(authorize)])
    def station_list():
        return stations()

    @app.get("/v1/availability", dependencies=[Depends(authorize)])
    def availability():
        now = clock()
        today = now.astimezone(KST).date()
        saved = runs()
        return {"today_kst": today, "timezone": "Asia/Seoul", "daily_time": "09:00", "days": 3,
                "today_window_available": find_window(saved, today) is not None,
                "runs": [{"run_id": r["manifest"]["run_id"],
                          "forecast_init_utc": r["manifest"]["forecast_init_utc"],
                          "valid_dates": [utc_time(p["valid_time_utc"]).astimezone(KST).date()
                                          for p in r["manifest"]["points"]]} for r in saved]}

    @app.get("/v1/update-status", dependencies=[Depends(authorize)])
    def update_status():
        path = root / "auto_update_status.json"
        if not path.exists():
            return {"state": "not_started", "message": "Start start_auto_update.py in another terminal."}
        try:
            state = json.loads(path.read_text(encoding="utf-8"))
            checked = utc_time(state["updated_at_utc"])
            interval = float(state["check_interval_seconds"])
        except (OSError, ValueError, KeyError, TypeError):
            raise HTTPException(status_code=503, detail="Updater status unreadable.") from None
        stale = (clock() - checked).total_seconds() > max(180, interval * 2)
        return {**state, "status_is_stale": stale}

    @app.get("/v1/forecasts", response_model=ForecastResponse, dependencies=[Depends(authorize)])
    def forecasts(request: Request, response: Response,
                  latitude: Annotated[float | None, Query(ge=-90, le=90, allow_inf_nan=False)] = None,
                  longitude: Annotated[float | None, Query(ge=-180, le=180, allow_inf_nan=False)] = None,
                  station_id: Annotated[int | None, Query(gt=0)] = None):
        if "start_date" in request.query_params:
            raise HTTPException(status_code=422, detail="start_date was removed in v2; dates are today/tomorrow/day-after in KST.")
        if station_id is not None:
            if latitude is not None or longitude is not None:
                raise HTTPException(status_code=422, detail="Choose station_id OR latitude and longitude.")
            location = next((s for s in stations() if s["station_id"] == station_id), None)
            if location is None:
                raise HTTPException(status_code=404, detail="Unknown station_id.")
        elif latitude is None or longitude is None:
            raise HTTPException(status_code=422, detail="Provide both latitude and longitude, or station_id.")
        else:
            location = {"latitude": latitude, "longitude": longitude}
        now = clock()
        today = now.astimezone(KST).date()
        window = window_for(today)
        manifest = window["manifest"]
        points = []
        try:
            for label, point in zip(("today", "tomorrow", "day_after_tomorrow"), window["points"]):
                surface = load_surface(window["folder"], point)
                weather = surface_weather(surface, location["latitude"], location["longitude"])
                del surface
                valid = utc_time(point["valid_time_utc"])
                points.append({"day": label, "date": valid.astimezone(KST).date(),
                    "valid_time_kst": valid.astimezone(KST), "lead_hours": point["lead_hours"],
                    "is_past_valid_time": valid < now, **weather})
        except (OSError, ValueError, KeyError, TypeError):
            raise HTTPException(status_code=503, detail="Forecast surface files are missing or invalid.") from None
        response.headers["Cache-Control"] = "no-store"
        return {"run_id": manifest["run_id"], "location": location, "today_kst": today,
                "forecast_init_utc": manifest["forecast_init_utc"], "published_at_utc": manifest["published_at_utc"],
                "input_source": manifest["input_source"], "model_variant": manifest["model_variant"],
                "model_sha256": manifest["model_sha256"],
                "initialization_age_hours": round((now-utc_time(manifest["forecast_init_utc"])).total_seconds()/3600, 2),
                "forecasts": points}

    return app


app = create_app()
