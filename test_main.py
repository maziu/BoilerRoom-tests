
from modbus_server import Modbus_ControllableServer

import pytest
import logging

class TestClass:
    
    xVar = 2
    log = logging.getLogger(__name__)

    @classmethod
    def setup_class(cls):
        cls.log.setLevel(logging.INFO)
        cls.xVar = 3
        cls.log.info("Setting up test env...")
        cls.server = Modbus_ControllableServer(1001, "TCP")
        cls.log.info("Done!")

    @classmethod
    def teardown_class(cls):
        cls.log.info("Finalizing tests...")
        cls.server.stop_server()
        cls.log.info("Done!")
        
    @pytest.mark.order(1)
    def test_smoke(self):
        self.log.info("Smoke test: PLC connection test")
        assert (1+1) == 2

    def test_base_2(self):
        assert (self.xVar) == 3


if __name__ == "__main__":
    print("Do not execute main please")