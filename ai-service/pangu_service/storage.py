"""Immutable JSON manifests and NumPy surface grids; no database."""
from __future__ import annotations

import json
import shutil
import tempfile
import uuid
from datetime import date, datetime, time, timedelta
from pathlib import Path

import numpy as np

from .core import KST, UTC, SURFACE_SHAPE, atomic_json, iso, now_utc, sha256, utc_time


def validate_manifest(manifest: dict) -> None:
    init = utc_time(manifest["forecast_init_utc"])
    utc_time(manifest["published_at_utc"])
    days = manifest["days"]
    if (manifest["schema_version"] != 2 or not 3 <= days <= 10
            or init != datetime.combine(init.date(), time(), UTC)
            or manifest["surface_shape"] != list(SURFACE_SHAPE)
            or manifest["surface_order"] != ["mslp", "u10", "v10", "t2m"]):
        raise ValueError("Invalid forecast manifest.")
    if len(manifest["points"]) != days:
        raise ValueError("Incomplete forecast run.")
    for day, point in enumerate(manifest["points"], 1):
        lead = 24 * day
        if (point["lead_hours"] != lead or point["file"] != f"surface_{lead}.npy"
                or utc_time(point["valid_time_utc"]) != init + timedelta(hours=lead)
                or len(point["sha256"]) != 64):
            raise ValueError("Invalid forecast point.")
    for key in ("run_id", "input_source", "model_variant", "model_sha256"):
        if not isinstance(manifest[key], str) or not manifest[key]:
            raise ValueError(f"Missing metadata: {key}")


def load_surface(folder: Path, point: dict):
    if point["file"] != f"surface_{int(point['lead_hours'])}.npy":
        raise ValueError("Invalid surface filename.")
    path = folder / point["file"]
    if sha256(path) != point["sha256"]:
        raise ValueError("Surface checksum mismatch.")
    array = np.load(path, allow_pickle=False, mmap_mode="r")
    if array.shape != SURFACE_SHAPE or array.dtype != np.float32:
        raise ValueError("Invalid surface shape/dtype.")
    return array


def publish(data_dir: Path, metadata: dict, surfaces: list[tuple[int, Path]]) -> str:
    """A complete directory becomes visible in one rename; retain older runs."""
    init = utc_time(metadata["forecast_init_utc"])
    run_id = init.strftime("%Y%m%dT%H%MZ") + "_" + uuid.uuid4().hex[:12]
    root = data_dir / "forecasts"
    root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root, prefix=".pending-") as temporary:
        stage = Path(temporary) / "run"
        stage.mkdir()
        points = []
        for lead, source in sorted(surfaces):
            array = np.load(source, allow_pickle=False, mmap_mode="r")
            if array.shape != SURFACE_SHAPE or array.dtype != np.float32 or not np.isfinite(array).all():
                raise ValueError("Invalid model output; run will not be published.")
            del array
            name = f"surface_{lead}.npy"
            shutil.copyfile(source, stage / name)
            points.append({"lead_hours": lead, "valid_time_utc": iso(init + timedelta(hours=lead)),
                           "file": name, "sha256": sha256(stage / name)})
        manifest = {**metadata, "schema_version": 2, "run_id": run_id,
                    "published_at_utc": iso(now_utc()), "surface_shape": list(SURFACE_SHAPE),
                    "surface_order": ["mslp", "u10", "v10", "t2m"], "points": points}
        validate_manifest(manifest)
        atomic_json(stage / "manifest.json", manifest)
        stage.rename(root / run_id)
    return run_id


def list_runs(data_dir: Path) -> list[dict]:
    runs = []
    for path in (data_dir / "forecasts").glob("*/manifest.json"):
        if path.parent.name.startswith("."):
            continue
        manifest = json.loads(path.read_text(encoding="utf-8"))
        validate_manifest(manifest)
        if manifest["run_id"] != path.parent.name:
            raise ValueError("Manifest directory mismatch.")
        runs.append({"folder": path.parent, "manifest": manifest})
    return sorted(runs, key=lambda run: (utc_time(run["manifest"]["forecast_init_utc"]),
                  utc_time(run["manifest"]["published_at_utc"]), run["manifest"]["run_id"]), reverse=True)


def find_window(runs: list[dict], today: date) -> dict | None:
    required = {today + timedelta(days=i) for i in range(3)}
    for run in runs:
        points = [point for point in run["manifest"]["points"]
                  if utc_time(point["valid_time_utc"]).astimezone(KST).date() in required]
        if len(points) == 3:
            return {**run, "points": points}
    return None
