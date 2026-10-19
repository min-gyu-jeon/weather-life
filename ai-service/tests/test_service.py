"""Synthetic fixtures only. These temperatures are not real Pangu forecasts."""
import json
import sys
from datetime import timedelta
from pathlib import Path
from types import SimpleNamespace

import numpy as np
import pytest
from fastapi.testclient import TestClient

from pangu_service import core, pipeline, storage
from pangu_service.api import create_app

KEY = 'synthetic-test-key-only'
NOW = core.utc_time('2026-10-15T07:00:00Z')


@pytest.fixture(autouse=True)
def small_grids(monkeypatch):
    for module in (core, pipeline, storage):
        monkeypatch.setattr(module, 'SURFACE_SHAPE', (4, 3, 4))
    monkeypatch.setattr(pipeline, 'UPPER_SHAPE', (5, 13, 3, 4))
    monkeypatch.setattr(pipeline, 'now_utc', lambda: NOW)
    monkeypatch.setattr(storage, 'now_utc', lambda: NOW)


def make_run(root, init='2026-10-14T00:00:00Z', days=4, kelvin=280):
    source = root / ('source_' + str(kelvin) + init[:10]); source.mkdir(exist_ok=True)
    surfaces = []
    for day in range(1, days+1):
        array = np.empty(core.SURFACE_SHAPE, dtype=np.float32)
        array[:] = np.array([101300, 3, 4, kelvin + day])[:, None, None]
        path = source / f'{day}.npy'; np.save(path, array)
        surfaces.append((24 * day, path))
    meta = {'forecast_init_utc': init, 'days': days, 'input_source': 'SYNTHETIC_TEST',
            'model_variant': 'SYNTHETIC_TEST', 'model_sha256': '0'*64}
    return storage.publish(root, meta, surfaces), meta, surfaces


def client_for(root, clock=lambda: NOW):
    station = root/'stations.csv'
    station.write_text('station_id,latitude,longitude\n400,37.5,127\n', encoding='utf-8')
    return TestClient(create_app(root, KEY, station_csv=station, clock=clock))


def test_api_coordinates_and_station_contract(tmp_path):
    make_run(tmp_path)
    with client_for(tmp_path) as client:
        params = {'latitude': 37.5, 'longitude': 127}
        assert client.get('/v1/forecasts', params=params).status_code == 401
        response = client.get('/v1/forecasts', params=params, headers={'X-API-Key': KEY})
        assert response.status_code == 200
        data = response.json()
        assert data['today_kst'] == '2026-10-15'
        assert [p['day'] for p in data['forecasts']] == ['today', 'tomorrow', 'day_after_tomorrow']
        assert [p['date'] for p in data['forecasts']] == ['2026-10-15', '2026-10-16', '2026-10-17']
        assert [p['lead_hours'] for p in data['forecasts']] == [24, 48, 72]
        assert [p['temperature_c'] for p in data['forecasts']] == pytest.approx([7.85, 8.85, 9.85], abs=.001)
        assert all(p['wind_speed_ms'] == 5 for p in data['forecasts'])
        assert all(p['wind_direction_deg'] == pytest.approx(216.87) for p in data['forecasts'])
        assert all(p['sea_level_pressure_hpa'] == 1013 for p in data['forecasts'])
        assert all(p['valid_time_kst'].endswith('09:00:00+09:00') for p in data['forecasts'])
        assert [p['is_past_valid_time'] for p in data['forecasts']] == [True, False, False]
        assert response.headers['Cache-Control'] == 'no-store'
        station_result = client.get('/v1/forecasts', params={'station_id': 400}, headers={'X-API-Key': KEY})
        assert station_result.json()['forecasts'] == data['forecasts']
        assert station_result.json()['location']['station_id'] == 400
        assert client.get('/health').json()['storage'] == 'files'
        assert client.get('/v1/stations', headers={'X-API-Key': KEY}).json()[0]['station_id'] == 400
        assert client.get('/v1/availability', headers={'X-API-Key': KEY}).json()['today_window_available']
        schema = client.get('/openapi.json').json()
        assert schema['info']['version'] == '2.0.0'
        assert schema['components']['securitySchemes']['APIKeyHeader']['name'] == 'X-API-Key'
        assert {p['name'] for p in schema['paths']['/v1/forecasts']['get']['parameters']} == {'latitude','longitude','station_id'}
    assert not list(tmp_path.rglob('*.sqlite*'))


