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

def assert_state_off(server):
    assert server.getOpmode() == t.OPMODE.OPMODE_Off
    assert not server.getOutput(t.Devices_OUT.DEVO_Fan)

def assert_state_preheat(server):
    assert server.getOpmode() == t.OPMODE.OPMODE_Preheat
    assert server.getOutput(t.Devices_OUT.DEVO_Fan)

def assert_state_fan_off(server):
    assert server.getOpmode() == t.OPMODE.OPMODE_FanOff
    assert not server.getOutput(t.Devices_OUT.DEVO_Fan)

def assert_state_fan_on(server):
    assert server.getOpmode() == t.OPMODE.OPMODE_FanOn
    assert server.getOutput(t.Devices_OUT.DEVO_Fan)


@pytest.mark.parametrize("fan_time_min_s", {5, 15})
def test_fan_alg__ignition_failed(server, fan_time_min_s):
    print("Test fan output during failed ignition")
    server.setParameter(t.Param.P_FAN_TIME_MIN_106, fan_time_min_s)
    server.saveParams()
    server.setTemperature(t.TempSensor.TS_BOILER, 0.75*defaults.P_FAN_TEMP_MAX_107)

    assert_state_off(server)

    print("start ignition")
    server.setInput(t.Devices_IN.DEVI_BtnLighter)
    server.waitForUpdate()
    server.clrInput(t.Devices_IN.DEVI_BtnLighter)

    assert_state_preheat(server)
    sleep(fan_time_min_s)
    assert_state_off(server)


def test_fan_alg__ignition_ok_fan_hysteresis(server):
    print("Test fan output during correct ignition")
    fan_time_min_s = 10
    server.setParameter(t.Param.P_FAN_TIME_MIN_106, fan_time_min_s)
    server.saveParams()
    server.setTemperature(t.TempSensor.TS_BOILER, 0.75*defaults.P_FAN_TEMP_MAX_107)

    assert_state_off(server)

    print("Start ignition")
    server.setInput(t.Devices_IN.DEVI_BtnLighter)
    server.waitForUpdate()
    server.clrInput(t.Devices_IN.DEVI_BtnLighter)

    assert_state_preheat(server)

    sleep(fan_time_min_s/2)
    print("Heat up")
    server.setTemperature(t.TempSensor.TS_BOILER, 1.25*defaults.P_FAN_TEMP_MAX_107)
    server.waitForUpdate()
    assert_state_fan_off(server)

    print("Cool down")
    server.setTemperature(t.TempSensor.TS_BOILER, 0.75*defaults.P_FAN_TEMP_MIN_108)
    server.waitForUpdate()
    assert_state_fan_on(server)

    print("Heat up")
    server.setTemperature(t.TempSensor.TS_BOILER, 1.25*defaults.P_FAN_TEMP_MAX_107)
    server.waitForUpdate()
    assert_state_fan_off(server)


@pytest.mark.parametrize("time_keep_s", {5, 15})
def test_fan_alg__time_keep_alive(server, time_keep_s):
    print("Test fan keep alive")
    fan_time_min_s = 10
    server.setParameter(t.Param.P_FAN_TIME_MIN_106, fan_time_min_s)
    server.setParameter(t.Param.P_FAN_TIME_KEEP_109, time_keep_s)
    server.saveParams()
    server.setTemperature(t.TempSensor.TS_BOILER, 0.75*defaults.P_FAN_TEMP_MAX_107)

    assert_state_off(server)

    print("Start ignition")
    server.setInput(t.Devices_IN.DEVI_BtnLighter)
    server.waitForUpdate()
    server.clrInput(t.Devices_IN.DEVI_BtnLighter)

    assert_state_preheat(server)

    sleep(fan_time_min_s/2)
    print("Heat up")
    server.setTemperature(t.TempSensor.TS_BOILER, 1.25*defaults.P_FAN_TEMP_MAX_107)
    server.waitForUpdate()
    assert_state_fan_off(server)

    print("Cool down")
    server.setTemperature(t.TempSensor.TS_BOILER, 0.75*defaults.P_FAN_TEMP_MIN_108)
    server.waitForUpdate()
    assert_state_fan_on(server)

    sleep(time_keep_s)
    print("Time keep passed")
    assert_state_off(server)


def test_fan_alg__keep_fan_button_and_reeignite(server):
    print("Test keep fan button and reignite")
    time_keep_s = 5
    server.setParameter(t.Param.P_FAN_TIME_KEEP_109, time_keep_s)
    server.saveParams()
    server.setTemperature(t.TempSensor.TS_BOILER, 0.75*defaults.P_FAN_TEMP_MAX_107)

    assert_state_off(server)

    print("Start ignition")
    server.setFlag(t.Flags.FLAG_FanKeepalive)
    server.waitForUpdate()
    server.clrFlag(t.Flags.FLAG_FanKeepalive)

    assert_state_fan_on(server)

    server.waitForUpdate()
    print("Heat up")
    server.setTemperature(t.TempSensor.TS_BOILER, 1.25*defaults.P_FAN_TEMP_MAX_107)
    server.waitForUpdate()
    assert_state_fan_off(server)

    print("Cool down")
    server.setTemperature(t.TempSensor.TS_BOILER, 0.75*defaults.P_FAN_TEMP_MIN_108)
    server.waitForUpdate()
    assert_state_fan_on(server)

    sleep(time_keep_s)
    print("Time keep passed")
    assert_state_off(server)