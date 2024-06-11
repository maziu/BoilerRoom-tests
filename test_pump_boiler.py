import modbus_server as t
import pytest
import defaults
from time import time, sleep

# POMPA KOTLA FB_ALG_PumpBoiler
# Wyjście 200.08 / PBoiler / Pompa Kotla
# Czujnik temperatury kotła TempBoiler (209)
# Parametr Temp. zal. pompy D111 P_PumpTempOn
# Parametr temp. wyl. pompy D112 P_PumpTempOff
# Wyjscie zał gdy TempBoiler(209) > P_PumpTempOn(111)
# Wyjscie wył gdy TempBoiler(209) < P_PumpTempOff(112)

def assert_state_off(server):
    assert server.getOutput(t.Devices_OUT.DEVO_PBoiler) == False

def assert_state_on(server):
    assert server.getOutput(t.Devices_OUT.DEVO_PBoiler)


@pytest.mark.parametrize("P_PumpTempOn, P_PumpTempOff", [(defaults.P_PUMP_TEMP_ON_111, defaults.P_PUMP_TEMP_OFF_112), 
                                                         (72, 83), 
                                                         (44, 51)])

def test_pump_boiler(server, P_PumpTempOn, P_PumpTempOff):
    print("Test Pump Boiler with default parameters")
    #Starting temp under lower limit
    server.setTemperature(t.TempSensor.TS_BOILER, 0.5*P_PumpTempOff)
    server.saveParams()
    server.waitForUpdate()
    assert_state_off()
    #Go between the limits, should be off
    server.setTemperature(t.TempSensor.TS_BOILER, P_PumpTempOff+0.2)
    server.waitForUpdate()
    assert_state_off()
    server.setTemperature(t.TempSensor.TS_BOILER, P_PumpTempOn-0.2)
    server.waitForUpdate()
    assert_state_off()
    #Go over upper limit, should be on
    server.setTemperature(t.TempSensor.TS_BOILER, P_PumpTempOn+0.2)
    server.waitForUpdate()
    assert_state_on()
    # Now test histeresis, go between the limits, should be ON
    server.setTemperature(t.TempSensor.TS_BOILER, P_PumpTempOn-0.2)
    server.waitForUpdate()
    assert_state_off()
    server.setTemperature(t.TempSensor.TS_BOILER, P_PumpTempOff+0.2)
    server.waitForUpdate()
    assert_state_off()
    #Finally go under low limit, should be OFF
    server.setTemperature(t.TempSensor.TS_BOILER, P_PumpTempOff-0.2)
    server.waitForUpdate()
    assert_state_off()
    