@pytest.mark.parametrize('params,status', [
    ({}, 422), ({'latitude': 37.5}, 422), ({'longitude': 127}, 422),
    ({'latitude': 91, 'longitude': 127}, 422), ({'latitude': 37.5, 'longitude': 181}, 422),
    ({'latitude': 'NaN', 'longitude': 127}, 422), ({'latitude': 37.5, 'longitude': 'inf'}, 422),
    ({'station_id': 400, 'latitude': 37.5, 'longitude': 127}, 422),
    ({'station_id': -1}, 422), ({'station_id': 999}, 404),
    ({'station_id': 400, 'start_date': '2026-10-15'}, 422),
])
def test_location_validation(tmp_path, params, status):
    make_run(tmp_path)
    with client_for(tmp_path) as client:
        assert client.get('/v1/forecasts', params=params, headers={'X-API-Key': KEY}).status_code == status


def test_no_fake_data_and_csv_independent_of_predictions(tmp_path):
    with client_for(tmp_path) as client:
        assert client.get('/health').status_code == 503
        assert client.get('/v1/stations', headers={'X-API-Key': KEY}).status_code == 200
        assert client.get('/v1/forecasts', params={'station_id': 400}, headers={'X-API-Key': KEY}).status_code == 503


def test_kst_midnight_rollover_not_utc_midnight(tmp_path):
    make_run(tmp_path, init='2026-10-13T00:00:00Z')
    for instant, expected in [('2026-10-14T14:59:59Z', '2026-10-14'), ('2026-10-14T15:00:00Z', '2026-10-15')]:
        with client_for(tmp_path, lambda value=instant: core.utc_time(value)) as client:
            data = client.get('/v1/forecasts', params={'station_id':400}, headers={'X-API-Key':KEY}).json()
            assert data['today_kst'] == expected
            assert data['forecasts'][0]['date'] == expected


def test_single_complete_run_no_lead_zero_or_mixed_initialization(tmp_path):
    old, _, _ = make_run(tmp_path)
    make_run(tmp_path, init='2026-10-15T00:00:00Z', kelvin=290)
    selected = storage.find_window(storage.list_runs(tmp_path), NOW.astimezone(core.KST).date())
    assert selected['manifest']['run_id'] == old
    assert [p['lead_hours'] for p in selected['points']] == [24,48,72]


def test_stale_run_cannot_be_relabelled_today(tmp_path):
    make_run(tmp_path, init='2026-10-10T00:00:00Z')
    with client_for(tmp_path) as client:
        assert client.get('/health').status_code == 503
        response=client.get('/v1/forecasts',params={'station_id':400},headers={'X-API-Key':KEY})
        assert response.status_code == 404
        assert response.json()['detail']['code'] == 'TODAY_WINDOW_NOT_AVAILABLE'


def test_incomplete_publish_keeps_previous_success_and_hides_staging(tmp_path):
    old, meta, surfaces = make_run(tmp_path)
    with pytest.raises(ValueError, match='Incomplete'):
        storage.publish(tmp_path, meta, surfaces[:-1])
    assert [r['manifest']['run_id'] for r in storage.list_runs(tmp_path)] == [old]
    hidden = tmp_path/'forecasts'/'.pending-crashed'; hidden.mkdir()
    (hidden/'manifest.json').write_text('not json')
    assert len(storage.list_runs(tmp_path)) == 1


@pytest.mark.parametrize('corruption', ['missing', 'checksum', 'manifest'])
def test_corrupt_files_return_503(tmp_path, corruption):
    run, _, _ = make_run(tmp_path)
    folder = tmp_path/'forecasts'/run
    if corruption == 'missing':
        (folder/'surface_24.npy').unlink()
    elif corruption == 'checksum':
        with (folder/'surface_24.npy').open('ab') as f: f.write(b'broken')
    else:
        manifest=json.loads((folder/'manifest.json').read_text());manifest['points'][0]['file']='../../outside.npy'
        core.atomic_json(folder/'manifest.json',manifest)
    with client_for(tmp_path) as client:
        assert client.get('/v1/forecasts',params={'station_id':400},headers={'X-API-Key':KEY}).status_code==503


@pytest.mark.parametrize('u,v,direction', [(0,-1,0),(-1,0,90),(0,1,180),(1,0,270),(0,0,None)])
def test_wind_from_direction_and_units(u,v,direction):
    surface=np.empty(core.SURFACE_SHAPE)
    surface[:]=np.array([101325,u,v,293.15])[:,None,None]
    result=core.surface_weather(surface,37.5,127)
    assert result['temperature_c']==20
    assert result['sea_level_pressure_hpa']==1013.25
    assert result['wind_direction_deg']==direction
    assert result['is_calm']==(direction is None)


def test_bilinear_longitude_wrap_poles_and_vector_interpolation():
    field=np.tile(np.array([0,2,4,6]),(3,1))
    assert core.sample_grid(field,0,-45)==3
    assert core.sample_grid(field,90,180)==core.sample_grid(field,90,-180)==4
    assert core.sample_grid(field,-90,45)==1
    surface=np.empty(core.SURFACE_SHAPE)
    surface[:]=np.array([100000,0,-1,280])[:,None,None]
    surface[1,:,0]=-.01; surface[1,:,1]=.01
    assert core.surface_weather(surface,0,45)['wind_direction_deg']==0


