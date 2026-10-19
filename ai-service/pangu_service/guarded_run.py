"""Windows CPU worker with a commit-memory limit, headroom checks and timeout.

This module uses only the standard library. No model imports occur before the
parent has attached the worker to a limited Windows Job Object.
"""
from __future__ import annotations

import argparse
import ctypes
from ctypes import wintypes
from dataclasses import dataclass
import math
import os
from pathlib import Path
import runpy
import subprocess
import sys
import tempfile
import time
import uuid

GIB = 1024 ** 3
JOB_MEMORY = 0x200
KILL_ON_CLOSE = 0x2000


class BasicLimits(ctypes.Structure):
    _fields_ = [("process_time", ctypes.c_longlong), ("job_time", ctypes.c_longlong),
                ("flags", wintypes.DWORD), ("min_ws", ctypes.c_size_t),
                ("max_ws", ctypes.c_size_t), ("active", wintypes.DWORD),
                ("affinity", ctypes.c_size_t), ("priority", wintypes.DWORD),
                ("scheduling", wintypes.DWORD)]


class IoCounters(ctypes.Structure):
    _fields_ = [(name, ctypes.c_ulonglong) for name in
                ("read_ops", "write_ops", "other_ops", "read_bytes", "write_bytes", "other_bytes")]


class ExtendedLimits(ctypes.Structure):
    _fields_ = [("basic", BasicLimits), ("io", IoCounters),
                ("process_limit", ctypes.c_size_t), ("job_limit", ctypes.c_size_t),
                ("peak_process", ctypes.c_size_t), ("peak_job", ctypes.c_size_t)]


class MemoryStatus(ctypes.Structure):
    _fields_ = [("length", wintypes.DWORD), ("load", wintypes.DWORD)] + [
        (name, ctypes.c_ulonglong) for name in
        ("total_phys", "avail_phys", "total_commit", "avail_commit", "total_virtual", "avail_virtual", "extended")]


def kernel():
    if sys.platform != "win32":
        raise RuntimeError("This memory guard supports Windows only; it will not run without a limit.")
    dll = ctypes.WinDLL("kernel32", use_last_error=True)
    dll.CreateJobObjectW.argtypes = [ctypes.c_void_p, wintypes.LPCWSTR]
    dll.CreateJobObjectW.restype = wintypes.HANDLE
    dll.OpenJobObjectW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
    dll.OpenJobObjectW.restype = wintypes.HANDLE
    dll.GetCurrentProcess.argtypes = []
    dll.GetCurrentProcess.restype = wintypes.HANDLE
    dll.IsProcessInJob.argtypes = [wintypes.HANDLE, wintypes.HANDLE, ctypes.POINTER(wintypes.BOOL)]
    dll.IsProcessInJob.restype = wintypes.BOOL
    dll.SetInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p, wintypes.DWORD]
    dll.SetInformationJobObject.restype = wintypes.BOOL
    dll.QueryInformationJobObject.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p,
                                             wintypes.DWORD, ctypes.c_void_p]
    dll.QueryInformationJobObject.restype = wintypes.BOOL
    dll.AssignProcessToJobObject.argtypes = [wintypes.HANDLE, wintypes.HANDLE]
    dll.AssignProcessToJobObject.restype = wintypes.BOOL
    dll.CloseHandle.argtypes = [wintypes.HANDLE]
    dll.CloseHandle.restype = wintypes.BOOL
    dll.GlobalMemoryStatusEx.argtypes = [ctypes.POINTER(MemoryStatus)]
    dll.GlobalMemoryStatusEx.restype = wintypes.BOOL
    return dll


def memory_status() -> MemoryStatus:
    state = MemoryStatus()
    state.length = ctypes.sizeof(state)
    if not kernel().GlobalMemoryStatusEx(ctypes.byref(state)):
        raise ctypes.WinError(ctypes.get_last_error())
    return state


def require_cpu_guard(device: str) -> None:
    """Refuse unbounded Windows CPU inference, including direct function calls."""
    if sys.platform != "win32" or device != "cpu":
        return
    if os.environ.get("PANGU_LIMITED_WORKER") != "1":
        raise RuntimeError("Unbounded Windows CPU inference is disabled after the PC freeze. "
                           "Use: python -m pangu_service.guarded_run")
    # An unnamed/null query may select an outer job in a nested launcher environment.
    # Open our exact job and verify both membership and its configured limit.
    name = os.environ.get("PANGU_LIMITED_JOB_NAME")
    if not name:
        raise RuntimeError("No parent job identity; refusing model load.")
    dll = kernel()
    job = dll.OpenJobObjectW(0x0004, False, name)  # JOB_OBJECT_QUERY
    if not job:
        raise RuntimeError("Cannot open the parent memory limit; refusing model load.")
    try:
        belongs = wintypes.BOOL()
        info = ExtendedLimits()
        if (not dll.IsProcessInJob(dll.GetCurrentProcess(), job, ctypes.byref(belongs)) or not belongs.value
                or not dll.QueryInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info), None)):
            raise RuntimeError("Cannot verify the worker memory limit; refusing model load.")
        if not info.basic.flags & JOB_MEMORY or not 0 < info.job_limit <= 4 * GIB:
            raise RuntimeError("No verified Job Object limit of 4 GiB or less; refusing model load.")
    finally:
        dll.CloseHandle(job)


