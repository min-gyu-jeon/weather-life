"""Synthetic constant GRIB fields; verifies the real 69-field input conversion."""
import numpy as np
import pytest
import eccodes as ec

from pangu_service.core import LEVELS,SURFACE_IDS,UPPER_IDS,utc_time
from pangu_service.pipeline import read_grib


def test_complete_grib_input_variable_and_pressure_order(tmp_path):
    path=tmp_path/'synthetic.grib2'
    constants={151:101325.,165:2.,166:-3.,167:280.,129:100000.,133:.003,130:260.,131:8.,132:-9.}
    fields=[(p,None) for p in reversed(SURFACE_IDS)]
    fields += [(p,lev) for p in reversed(UPPER_IDS) for lev in reversed(LEVELS)]
    with path.open('wb') as handle:
        for pid,lev in fields:
            gid=ec.codes_grib_new_from_samples('regular_ll_pl_grib2' if lev else 'regular_ll_sfc_grib2')
            try:
                settings={'Ni':1440,'Nj':721,'latitudeOfFirstGridPointInDegrees':90,
                          'latitudeOfLastGridPointInDegrees':-90,'longitudeOfFirstGridPointInDegrees':0,
                          'longitudeOfLastGridPointInDegrees':359.75,'iDirectionIncrementInDegrees':.25,
                          'jDirectionIncrementInDegrees':.25,'jScansPositively':0,'iScansNegatively':0,
                          'dataDate':20230101,'dataTime':0,'step':0,'paramId':pid}
                for key,value in settings.items():ec.codes_set(gid,key,value)
                if lev is not None:ec.codes_set(gid,'level',lev)
                # Vary upper temperature by level so pressure ordering is tested as well.
                value=constants[pid]+(lev/10000 if pid==130 and lev else 0)
                ec.codes_set_values(gid,np.full(721*1440,value))
                ec.codes_write(gid,handle)
            finally:ec.codes_release(gid)
    upper,surface=read_grib([path],utc_time('2023-01-01T00:00:00Z'))
    assert upper.shape==(5,13,721,1440) and surface.shape==(4,721,1440)
    assert upper.dtype==surface.dtype==np.float32
    assert surface[:,120,500]==pytest.approx([101325,2,-3,280])
    assert upper[0,0,100,100]==pytest.approx(100000)  # Geopotential must not be multiplied by gravity again.
    assert upper[1,0,100,100]==pytest.approx(.003)
    assert upper[2,:,100,100]==pytest.approx([260+lev/10000 for lev in LEVELS],abs=1e-4)
