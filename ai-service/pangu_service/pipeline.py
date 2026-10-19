"""ECMWF IFS -> Pangu 24h recurrence -> immutable daily surface files."""
from __future__ import annotations

import argparse
import json
import logging
import os
import tempfile
from datetime import datetime, timedelta
from pathlib import Path
from time import perf_counter

import numpy as np

from .core import (ATTRIBUTION, LEVELS, SURFACE_IDS, UPPER_IDS, SURFACE_SHAPE,
                   UPPER_SHAPE, UTC, KST, atomic_json, initialization_cutoff, iso, now_utc,
                   read_stations, sha256, utc_time)
from .storage import publish
from .locking import exclusive_lock

LOG = logging.getLogger(__name__)


def normalize_grid(values, latitudes, longitudes):
    """Normalize axes, without inventing missing grid points or levels."""
    lat_order = np.argsort(latitudes)[::-1]
    lon_order = np.argsort(np.asarray(longitudes) % 360)
    lat = np.asarray(latitudes)[lat_order]
    lon = (np.asarray(longitudes) % 360)[lon_order]
    if not (np.allclose(lat, np.linspace(90, -90, 721), atol=1e-5)
            and np.allclose(lon, np.arange(1440)*0.25, atol=1e-5)):
        raise ValueError("Input must cover the complete global 0.25-degree grid, including both poles.")
    return np.ascontiguousarray(values[np.ix_(lat_order, lon_order)], dtype=np.float32)


def read_grib(paths: list[Path], init: datetime):
    import eccodes as ec
    surface = np.empty(SURFACE_SHAPE, dtype=np.float32)
    upper = np.empty(UPPER_SHAPE, dtype=np.float32)
    expected = {(pid, None) for pid in SURFACE_IDS} | {(pid, lev) for pid in UPPER_IDS for lev in LEVELS}
    seen = set()
    units_allowed = {
        151: {"Pa"}, 165: {"ms**-1", "ms-1"}, 166: {"ms**-1", "ms-1"}, 167: {"K"},
        129: {"m**2s**-2", "m2s-2"}, 133: {"kgkg**-1", "kgkg-1"},
        130: {"K"}, 131: {"ms**-1", "ms-1"}, 132: {"ms**-1", "ms-1"},
    }
    for path in paths:
        with path.open("rb") as handle:
            while True:
                gid = ec.codes_grib_new_from_file(handle)
                if gid is None:
                    break
                try:
                    pid = int(ec.codes_get(gid, "paramId"))
                    level_type = ec.codes_get(gid, "typeOfLevel")
                    lev = int(ec.codes_get(gid, "level")) if level_type == "isobaricInhPa" else None
                    key = pid, lev
                    if key not in expected:
                        raise ValueError(f"Unexpected field in downloaded subset: {key}")
                    if key in seen:
                        raise ValueError(f"Duplicate field: {key}")
                    stamp = str(ec.codes_get(gid, "dataDate")) + f"{int(ec.codes_get(gid, 'dataTime')):04d}"
                    if stamp != init.strftime("%Y%m%d%H%M") or int(ec.codes_get(gid, "endStep")) != 0:
                        raise ValueError("Mixed initialization or a nonzero input forecast step.")
                    unit = str(ec.codes_get(gid, "units")).replace(" ", "")
                    if unit not in units_allowed[pid]:
                        raise ValueError(f"Unexpected units for parameter {pid}: {unit}. Do not guess conversions.")
                    if (ec.codes_get(gid, "gridType") != "regular_ll"
                        or int(ec.codes_get(gid, "Ni")) != 1440
                        or int(ec.codes_get(gid, "Nj")) != 721
                        or int(ec.codes_get(gid, "jPointsAreConsecutive"))
                        or int(ec.codes_get(gid, "alternativeRowScanning"))):
                        raise ValueError("Unsupported GRIB grid or scan mode.")
                    if int(ec.codes_get(gid, "numberOfMissing")):
                        raise ValueError(f"Missing grid values in field {key}.")
                    di = float(ec.codes_get(gid, "iDirectionIncrementInDegrees"))
                    dj = float(ec.codes_get(gid, "jDirectionIncrementInDegrees"))
                    lat0 = float(ec.codes_get(gid, "latitudeOfFirstGridPointInDegrees"))
                    lon0 = float(ec.codes_get(gid, "longitudeOfFirstGridPointInDegrees"))
                    lat = lat0 + np.arange(721)*dj*(1 if ec.codes_get(gid,"jScansPositively") else -1)
                    lon = lon0 + np.arange(1440)*di*(-1 if ec.codes_get(gid,"iScansNegatively") else 1)
                    values = np.asarray(ec.codes_get_values(gid)).reshape(721,1440)
                    values = normalize_grid(values,lat,lon)
                    if not np.isfinite(values).all():
                        raise ValueError(f"Nonfinite input field: {key}")
                    if lev is None:
                        surface[SURFACE_IDS.index(pid)] = values
                    else:
                        upper[UPPER_IDS.index(pid),LEVELS.index(lev)] = values
                    seen.add(key)
                finally:
                    ec.codes_release(gid)
    missing = expected - seen
    if missing:
        raise ValueError(f"Missing Pangu input fields/levels: {sorted(missing, key=str)}. No interpolation was applied.")
    return upper, surface


