import modbus_server as t
import pytest
import defaults
from time import time, sleep

# FB_ALG_Fan		
# S0: OFF		
# S0 -> S1 rozpalanie gdy X6 przycisk zapalarki wciśnięty		
# S0 -> S3 gdy wcisniety przycisk podtrzymania went.		
# S0: Wyłączone wyjście Wentylator/Fan/200.07		
# S1: Rozpalanie		
# S1 -> S0 Licznik timBoilerStart liczy, jeśli doliczy P_FanTimeMin(106) to do S0		
# S1 -> S2 praca wył. gdy TempBoiler(209) > P_FanTempMax (107)		
# S1: Załączone wyjście Wentylator/Fan/200.07		
# S2: Praca went. wył		
# S2 -> S3 TempBoiler(209) < P_FanTempMin(108)		
# S2: Wyłączone wyjście Wentylator/Fan/200.07		
# S3: Praca went. wł		
# S3: Liczymy czas timBoilerKeepalive		
# S3 -> S2 gdy TempBoiler(209) > P_FanTempMax(107)		
# S3 -> S0 gdy timBoilerKeepAlive > P_FanTimeKeep(P109)		
# S3: Załączone wyjście Wentylator/Fan/200.07		

@pytest.mark.parametrize("fan_time_min_s", {5, 15})
def test_fan_alg__ignition_failed(server, fan_time_min_s):
    print("Test fan output during failed ignition")
    server.setParameter(t.Param.P_FAN_TIME_MIN_106, fan_time_min_s)
    server.saveParams()
    server.setTemperature(t.TempSensor.TS_BOILER, 0.75*defaults.P_FAN_TEMP_MAX_107)

    assert not server.getOutput(t.Devices_OUT.DEVO_Fan)
    assert server.getOpmode() == t.OPMODE.OPMODE_Off

    print("start ignition")
    server.setInput(t.Devices_IN.DEVI_BtnLighter)
    server.waitForUpdate()
    server.clrInput(t.Devices_IN.DEVI_BtnLighter)

    assert server.getOpmode() == t.OPMODE.OPMODE_Preheat
    assert server.getOutput(t.Devices_OUT.DEVO_Fan)

    sleep(fan_time_min_s)

    assert not server.getOutput(t.Devices_OUT.DEVO_Fan)
    assert server.getOpmode() == t.OPMODE.OPMODE_Off


# def test_fan_alg__ignition_ok(server):
#     print("Test fan output during correct ignition")
#     fan_time_min_s = 10
#     server.setParameter(t.Param.P_FAN_TIME_MIN_106, fan_time_min_s)
#     server.saveParams()
#     server.setTemperature(t.TempSensor.TS_BOILER, 35.0)  # less thab default P_FAN_TEMP_MAX_107 = 800

#     assert not server.getOutput(t.Devices_OUT.DEVO_Fan)
#     assert server.getOpmode() == t.OPMODE.OPMODE_Off

#     print("start ignition")
#     server.setInput(t.Devices_IN.DEVI_BtnLighter)
#     server.waitForUpdate()
#     server.clrInput(t.Devices_IN.DEVI_BtnLighter)

#     assert server.getOpmode() == t.OPMODE.OPMODE_Preheat
#     assert server.getOutput(t.Devices_OUT.DEVO_Fan)

#     sleep(fan_time_min_s)

#     assert not server.getOutput(t.Devices_OUT.DEVO_Fan)
#     assert server.getOpmode() == t.OPMODE.OPMODE_Off