@dataclass
class WorkerResult:
    returncode: int
    reason: str
    output: str


def run_limited(command: list[str], *, limit_bytes: int, timeout_seconds: float,
                reserve_bytes: int = 2 * GIB) -> WorkerResult:
    """Child MUST wait for GO on stdin before importing/loading its workload."""
    if not 0 < limit_bytes <= 4 * GIB or not math.isfinite(timeout_seconds) or timeout_seconds <= 0:
        raise ValueError("Require 0 < limit <= 4 GiB and a positive finite timeout.")
    if reserve_bytes < 0:
        raise ValueError("Invalid reserve.")
    dll = kernel()
    before = memory_status()
    if min(before.avail_phys, before.avail_commit) < limit_bytes + reserve_bytes:
        raise RuntimeError("Not enough free RAM/commit headroom for the selected cap; worker was not started.")
    job_name = "Local\\PanguGuard_" + uuid.uuid4().hex
    job = dll.CreateJobObjectW(None, job_name)
    if not job:
        raise ctypes.WinError(ctypes.get_last_error())
    process = None
    try:
        info = ExtendedLimits()
        info.basic.flags = JOB_MEMORY | KILL_ON_CLOSE
        info.job_limit = limit_bytes
        if not dll.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
            raise ctypes.WinError(ctypes.get_last_error())
        with tempfile.TemporaryFile(mode="w+b") as log:
            environment = dict(os.environ, PANGU_LIMITED_WORKER="1", PANGU_LIMITED_JOB_NAME=job_name,
                               PYTHONUNBUFFERED="1", PYTHONIOENCODING="utf-8")
            process = subprocess.Popen(command, stdin=subprocess.PIPE, stdout=log, stderr=subprocess.STDOUT,
                                       env=environment, creationflags=subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS)
            if not dll.AssignProcessToJobObject(job, wintypes.HANDLE(int(process._handle))):
                raise RuntimeError("Cannot attach the memory cap. The waiting worker will be stopped without loading a model.")
            # A failed limit setup never reaches this handshake.
            process.stdin.write(b"GO\n")
            process.stdin.flush()
            process.stdin.close()
            deadline = time.monotonic() + timeout_seconds
            reason = "exited"
            while process.poll() is None:
                if time.monotonic() >= deadline:
                    reason = "timeout"
                    process.kill()
                    break
                state = memory_status()
                if min(state.avail_phys, state.avail_commit) < reserve_bytes:
                    reason = "low_system_headroom"
                    process.kill()
                    break
                time.sleep(0.1)
            process.wait(timeout=5)
            log.seek(0)
            # Keep only the tail. Large output must not consume parent memory.
            log.seek(max(0, log.seek(0, 2) - 65536))
            output = log.read().decode("utf-8", errors="replace")
            return WorkerResult(process.returncode, reason, output)
    finally:
        if process is not None and process.poll() is None:
            process.kill()
            process.wait(timeout=5)
        if process is not None and process.stdin is not None and not process.stdin.closed:
            process.stdin.close()
        dll.CloseHandle(job)


def main():
    # Worker imports pipeline (and therefore NumPy/ORT later) only after GO.
    if sys.argv[1:2] == ["--_worker"]:
        if sys.stdin.buffer.readline() != b"GO\n":
            raise SystemExit("No parent handshake; model not loaded.")
        require_cpu_guard("cpu")
        sys.argv = ["pangu_service.pipeline", *sys.argv[2:]]
        runpy.run_module("pangu_service.pipeline", run_name="__main__")
        return
    parser = argparse.ArgumentParser(description="Memory-capped Windows CPU Pangu worker. No unbounded fallback.")
    parser.add_argument("--max-memory-gb", type=float, default=4)
    parser.add_argument("--timeout-seconds", type=float, default=120)
    parser.add_argument("--data-dir", type=Path, default=Path("data"))
    parser.add_argument("--model", type=Path, default=Path("models/pangu_weather_24.onnx"))
    parser.add_argument("--days", type=int, choices=range(3, 11), default=4)
    args = parser.parse_args()
    if not math.isfinite(args.max_memory_gb) or not 0 < args.max_memory_gb <= 4:
        parser.error("max-memory-gb must be positive and at most 4; raising the cap is disabled.")
    command = [sys.executable, "-u", "-m", "pangu_service.guarded_run", "--_worker",
               "predict", "--data-dir", str(args.data_dir), "--days", str(args.days),
               "--device", "cpu", "--model", str(args.model)]
    print(f"Starting limited CPU worker: at most {args.max_memory_gb:g} GiB committed memory, "
          f"{args.timeout_seconds:g}s timeout. Full Pangu may not fit; no unbounded fallback.", flush=True)
    try:
        result = run_limited(command, limit_bytes=int(args.max_memory_gb * GIB),
                             timeout_seconds=args.timeout_seconds)
    except (OSError, RuntimeError, ValueError) as error:
        raise SystemExit(f"Limited worker not started / stopped: {error}") from None
    print(result.output, end="")
    print(f"\nWorker finished: {result.reason}; exit={result.returncode}. "
          "A memory-limit failure is not a successful prediction.")
    raise SystemExit(result.returncode or (1 if result.reason != "exited" else 0))


if __name__ == "__main__":
    main()