def latest_eligible_initialization(source: str) -> datetime:
    """Newest published 00 UTC input that keeps all three dates on one run."""
    from ecmwf.opendata import Client
    client = Client(source=source, model="ifs", resol="0p25", infer_stream_keyword=False,
                    maximum_retries=3, retry_after=10)
    head = client.session.head

    def bounded_head(*args, **kwargs):
        kwargs.setdefault("timeout", (10, 30))
        return head(*args, **kwargs)

    client.session.head = bounded_head
    latest = client.latest(time=0, step=0, type="fc", stream="oper")
    latest = latest.replace(tzinfo=UTC) if latest.tzinfo is None else latest.astimezone(UTC)
    if latest.hour or latest.minute or latest.second or latest.microsecond:
        raise ValueError("Expected a published 00 UTC initialization.")
    return min(latest, initialization_cutoff(now_utc()))


def fetch(data_dir: Path, source: str, requested_date: str | None = None) -> Path:
    from ecmwf.opendata import Client
    data_dir = data_dir.resolve()
    client = Client(source=source, model="ifs", resol="0p25", infer_stream_keyword=False,
                    maximum_retries=3, retry_after=10)
    request = dict(time=0, step=0, type="fc", stream="oper")
    cutoff = initialization_cutoff(now_utc())
    if requested_date:
        init = datetime.strptime(requested_date, "%Y%m%d").replace(tzinfo=UTC)
        if init > cutoff:
            raise ValueError("To include today at 09 KST, --date must be yesterday or earlier (KST calendar date).")
    else:
        latest = client.latest(**request)
        # ECMWF client returns naive UTC, explicitly documented by its API.
        latest = latest.replace(tzinfo=UTC) if latest.tzinfo is None else latest.astimezone(UTC)
        init = min(latest, cutoff)
    if init.hour != 0:
        raise ValueError("Expected the latest published 00 UTC run.")
    target = data_dir / "inputs" / init.strftime("%Y%m%dT00Z")
    target.parent.mkdir(parents=True, exist_ok=True)
    if not target.exists():
        request.update(date=init.strftime("%Y%m%d"))  # Lock both requests to ONE initialization.
        with tempfile.TemporaryDirectory(dir=target.parent, prefix="fetch_") as folder:
            stage = Path(folder)/"ready"
            stage.mkdir()
            paths = [stage/"surface.grib2",stage/"upper.grib2"]
            client.retrieve(**request, levtype="sfc", param=["msl","10u","10v","2t"], target=str(paths[0]))
            client.retrieve(**request, levtype="pl", param=["z","q","t","u","v"],
                            levelist=LEVELS, target=str(paths[1]))
            upper, surface = read_grib(paths, init)
            np.save(stage/"input_upper.npy",upper,allow_pickle=False)
            np.save(stage/"input_surface.npy",surface,allow_pickle=False)
            metadata = {"forecast_init_utc":iso(init), "input_source":"ECMWF_IFS_OPEN_DATA_STEP0",
                        "download_source":source, "fetched_at_utc":iso(datetime.now(UTC)),
                        "surface_order":["mslp","u10","v10","t2m"],
                        "upper_order":["geopotential","specific_humidity","temperature","u","v"],
                        "pressure_levels_hpa":LEVELS, "attribution":ATTRIBUTION,
                        "input_upper_sha256":sha256(stage/"input_upper.npy"),
                        "input_surface_sha256":sha256(stage/"input_surface.npy")}
            atomic_json(stage/"metadata.json", metadata)
            stage.rename(target)
    # Validate reused snapshots as well, before updating the pointer.
    metadata = json.loads((target/"metadata.json").read_text(encoding="utf-8"))
    if utc_time(metadata["forecast_init_utc"]) != init:
        raise ValueError("Existing input directory has a mismatched initialization.")
    for name in ["input_upper", "input_surface"]:
        if sha256(target/f"{name}.npy") != metadata[f"{name}_sha256"]:
            raise ValueError(f"Input checksum mismatch: {name}; use a new data directory to refetch.")
    atomic_json(data_dir/"latest_input.json", {"input_dir":str(target.relative_to(data_dir))})
    LOG.info("Input ready: %s; target is daily 09 KST.", iso(init))
    return target


