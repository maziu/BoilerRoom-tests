
from modbus_server import Modbus_ControllableServer, Temp
import modbus_server as t

import pytest
import logging
import random

class TestClass:
    
    xVar = 2
    log = logging.getLogger(__name__)

    @classmethod
    def setup_class(cls):
        cls.log.setLevel(logging.INFO)
        cls.xVar = 3
        cls.log.info("Setting up test env...")
        cls.server = Modbus_ControllableServer(1001, "TCP")
        cls.server.enableTestMode()
        cls.log.info("Done!")

    @classmethod
    def teardown_class(cls):
        cls.log.info("Finalizing tests...")
        cls.server.disableTestMode()
        cls.server.stop_server()
        cls.log.info("Done!")

    @pytest.mark.order(1)
    def test_smoke(self):
        self.log.info("Smoke test: Temperature types")
        t1 = Temp(123)
        assert (float(t1)) == 12.3
        assert (int(t1)) == 123
        t2 = Temp(15.4)
        assert (float(t2)) == 15.4
        assert (int(t2)) == 154
        assert (1+1) == 2
        self.log.info("Smoke test: Connection to PLC enable test mode and check temp setting")
        r = float(random.randint(0, 500))/10
        self.server.setTemperature(t.TempSensor.TS_3D, r)
        self.server.waitForUpdate()
        assert (self.server.getTemperature(t.TempSensor.TS_3D)) == r,  \
                f"Basic get / set temperature test failed, no PLC connection or invalid PLC program"

    def test_base_2(self):
        
        assert (1+2) == 3


if __name__ == "__main__":
    print("Do not execute main please")