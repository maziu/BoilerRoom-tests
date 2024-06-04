
import sys
from enum import Enum

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_tcp
from modbus_tk import modbus_rtu


class Input(Enum):
    EXAMPLE_INPUT = 1
    EXAMPLE_IN2 = 2

class TempSensor(Enum):
    TS_3D = 100
    TS_WEATHER = 101
    TS_XXX = 2

class Output(Enum):
    OUT_integrator = 0
    OUT_XXX = 1   

class Param(Enum):
    P_abc = 0
    P_cde = 1
    P_qwe = 2

class Modbus_ControllableServer():


    def __init__(self, port, serverType = "Serial", slaveID = 5):
        self.logger = modbus_tk.utils.create_logger(name="console", record_format="%(message)s")
        if not port:
            raise ValueError("No port specified")
        if serverType is not "Serial" and serverType is not "TCP":
            raise ValueError("Invalid serverType specified, only Serial and TCP supported")
        if serverType is "Serial":
            self.server = modbus_rtu.RtuServer(serial = port) 
        if serverType is "TCP":
            self.server = modbus_tcp.TcpServer(port = port)

        self.slaveID = slaveID

        #Init data banks now
        self.server.start()
        self.logger.info("Server initialized")

        self.slave = self.server.add_slave(self.slaveID)
        self.slave.add_block('0', cst.HOLDING_REGISTERS, 100, 300)

    def stop_server(self):
        self.server.stop()

    def setTemperature(self, sensor : TempSensor, value : float):
        pass

    def setInput(self, input : Input):
        pass

    def setParameter(self, param : Param, value : float):
        pass

    def saveParams(self): #Set value, clear after 2-3s
        pass

    def getOutput(self, output : Output) -> bool:
        pass

    def getCounters(self) -> dict:
        pass 

    def init_server():
        try:
            #Create the server
            server = modbus_tcp.TcpServer(port=1234)

            #logger.info("enter 'quit' for closing the server")

            server.start()

            
            while True:
                cmd = sys.stdin.readline()
                args = cmd.split(' ')

                if cmd.find('quit') == 0:
                    sys.stdout.write('bye-bye\r\n')
                    break

                elif args[0] == 'add_slave':
                    slave_id = int(args[1])
                    server.add_slave(slave_id)
                    sys.stdout.write('done: slave %d added\r\n' % slave_id)

                elif args[0] == 'add_block':
                    slave_id = int(args[1])
                    name = args[2]
                    block_type = int(args[3])
                    starting_address = int(args[4])
                    length = int(args[5])
                    slave = server.get_slave(slave_id)
                    slave.add_block(name, block_type, starting_address, length)
                    sys.stdout.write('done: block %s added\r\n' % name)

                elif args[0] == 'set_values':
                    slave_id = int(args[1])
                    name = args[2]
                    address = int(args[3])
                    values = []
                    for val in args[4:]:
                        values.append(int(val))
                    slave = server.get_slave(slave_id)
                    slave.set_values(name, address, values)
                    values = slave.get_values(name, address, len(values))
                    sys.stdout.write('done: values written: %s\r\n' % str(values))

                elif args[0] == 'get_values':
                    slave_id = int(args[1])
                    name = args[2]
                    address = int(args[3])
                    length = int(args[4])
                    slave = server.get_slave(slave_id)
                    values = slave.get_values(name, address, length)
                    sys.stdout.write('done: values read: %s\r\n' % str(values))

                else:
                    sys.stdout.write("unknown command %s\r\n" % args[0])
        finally:
            server.stop()
