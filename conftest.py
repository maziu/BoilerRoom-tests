import pytest
from modbus_server import ModbusServer
import modbus_server as t
import defaults

@pytest.fixture(scope="session")
def server():
    with ModbusServer() as s:
        yield s


@pytest.fixture(autouse=True)
def reset(server):
    print(" Reset to default state")
    server.setParameter(t.Param.P_IGNITION_TIME_105, defaults.P_IGNITION_TIME_105)
    server.setParameter(t.Param.P_FAN_TIME_MIN_106, defaults.P_FAN_TIME_MIN_106)
    server.setParameter(t.Param.P_FAN_TEMP_MAX_107, t.Temp(defaults.P_FAN_TEMP_MAX_107))
    server.setParameter(t.Param.P_FAN_TEMP_MIN_108, t.Temp(defaults.P_FAN_TEMP_MIN_108))
    server.setParameter(t.Param.P_FAN_TIME_KEEP_109, defaults.P_FAN_TIME_KEEP_109)
    server.setParameter(t.Param.P_PUMP_TEMP_ON_111, t.Temp(defaults.P_PUMP_TEMP_ON_111))
    server.setParameter(t.Param.P_PUMP_TEMP_OFF_112, t.Temp(defaults.P_PUMP_TEMP_OFF_112))
    server.setParameter(t.Param.P_CWU_TEMP_ON_114, t.Temp(defaults.P_CWU_TEMP_ON_114))
    server.setParameter(t.Param.P_CWU_TEMP_OFF_115, t.Temp(defaults.P_CWU_TEMP_OFF_115))
    server.setParameter(t.Param.P_CWU_INTEGR_TEMP_DIFF_ON_116, t.Temp(defaults.P_CWU_INTEGR_TEMP_DIFF_ON_116))
    server.setParameter(t.Param.P_CWU_INTEGR_TEMP_DIFF_OFF_117, t.Temp(defaults.P_CWU_INTEGR_TEMP_DIFF_OFF_117))
    
    server.setPLCReset()
    yield
