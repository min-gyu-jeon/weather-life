"""Synthetic grids and tiny workers only; no real GPU/model/download calls."""
import json
from pathlib import Path
import subprocess
import sys
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi.testclient import TestClient

from pangu_service import auto_update, pipeline, storage, core
from pangu_service.api import create_app
from pangu_service.locking import exclusive_lock

NOW = core.utc_time('2026-10-16T07:00:00Z')
INIT = core.utc_time('2026-10-15T00:00:00Z')
KEY = 'synthetic-auto-update-key'


@pytest.fixture
def updater(tmp_path, monkeypatch):
    monkeypatch.setattr(auto_update, 'now_utc', lambda: NOW)
    monkeypatch.setattr(pipeline, 'now_utc', lambda: NOW)
    monkeypatch.setattr(storage, 'now_utc', lambda: NOW)
    monkeypatch.setattr(storage, 'SURFACE_SHAPE', (4, 3, 4))
    monkeypatch.setattr(core, 'SURFACE_SHAPE', (4, 3, 4))
    monkeypatch.setattr(auto_update, 'latest_eligible_initialization', lambda source: INIT)
    model = tmp_path / 'synthetic-model.onnx'
    model.write_bytes(b'Not a real model; never execute.')
    return auto_update.AutomaticUpdater(tmp_path, model, tmp_path / 'stations.csv')


def publish_fake(updater, initialization=INIT, kelvin=280):
    surfaces = []
    for day in range(1, 5):
        array = np.empty((4, 3, 4), dtype=np.float32)
        array[:] = np.array([101325, 3, 4, kelvin + day])[:, None, None]
        path = updater.data_dir / f'test_surface_{day}.npy'
        np.save(path, array)
        surfaces.append((day * 24, path))
    metadata = {'forecast_init_utc': core.iso(initialization), 'days': 4,
                'model_sha256': updater.model_hash(), 'device_requested': 'cuda',
                'model_variant': 'SYNTHETIC_TEST_ONLY', 'input_source': 'SYNTHETIC_TEST_ONLY'}
    return storage.publish(updater.data_dir, metadata, surfaces)


def test_startup_predicts_and_restart_does_not_duplicate(updater, monkeypatch):
    calls = []
    def worker(initialization):
        calls.append(initialization)
        publish_fake(updater, initialization)
    monkeypatch.setattr(updater, 'run_worker', worker)
    assert updater.check_once() is True
    assert updater.check_once() is False
    restarted = auto_update.AutomaticUpdater(updater.data_dir, updater.model, updater.stations)
    monkeypatch.setattr(restarted, 'run_worker', lambda _: pytest.fail('duplicate GPU run'))
    assert restarted.check_once() is False
    assert calls == [INIT]


def test_new_daily_initialization_is_used_after_busy_run(updater, monkeypatch):
    calls = []
    current = [NOW]
    newest = [INIT]
    monkeypatch.setattr(auto_update, 'now_utc', lambda: current[0])
    monkeypatch.setattr(auto_update, 'latest_eligible_initialization', lambda _: newest[0])
    def worker(initialization):
        calls.append(initialization)
        publish_fake(updater, initialization)
        if len(calls) == 1:
            current[0] = core.utc_time('2026-10-16T15:01:00Z')  # KST midnight passed
            newest[0] = core.utc_time('2026-10-16T00:00:00Z')
    monkeypatch.setattr(updater, 'run_worker', worker)
    assert updater.check_once()
    assert updater.check_once()
    assert calls == [INIT, core.utc_time('2026-10-16T00:00:00Z')]


def test_worker_failure_keeps_previous_results_and_retries(updater, monkeypatch):
    old = publish_fake(updater, INIT - core.timedelta(days=1))
    attempts = []
    def fail(initialization):
        attempts.append(initialization)
        raise RuntimeError('simulated CUDA failure')
    monkeypatch.setattr(updater, 'run_worker', fail)
    for _ in range(2):
        with pytest.raises(RuntimeError, match='simulated CUDA'):
            updater.run(once=True)
    assert attempts == [INIT, INIT]
    assert [r['manifest']['run_id'] for r in storage.list_runs(updater.data_dir)] == [old]
    state = json.loads((updater.data_dir/'auto_update_status.json').read_text())
    assert state['state'] == 'stopped' and 'simulated CUDA' in state['last_error']


def test_zero_exit_without_output_is_not_success(updater, monkeypatch):
    monkeypatch.setattr(updater, 'run_worker', lambda _: None)
    with pytest.raises(RuntimeError, match='without a verified complete'):
        updater.check_once()


def test_missing_or_corrupt_output_is_recomputed(updater, monkeypatch):
    run_id = publish_fake(updater)
    (updater.data_dir/'forecasts'/run_id/'surface_24.npy').unlink()
    calls = []
    monkeypatch.setattr(updater, 'run_worker', lambda init: (calls.append(init), publish_fake(updater, init)))
    assert updater.check_once()
    assert calls == [INIT]


