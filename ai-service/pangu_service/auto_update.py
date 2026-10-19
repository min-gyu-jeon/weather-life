"""Poll for the next eligible daily input; run one isolated CUDA worker at a time."""
from __future__ import annotations

import argparse
from datetime import datetime
import logging
from logging.handlers import RotatingFileHandler
import math
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

from .core import KST, atomic_json, iso, now_utc, sha256, utc_time
from .locking import exclusive_lock
from .pipeline import latest_eligible_initialization
from .storage import find_window, list_runs, load_surface

LOG = logging.getLogger(__name__)


class AutomaticUpdater:
    def __init__(self, data_dir: Path, model: Path, stations: Path, *, source='ecmwf',
                 days=4, check_interval=600, worker_timeout=7200):
        if not math.isfinite(check_interval) or check_interval < 60:
            raise ValueError('Check interval must be at least 60 seconds.')
        if not math.isfinite(worker_timeout) or worker_timeout < 60:
            raise ValueError('Worker timeout must be at least 60 seconds.')
        if not 3 <= days <= 10:
            raise ValueError('days must be between 3 and 10.')
        self.data_dir = data_dir.resolve()
        self.model = model.resolve()
        self.stations = stations.resolve()
        self.source, self.days = source, days
        self.check_interval, self.worker_timeout = check_interval, worker_timeout
        self.status = {'state': 'starting', 'device': 'cuda',
                       'policy': 'same_initialization_daily_09_kst',
                       'check_interval_seconds': check_interval,
                       'worker_timeout_seconds': worker_timeout}
        self._model_stat = self._model_hash = None

    def write_status(self, state=None, **fields):
        self.status.update(fields)
        if state:
            self.status['state'] = state
        self.status['updated_at_utc'] = iso(now_utc())
        atomic_json(self.data_dir / 'auto_update_status.json', self.status)

    def model_hash(self):
        info = self.model.stat()
        identity = (info.st_size, info.st_mtime_ns)
        if identity != self._model_stat:
            self._model_hash = sha256(self.model)
            self._model_stat = identity
        return self._model_hash

    def completed_run(self, initialization: datetime):
        """Use immutable published outputs, not a possibly lost scheduler marker."""
        for run in list_runs(self.data_dir):
            manifest = run['manifest']
            if (utc_time(manifest['forecast_init_utc']) != initialization
                    or manifest['model_sha256'] != self.model_hash()
                    or manifest.get('device_requested') != 'cuda'
                    or manifest['days'] < self.days):
                continue
            # Reject missing/corrupted outputs, so a bad run is retried.
            try:
                for point in manifest['points']:
                    surface = load_surface(run['folder'], point)
                    del surface
            except (OSError, ValueError, KeyError, TypeError):
                continue
            if find_window([run], now_utc().astimezone(KST).date()) is not None:
                return manifest
        return None

    def worker_command(self, initialization):
        return [sys.executable, '-u', '-m', 'pangu_service.pipeline', 'update',
                '--source', self.source, '--date', initialization.strftime('%Y%m%d'),
                '--data-dir', str(self.data_dir), '--model', str(self.model),
                '--stations', str(self.stations), '--days', str(self.days), '--device', 'cuda']

    def run_worker(self, initialization):
        """GPU worker lifetime is bounded; no CPU fallback, no parallel model sessions."""
        log_path = self.data_dir / 'gpu_worker.log'
        if log_path.exists() and log_path.stat().st_size > 5 * 1024 * 1024:
            log_path.replace(log_path.with_suffix('.log.previous'))
        command = self.worker_command(initialization)
        process = None
        job = dll = None
        try:
            # Kill only our child on updater shutdown/crash, including on Windows.
            if os.name == 'nt':
                import ctypes
                from .guarded_run import kernel, ExtendedLimits, KILL_ON_CLOSE
                dll = kernel()
                job = dll.CreateJobObjectW(None, None)
                if not job:
                    raise ctypes.WinError(ctypes.get_last_error())
                info = ExtendedLimits()
                info.basic.flags = KILL_ON_CLOSE  # GPU: no artificial 4 GiB CPU cap.
                if not dll.SetInformationJobObject(job, 9, ctypes.byref(info), ctypes.sizeof(info)):
                    raise ctypes.WinError(ctypes.get_last_error())
            with log_path.open('ab') as output:
                output.write(f'\n=== {iso(now_utc())} input={iso(initialization)} ===\n'.encode())
                output.flush()
                options = {'creationflags': subprocess.CREATE_NO_WINDOW | subprocess.BELOW_NORMAL_PRIORITY_CLASS} if os.name == 'nt' else {'start_new_session': True}
                process = subprocess.Popen(command, stdout=output, stderr=subprocess.STDOUT,
                                           stdin=subprocess.DEVNULL,
                                           cwd=Path(__file__).resolve().parent.parent,
                                           env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}, **options)
                if job and not dll.AssignProcessToJobObject(job, int(process._handle)):
                    raise RuntimeError('Cannot supervise GPU worker; stopping without unbounded fallback.')
                deadline = time.monotonic() + self.worker_timeout
                heartbeat = time.monotonic()
                while process.poll() is None:
                    if time.monotonic() >= deadline:
                        raise TimeoutError('GPU worker exceeded its time limit; existing predictions were retained.')
                    if time.monotonic() - heartbeat >= 30:
                        self.write_status(worker_pid=process.pid)
                        heartbeat = time.monotonic()
                    time.sleep(0.5)
                if process.returncode:
                    raise RuntimeError(f'GPU worker exited with code {process.returncode}. See data/gpu_worker.log.')
        finally:
            if process is not None and process.poll() is None:
                if os.name != 'nt':
                    os.killpg(process.pid, signal.SIGKILL)
                else:
                    process.kill()
                process.wait(timeout=10)
            if job:
                dll.CloseHandle(job)

    def check_once(self):
        self.write_status('checking', last_error=None, worker_pid=None)
        if not self.model.is_file():
            raise FileNotFoundError('Pangu model missing. Run: python -m pangu_service.download_model')
        self.model_hash()
        initialization = latest_eligible_initialization(self.source)
        self.write_status(last_checked_at_utc=iso(now_utc()),
                          eligible_initialization_utc=iso(initialization))
        completed = self.completed_run(initialization)
        if completed:
            self.write_status('waiting', last_success_init_utc=completed['forecast_init_utc'],
                              last_success_run_id=completed['run_id'])
            LOG.info('Already predicted input %s; no GPU rerun.', iso(initialization))
            return False
        self.write_status('running', worker_initialization_utc=iso(initialization))
        LOG.info('New daily input %s: downloading and starting GPU prediction.', iso(initialization))
        self.run_worker(initialization)
        completed = self.completed_run(initialization)
        if not completed:
            raise RuntimeError('Worker ended without a verified complete forecast. No success was recorded.')
        self.write_status('waiting', worker_pid=None,
                          last_success_init_utc=completed['forecast_init_utc'],
                          last_success_run_id=completed['run_id'])
        LOG.info('Forecast published: %s. API will use it on subsequent requests.', completed['run_id'])
        return True

    def run(self, *, once=False):
        with exclusive_lock(self.data_dir / 'auto_update.lock'):
            self.write_status('starting')
            try:
                while True:
                    try:
                        changed = self.check_once()
                    except Exception as error:
                        LOG.exception('Update failed; keeping earlier forecast files. Retry later.')
                        self.write_status('error', last_error=str(error), worker_pid=None)
                        if once:
                            raise
                        changed = False
                    if once:
                        return
                    # Recheck immediately after a run, catching day rollover while busy.
                    if changed:
                        continue
                    deadline = time.monotonic() + self.check_interval
                    while time.monotonic() < deadline:
                        time.sleep(min(30, max(0, deadline - time.monotonic())))
                        self.write_status()
            finally:
                self.write_status('stopped', worker_pid=None)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data-dir', type=Path, default=Path('data'))
    parser.add_argument('--model', type=Path, default=Path('models/pangu_weather_24.onnx'))
    parser.add_argument('--stations', type=Path, default=Path('stations.csv'))
    parser.add_argument('--source', choices=['ecmwf', 'aws', 'google'], default='ecmwf')
    parser.add_argument('--days', type=int, choices=range(3, 11), default=4)
    parser.add_argument('--check-interval-seconds', type=float, default=600)
    parser.add_argument('--worker-timeout-seconds', type=float, default=7200)
    parser.add_argument('--once', action='store_true', help='Check once, update if needed, then exit.')
    args = parser.parse_args()
    args.data_dir.mkdir(parents=True, exist_ok=True)
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s',
                        handlers=[logging.StreamHandler(), RotatingFileHandler(
                            args.data_dir / 'auto_update.log', maxBytes=2 * 1024 * 1024,
                            backupCount=2, encoding='utf-8')])
    updater = AutomaticUpdater(args.data_dir, args.model, args.stations, source=args.source,
                               days=args.days, check_interval=args.check_interval_seconds,
                               worker_timeout=args.worker_timeout_seconds)
    try:
        updater.run(once=args.once)
    except KeyboardInterrupt:
        LOG.info('Updater stopped by user.')


if __name__ == '__main__':
    main()