def predict(data_dir: Path, model: Path, station_csv: Path, days: int, device: str) -> str:
    import onnxruntime as ort
    started = perf_counter()
    data_dir = data_dir.resolve()
    pointer = json.loads((data_dir/"latest_input.json").read_text(encoding="utf-8"))
    folder = (data_dir/pointer["input_dir"]).resolve()
    if not folder.is_relative_to(data_dir):
        raise ValueError("Input directory must be inside data-dir.")
    metadata = json.loads((folder/"metadata.json").read_text(encoding="utf-8"))
    init = utc_time(metadata["forecast_init_utc"])
    if (init.hour != 0 or init.minute or init.second or init.microsecond
            or metadata["pressure_levels_hpa"] != LEVELS):
        raise ValueError("Unexpected initial time or pressure-level order.")
    today = now_utc().astimezone(KST).date()
    last_date = (init + timedelta(days=days)).astimezone(KST).date()
    if init > initialization_cutoff(now_utc()) or last_date < today + timedelta(days=2):
        raise ValueError("Input/horizon cannot cover today, tomorrow and day-after at 09 KST. "
                         "Run fetch again and use --days 4 (or a longer horizon for older input).")
    if not 3 <= days <= 10:
        raise ValueError("days must be between 3 and 10.")
    if station_csv.is_file():
        read_stations(station_csv)
        metadata["station_csv_sha256"] = sha256(station_csv)
    for name in ["input_upper", "input_surface"]:
        if sha256(folder/f"{name}.npy") != metadata[f"{name}_sha256"]:
            raise ValueError(f"Corrupt input: {name}")
    upper = np.load(folder/"input_upper.npy", allow_pickle=False, mmap_mode="r")
    surface = np.load(folder/"input_surface.npy", allow_pickle=False, mmap_mode="r")
    if upper.shape != UPPER_SHAPE or surface.shape != SURFACE_SHAPE:
        raise ValueError("Pangu input shape mismatch.")
    if upper.dtype != np.float32 or surface.dtype != np.float32:
        raise ValueError("Pangu input must be float32.")
    if not (np.isfinite(upper).all() and np.isfinite(surface).all()):
        raise ValueError("Nonfinite model input.")
    providers = ["CPUExecutionProvider"]
    if device == "cuda":
        # cuDNN loads additional engine DLLs during the first convolution.
        # Keep their directories active for the entire inference session.
        dll_directories = []
        if os.name == "nt":
            nvidia = Path(ort.__file__).resolve().parent.parent / "nvidia"
            bins = list(nvidia.glob("*/bin"))
            dll_directories = [os.add_dll_directory(str(p)) for p in bins]
            os.environ["PATH"] = os.pathsep.join(map(str, bins)) + os.pathsep + os.environ.get("PATH", "")
        if hasattr(ort, "preload_dlls"):
            ort.preload_dlls(directory="")
        if "CUDAExecutionProvider" not in ort.get_available_providers():
            raise RuntimeError("CUDAExecutionProvider unavailable. Install a compatible GPU runtime or choose --device cpu.")
        providers = [("CUDAExecutionProvider", {
            "arena_extend_strategy": "kSameAsRequested",
            "cudnn_conv_algo_search": "HEURISTIC",
            "cudnn_conv_use_max_workspace": "0",
        })]
    options = ort.SessionOptions()
    options.enable_cpu_mem_arena = False
    options.enable_mem_pattern = False
    options.enable_mem_reuse = False
    options.intra_op_num_threads = 1
    LOG.info("Initializing Pangu model on %s", device)
    try:
        session = ort.InferenceSession(str(model.resolve()), sess_options=options, providers=providers)
    except Exception as error:
        if "bad allocation" in str(error).lower():
            raise RuntimeError("Pangu initialization could not allocate memory. No forecast was published. "
                               "Free memory or use a machine with sufficient RAM/GPU memory.") from error
        raise
    if device == "cuda" and "CUDAExecutionProvider" not in session.get_providers():
        raise RuntimeError("GPU session was not established; refusing silent CPU fallback.")
    session.disable_fallback()
    LOG.info("Model ready; execution providers: %s", session.get_providers())
    if {i.name for i in session.get_inputs()} != {"input", "input_surface"}:
        raise ValueError("This is not the expected official Pangu 24h model.")
    model_hash = sha256(model)
    timings = []
    with tempfile.TemporaryDirectory(dir=data_dir, prefix="predict_") as temporary:
        surfaces = []
        for day in range(1, days+1):
            step_started = perf_counter()
            LOG.info("Starting forecast step +%sh", 24 * day)
            # Both complete state tensors feed the next step, including upper air.
            output = session.run(None, {"input": np.ascontiguousarray(upper),
                                        "input_surface": np.ascontiguousarray(surface)})
            if len(output) != 2:
                raise ValueError("Unexpected Pangu output count.")
            upper, surface = output
            del output
            if upper.shape != UPPER_SHAPE or surface.shape != SURFACE_SHAPE:
                raise ValueError("Pangu output order/shape mismatch.")
            if upper.dtype != np.float32 or surface.dtype != np.float32:
                raise ValueError("Unexpected Pangu output dtype.")
            if not (np.isfinite(upper).all() and np.isfinite(surface).all()):
                raise ValueError("Nonfinite output; run will not be published.")
            lead = 24 * day
            path = Path(temporary)/f"surface_{lead}.npy"
            np.save(path, surface, allow_pickle=False)
            surfaces.append((lead, path))
            timings.append({"lead_hours": lead, "inference_and_save_seconds": perf_counter()-step_started})
            LOG.info("Completed +%sh, %s", lead, (init+timedelta(hours=lead)).astimezone(KST).isoformat())
        metadata.update({"model": "Pangu-Weather", "model_variant": "official_pangu_weather_24.onnx",
                         "model_sha256": model_hash, "days": days, "device_requested": device,
                         "onnxruntime_providers": session.get_providers(), "timings": timings,
                         "total_predict_seconds": perf_counter()-started,
                         "inference_completed_at_utc": iso(now_utc())})
        run_id = publish(data_dir, metadata, surfaces)
    atomic_json(data_dir/"last_success.json", {"run_id": run_id, **metadata})
    LOG.info("Published run %s; %s daily global surface grids (no database)", run_id, days)
    return run_id


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command",choices=["fetch","predict","update"])
    parser.add_argument("--data-dir",type=Path,default=Path("data"))
    parser.add_argument("--source",choices=["ecmwf","aws","google"],default="ecmwf")
    parser.add_argument("--date",help="Optional initialization date YYYYMMDD, always 00 UTC; must still be available.")
    parser.add_argument("--model",type=Path,default=Path("models/pangu_weather_24.onnx"))
    parser.add_argument("--stations",type=Path,default=Path("stations.csv"))
    parser.add_argument("--days",type=int,choices=range(3,11),default=4,
                        help="Model steps; 4 covers three response days plus a midnight rollover buffer.")
    parser.add_argument("--device",choices=["cpu","cuda"],default="cpu")
    args=parser.parse_args()
    logging.basicConfig(level=logging.INFO,format="%(asctime)s %(levelname)s %(message)s")
    # Manual CLI runs and the automatic GPU worker share the same data lock.
    with exclusive_lock(args.data_dir.resolve() / "pipeline.lock"):
        if args.command in {"fetch","update"}:
            fetch(args.data_dir,args.source,args.date)
        if args.command in {"predict","update"}:
            predict(args.data_dir,args.model,args.stations,args.days,args.device)


if __name__ == "__main__":
    main()