def test_api_picks_new_complete_run_without_server_restart(updater):
    publish_fake(updater, INIT - core.timedelta(days=1), kelvin=270)
    app = create_app(updater.data_dir, KEY, clock=lambda: NOW)
    with TestClient(app) as client:
        params = {'latitude': 37.5, 'longitude': 127}
        headers = {'X-API-Key': KEY}
        old = client.get('/v1/forecasts', params=params, headers=headers).json()
        new_id = publish_fake(updater, kelvin=280)
        new = client.get('/v1/forecasts', params=params, headers=headers).json()
        assert new['run_id'] == new_id and old['run_id'] != new_id
        assert len(new['forecasts']) == 3
        assert new['forecasts'][0]['temperature_c'] != old['forecasts'][0]['temperature_c']
        assert [p['lead_hours'] for p in new['forecasts']] == [24, 48, 72]


def test_status_endpoint_is_authenticated_and_reports_stale(updater):
    updater.write_status('waiting')
    with TestClient(create_app(updater.data_dir, KEY, clock=lambda: NOW)) as client:
        assert client.get('/v1/update-status').status_code == 401
        state = client.get('/v1/update-status', headers={'X-API-Key': KEY}).json()
        assert state['state'] == 'waiting' and state['status_is_stale'] is False
    with TestClient(create_app(updater.data_dir, KEY,
                              clock=lambda: NOW + core.timedelta(hours=2))) as client:
        assert client.get('/v1/update-status', headers={'X-API-Key': KEY}).json()['status_is_stale']


def test_latest_is_capped_for_same_initialization_daily_policy(monkeypatch):
    calls = []
    class Client:
        def __init__(self, **kwargs):
            self.session = SimpleNamespace(head=lambda *a, **kw: kw)
        def latest(self, **kwargs):
            calls.append(kwargs)
            assert self.session.head('test')['timeout'] == (10, 30)
            return NOW.replace(hour=0, tzinfo=None)
    import ecmwf.opendata
    monkeypatch.setattr(ecmwf.opendata, 'Client', Client)
    monkeypatch.setattr(pipeline, 'now_utc', lambda: NOW)
    assert pipeline.latest_eligible_initialization('ecmwf') == INIT
    assert calls == [{'time': 0, 'step': 0, 'type': 'fc', 'stream': 'oper'}]


def test_lock_excludes_other_process_and_releases_after_exit(tmp_path):
    lock_path = tmp_path/'test.lock'
    code = '''from pathlib import Path
from pangu_service.locking import exclusive_lock
import sys
try:
    with exclusive_lock(Path(sys.argv[1])):
        pass
except RuntimeError:
    raise SystemExit(9)
'''
    command = [sys.executable, '-c', code, str(lock_path)]
    with exclusive_lock(lock_path):
        assert subprocess.run(command, timeout=10).returncode == 9
    assert subprocess.run(command, timeout=10).returncode == 0


def test_gpu_only_worker_uses_locked_exact_date(updater):
    command = updater.worker_command(INIT)
    assert command[command.index('--device') + 1] == 'cuda'
    assert command[command.index('--date') + 1] == '20261015'
    assert '--low-memory' not in command


def test_manual_pipeline_cli_respects_same_work_lock(tmp_path):
    command = [sys.executable, '-m', 'pangu_service.pipeline', 'fetch', '--data-dir', str(tmp_path)]
    with exclusive_lock(tmp_path/'pipeline.lock'):
        result = subprocess.run(command, capture_output=True, text=True, timeout=15)
    assert result.returncode != 0
    assert 'already running' in result.stderr
    assert not (tmp_path/'inputs').exists()


def test_second_updater_refused_before_any_source_check(updater, monkeypatch):
    monkeypatch.setattr(auto_update, 'latest_eligible_initialization', lambda _: pytest.fail('must not check source'))
    with exclusive_lock(updater.data_dir/'auto_update.lock'):
        with pytest.raises(RuntimeError, match='already running'):
            updater.run(once=True)


def test_timeout_kills_only_tiny_test_worker(updater, monkeypatch):
    updater.worker_timeout = 0.1
    monkeypatch.setattr(updater, 'worker_command', lambda _: [sys.executable, '-c', 'import time; time.sleep(30)'])
    with pytest.raises(TimeoutError):
        updater.run_worker(INIT)


def test_model_change_invalidates_previous_success(updater):
    publish_fake(updater)
    assert updater.completed_run(INIT)
    updater.model.write_bytes(b'Different fake model content')
    assert updater.completed_run(INIT) is None


def test_no_success_marker_required_after_crash(updater):
    run_id = publish_fake(updater)
    assert not (updater.data_dir/'last_success.json').exists()
    assert updater.completed_run(INIT)['run_id'] == run_id