def setup_pipeline(root):
    folder=root/'inputs'/'fixture';folder.mkdir(parents=True)
    np.save(folder/'input_upper.npy', np.ones(pipeline.UPPER_SHAPE,dtype=np.float32))
    surface=np.empty(pipeline.SURFACE_SHAPE,dtype=np.float32)
    surface[:]=np.array([101300,3,4,280])[:,None,None]
    np.save(folder/'input_surface.npy',surface)
    core.atomic_json(folder/'metadata.json',{'forecast_init_utc':'2026-10-14T00:00:00Z',
        'pressure_levels_hpa':core.LEVELS,'input_source':'SYNTHETIC_TEST',
        'input_upper_sha256':core.sha256(folder/'input_upper.npy'),
        'input_surface_sha256':core.sha256(folder/'input_surface.npy')})
    core.atomic_json(root/'latest_input.json',{'input_dir':'inputs/fixture'})
    model=root/'synthetic.onnx';model.write_bytes(b'NOT_A_REAL_MODEL_TEST_ONLY')
    return model,folder


def test_pipeline_full_recurrence_and_file_publication(tmp_path,monkeypatch):
    model,_=setup_pipeline(tmp_path)
    received=[]
    class Session:
        def __init__(self,*a,**kw):pass
        def get_providers(self):return ['CPUExecutionProvider']
        def disable_fallback(self):pass
        def get_inputs(self):return [SimpleNamespace(name='input'),SimpleNamespace(name='input_surface')]
        def run(self,names,inputs):
            received.append((float(inputs['input'][0,0,0,0]),float(inputs['input_surface'][3,0,0])))
            return [inputs['input']+1,inputs['input_surface']+1]
    monkeypatch.setitem(sys.modules,'onnxruntime',SimpleNamespace(SessionOptions=SimpleNamespace,InferenceSession=Session))
    pipeline.predict(tmp_path,model,tmp_path/'not-needed.csv',4,'cpu')
    assert received==[(1,280),(2,281),(3,282),(4,283)]
    runs=storage.list_runs(tmp_path)
    assert len(runs)==1 and len(runs[0]['manifest']['points'])==4
    assert not list(tmp_path.rglob('*.sqlite*'))
    with client_for(tmp_path) as client:
        data=client.get('/v1/forecasts',params={'latitude':37.5,'longitude':127},headers={'X-API-Key':KEY}).json()
        assert [p['temperature_c'] for p in data['forecasts']]==pytest.approx([7.85,8.85,9.85],abs=.001)


def test_pipeline_failed_step_never_publishes_partial_run(tmp_path,monkeypatch):
    old,_,_=make_run(tmp_path)
    model,_=setup_pipeline(tmp_path)
    class Session:
        def __init__(self,*a,**kw):self.count=0
        def get_providers(self):return ['CPUExecutionProvider']
        def disable_fallback(self):pass
        def get_inputs(self):return [SimpleNamespace(name='input'),SimpleNamespace(name='input_surface')]
        def run(self,names,inputs):
            self.count+=1
            if self.count==2:raise RuntimeError('synthetic failure')
            return [inputs['input']+1,inputs['input_surface']+1]
    monkeypatch.setitem(sys.modules,'onnxruntime',SimpleNamespace(SessionOptions=SimpleNamespace,InferenceSession=Session))
    with pytest.raises(RuntimeError,match='synthetic failure'):
        pipeline.predict(tmp_path,model,tmp_path/'missing.csv',4,'cpu')
    assert [r['manifest']['run_id'] for r in storage.list_runs(tmp_path)]==[old]


def test_today_input_rejected_before_model_load(tmp_path,monkeypatch):
    model,folder=setup_pipeline(tmp_path)
    meta=json.loads((folder/'metadata.json').read_text());meta['forecast_init_utc']='2026-10-15T00:00:00Z'
    core.atomic_json(folder/'metadata.json',meta)
    monkeypatch.setitem(sys.modules,'onnxruntime',SimpleNamespace())
    with pytest.raises(ValueError,match='cannot cover today'):
        pipeline.predict(tmp_path,model,tmp_path/'missing.csv',4,'cpu')


def test_fetch_uses_yesterday_when_today_initialization_is_published(tmp_path,monkeypatch):
    folder=tmp_path/'inputs'/'20261014T00Z';folder.mkdir(parents=True)
    for name in ['input_upper','input_surface']:np.save(folder/f'{name}.npy',np.zeros(1))
    core.atomic_json(folder/'metadata.json',{'forecast_init_utc':'2026-10-14T00:00:00Z',
        **{f'{name}_sha256':core.sha256(folder/f'{name}.npy') for name in ['input_upper','input_surface']}})
    class Client:
        def __init__(self,**kwargs):pass
        def latest(self,**kwargs):return core.utc_time('2026-10-15T00:00:00Z')
    monkeypatch.setitem(sys.modules,'ecmwf.opendata',SimpleNamespace(Client=Client))
    assert pipeline.fetch(tmp_path,'ecmwf')==folder
    with pytest.raises(ValueError,match='yesterday or earlier'):
        pipeline.fetch(tmp_path,'ecmwf','20261015')


