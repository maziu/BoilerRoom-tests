import pytest
from modbus_server import ModbusServer


@pytest.fixture(scope="session")
def server():
    with ModbusServer() as s:
        yield s


@pytest.fixture(autouse=True)
def reset(server):
    server.setPLCReset()
    print(" Reset to default state")
    yield
