
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
        cls.server = Modbus_ControllableServer("COM3", "Serial")
        cls.server.enableTestMode()
        cls.log.info("Done!")

    @classmethod
    def teardown_class(cls):
        cls.log.info("Finalizing tests...")
        cls.server.disableTestMode()
        cls.server.stop_server()
        cls.log.info("Done!")

    @pytest.mark.order(0)
    def test_self(self):
        self.log.info("Self-testing test system")
        self.server.setRegister(t.TestReg.REG_TEST, 0x1234)
        assert 0x1234 == self.server.getRegister(t.TestReg.REG_TEST)
        self.server.setRegister(t.TestReg.REG_TEST, 0)
        assert 0 == self.server.getRegister(t.TestReg.REG_TEST)
        self.server.setBitInRegister(t.TestReg.REG_TEST, 3)
        assert 0x08 == self.server.getRegister(t.TestReg.REG_TEST) # 4th bit set
        self.server.setRegister(t.TestReg.REG_TEST, 0xAAAA)
        self.server.setBitInRegister(t.TestReg.REG_TEST, 1, False)
        assert 0xAAA8 == self.server.getRegister(t.TestReg.REG_TEST) # 2nd bit cleared
        self.server.setRegister(t.TestReg.REG_TEST, 0xAAAA)
        self.server.clrBitInRegister(t.TestReg.REG_TEST, 1)
        assert 0xAAA8 == self.server.getRegister(t.TestReg.REG_TEST) # 2nd bit cleared
        assert False == self.server.getBitInRegister(t.TestReg.REG_TEST, 2)
        assert True == self.server.getBitInRegister(t.TestReg.REG_TEST, 3)
        self.server.setRegister(t.TestReg.REG_TEST, 0)
        self.log.info("Self-test: Temperature types")
        t1 = Temp(123)
        assert (float(t1)) == 12.3
        assert (int(t1)) == 123
        t2 = Temp(15.4)
        assert (float(t2)) == 15.4
        assert (int(t2)) == 154
        assert (1+1) == 2
        

    @pytest.mark.order(1)
    def test_smoke(self):
        self.log.info("Smoke test: Connection to PLC enable test mode and check temp setting")
        r = float(random.randint(0, 500))/10
        self.server.setTemperature(t.TempSensor.TS_3D, r)
        self.server.waitForUpdate()
        assert (self.server.getTemperature(t.TempSensor.TS_3D)) == r,  \
                f"Basic get / set temperature test failed, no PLC connection or invalid PLC program"
        self.server.waitForUpdate()


    def test_ctrlmode(self):
        self.log.info("Test: Control mode and manual command from HMI")
        self.server.setRegister(t.HMIWrite.REG_MODE, 0xFFFF) #Control all from HMI 
        self.server.setRegister(t.HMIWrite.REG_CMD, 0x0000)
        self.log.info("Set all outputs OFF")
        self.server.waitForUpdate()
        self.log.info("Check results")
        assert self.server.getRegister(t.HMIRead.REG_DeviceStatus) == 0x0000
        self.server.waitForUpdate()
        self.server.setBitInRegister(t.HMIWrite.REG_MODE, t.Devices_OUT.DEVO_Belimo1)
        self.server.setBitInRegister(t.HMIWrite.REG_CMD, t.Devices_OUT.DEVO_Belimo1)
        self.log.info("Set belimo to ON")
        self.server.waitForUpdate()
        self.log.info("Get results")
        assert self.server.getBitInRegister(t.HMIRead.REG_DeviceStatus, t.Devices_OUT.DEVO_Belimo1) == 1
        self.log.info("Get disable all outputs")
        self.server.setRegister(t.HMIWrite.REG_MODE, 0xFFFF) #Control all from HMI 
        self.server.setRegister(t.HMIWrite.REG_CMD, 0x0000)
        self.server.waitForUpdate()
        self.log.info("Check results")
        assert self.server.getRegister(t.HMIRead.REG_DeviceStatus) == 0x0000
        self.server.setRegister(t.HMIWrite.REG_MODE, 0) #Disable HMI control
        


if __name__ == "__main__":
    print("Do not execute main please")