def test_station_csv_validation(tmp_path):
    path=tmp_path/'stations.csv'
    path.write_text('station_id,latitude,longitude\n400,37,127\n400,38,128\n')
    with pytest.raises(ValueError):core.read_stations(path)
    path.write_text('station_id,latitude,longitude\n400,,127\n')
    with pytest.raises(ValueError):core.read_stations(path)


def test_grib_reader_requires_all_fields(tmp_path, monkeypatch):
    monkeypatch.setattr(pipeline, 'SURFACE_SHAPE', (4,721,1440))
    monkeypatch.setattr(pipeline, 'UPPER_SHAPE', (5,13,721,1440))
    import eccodes as ec
    gid=ec.codes_grib_new_from_samples('regular_ll_sfc_grib2')
    try:
        for key,value in {'Ni':1440,'Nj':721,'latitudeOfFirstGridPointInDegrees':90,
            'latitudeOfLastGridPointInDegrees':-90,'longitudeOfFirstGridPointInDegrees':0,
            'longitudeOfLastGridPointInDegrees':359.75,'iDirectionIncrementInDegrees':.25,
            'jDirectionIncrementInDegrees':.25,'jScansPositively':0,'iScansNegatively':0,
            'dataDate':20261014,'dataTime':0,'step':0,'paramId':167}.items():ec.codes_set(gid,key,value)
        ec.codes_set_values(gid,np.full(721*1440,280.))
        with (tmp_path/'fixture.grib2').open('wb') as f:ec.codes_write(gid,f)
    finally:ec.codes_release(gid)
    with pytest.raises(ValueError,match='Missing Pangu input fields'):
        pipeline.read_grib([tmp_path/'fixture.grib2'],core.utc_time('2026-10-14T00:00:00Z'))


def test_coordinate_request_does_not_require_station_csv(tmp_path):
    make_run(tmp_path)
    with TestClient(create_app(tmp_path, KEY, station_csv=tmp_path/'missing.csv', clock=lambda:NOW)) as client:
        assert client.get('/v1/forecasts', params={'latitude':37.5,'longitude':127}, headers={'X-API-Key':KEY}).status_code==200
        assert client.get('/v1/stations', headers={'X-API-Key':KEY}).status_code==503


def test_input_checksum_fails_before_inference(tmp_path,monkeypatch):
    model,folder=setup_pipeline(tmp_path)
    with (folder/'input_surface.npy').open('ab') as f:f.write(b'corrupt')
    monkeypatch.setitem(sys.modules,'onnxruntime',SimpleNamespace())
    with pytest.raises(ValueError,match='Corrupt input'):
        pipeline.predict(tmp_path,model,tmp_path/'missing.csv',4,'cpu')


def test_bad_allocation_preserves_existing_run(tmp_path,monkeypatch):
    old,_,_=make_run(tmp_path)
    model,_=setup_pipeline(tmp_path)
    def fail(*a,**kw):raise RuntimeError('bad allocation')
    monkeypatch.setitem(sys.modules,'onnxruntime',SimpleNamespace(SessionOptions=SimpleNamespace,InferenceSession=fail))
    with pytest.raises(RuntimeError,match='No forecast was published'):
        pipeline.predict(tmp_path,model,tmp_path/'missing.csv',4,'cpu')
    assert [r['manifest']['run_id'] for r in storage.list_runs(tmp_path)]==[old]


def test_file_export_can_be_served_without_model_or_input(tmp_path,monkeypatch):
    from pangu_service import export_files
    source=tmp_path/'producer';source.mkdir()
    make_run(source)
    destination=tmp_path/'consumer'
    monkeypatch.setattr(sys,'argv',['export_files','--data-dir',str(source),'--output',str(destination)])
    export_files.main()
    assert not (destination/'inputs').exists()
    with TestClient(create_app(destination,KEY,clock=lambda:NOW)) as client:
        assert client.get('/v1/forecasts',params={'latitude':37.5,'longitude':127},headers={'X-API-Key':KEY}).status_code==200


def test_normalize_grid_orders_latitude_and_longitude():
    lat=np.linspace(-90,90,721)
    lon=np.arange(-180,180,.25)
    values=np.broadcast_to(lat[:,None],(721,1440)).copy()
    result=pipeline.normalize_grid(values,lat,lon)
    assert result.dtype==np.float32
    assert result[0,0]==90 and result[-1,-1]==-90
