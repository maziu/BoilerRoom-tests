
import sys
from enum import IntEnum

import modbus_tk
import modbus_tk.defines as cst
from modbus_tk import modbus_tcp
from modbus_tk import modbus_rtu
import serial

from threading import Lock
from  time import sleep

import logging
import traceback

log = logging.getLogger(__name__)

class HMIRead(IntEnum):
    REG_DeviceStatus = 200
    REG_IO_Inputs = 201
    REG_3D_Setpoint = 202
    REG_CyclesPerSec = 203
    REG_ParamsTimestamp = 204
    REG_Temperatures = 205
    REG_TS_3D = 205
    REG_TS_WEATHER = 206
    REG_TS_BUF = 207
    REG_TS_CWU = 208
    REG_TS_BOILER = 209
    REG_TS_INT = 210
    REG_TS_RESERVED = 211
    REG_OpMode = 212

class TestReg(IntEnum):
    REG_TEST = 299

class OPMODE(IntEnum):
    OPMODE_Off = 0
    OPMODE_Preheat = 1
    OPMODE_FanOff = 2
    OPMODE_FanOn = 3

class HMIWrite(IntEnum):
    REG_MODE = 100
    REG_CMD = 101
    REG_FLAGS = 102
    REG_TestMode = 103
    REG_ParamsTimestamp = 104
    REG_PARAMS = 105
    REG_SIM_TEMP = 144
    REG_SIM_INPUTS = 150

class TestMode(IntEnum):
    REG_TestMode_Off = 0
    REG_TestMode_1 = 0xFEED

class TempSensor(IntEnum):
    TS_3D = 0
    TS_WEATHER = 1
    TS_BUF = 2
    TS_CWU = 3
    TS_BOILER = 4
    TS_INT = 5

class Flags(IntEnum):
    FLAG_SaveParams = 0
    FLAG_StartBoiler = 1
    FLAG_SimTemp = 2
    FLAG_FanKeepalive = 3
    FLAG_SimInputs = 4
    FLAG_PLCReset = 5

class Devices_OUT(IntEnum):
    DEVO_PCirc = 0
    DEVO_Belimo2 = 1
    DEVO_Belimo1 = 2
    DEVO_PBuf = 3
    DEVO_VI2_CWU = 4
    DEVO_VI2_Heater = 5
    DEVO_Lighter = 6
    DEVO_Fan = 7   
    DEVO_PBoiler = 8
    DEVO_VI1_Heater = 9
    DEVO_PHeater = 10
    DEVO_VI1_CWU = 11
    DEVO_V3D_Close = 12
    DEVO_V3D_Open = 13     

class Devices_IN(IntEnum):
    DEVI_PFireplace = 0
    DEVI_BtnCirc = 3
    DEVI_BtnLighter = 6
    DEVI_SigThermostat = 7

class Param(IntEnum):
    P_IGNITION_TIME_105 = 0
    P_FAN_TIME_MIN_106 = 1
    P_FAN_TEMP_MAX_107 = 2
    P_FAN_TEMP_MIN_108 = 3
    P_FAN_TIME_KEEP_109 = 4
    # RESERVED_110 = 5
    P_PUMP_TEMP_ON_111 = 6
    P_PUMP_TEMP_OFF_112 = 7
    P_INTEGR_TIME_MOVE_113 = 8
    P_CWU_TEMP_ON_114 = 9
    P_CWU_TEMP_OFF_115 = 10
    P_CWU_INTEGR_TEMP_DIFF_ON_116 = 11
    P_CWU_INTEGR_TEMP_DIFF_OFF_117 = 12
    P_PUMP_HEATER_TEMP_DIFF_BOILER_MIN_118 = 13
    P_PUMP_HEATER_TEMP_DIFF_BOILER_MAX_119 = 14
    P_PUMP_MODE_HEATER_INTEGR_TEMP_DIFF_ON_120 = 15
    P_PUMP_MODE_HEATER_INTEGR_TEMP_DIFF_OF_121 = 16
    P_PUMP_MODE_FIRE_INTEGR_TEMP_DIFF_ON_122 = 17
    P_PUMP_MODE_FIRE_INTEGR_TEMP_DIFF_OFF_123 = 18
    P_PUMP_MODE_BUFF_INTEGR_TEMP_DIFF_ON_124 = 19
    P_PUMP_MODE_BUFF_INTEGR_TEMP_DIFF_OFF_125 = 20
    P_3D_VALVE_TIME_WAIT_126 = 21
    P_3D_VALVE_TEMP_DIFF_ACTIVATION_127 = 22
    P_3D_VALVE_KP_128 = 23
    P_3D_TEMP_OUTSIDE_MINUS10_129 = 23
    P_3D_TEMP_OUTSIDE_MINUS5_130 = 24
    P_3D_TEMP_OUTSIDE0_131 = 25
    P_3D_TEMP_OUTSIDE10_132 = 26
    P_3D_TEMP_OUTSIDE_OVER10_133 = 27
    P_BELIMO1_TIME_SWITCHOVER_134 = 28
    P_BELIMO2_LOW_TEMPERATURE_135 = 29
    P_BELIMO2_HIGH_TEMPERATURE_136 = 30

class Temp:
    def __init__(self, i):
        if(type(i) == type(1.23)):
            self.float = i
            self.int = self.float_to_bus(i)
        elif(type(i) == type(123)):
            self.int = i
            self.float = self.bus_to_float(i)
        else:
            raise ValueError("Incorrect temperature type specified!")

    def __int__(self):
        return self.int
    
    def __float__(self):
        return self.float

    def bus_to_float(self, bus):
        x : float = float(bus)
        x = x / 10.0
        return x

    def float_to_bus(self, float):
        x : int = int((float * 10))
        return x

class Modbus_ControllableServer():

    BL_NAME = "BL_1"

    def __init__(self, port, serverType = "Serial", slaveID = 5):
        self.logger = modbus_tk.utils.create_logger(name="console", record_format="%(message)s")
        if not port:
            raise ValueError("No port specified")
        if serverType is not "Serial" and serverType is not "TCP":
            raise ValueError("Invalid serverType specified, only Serial and TCP supported")
        if serverType is "Serial":
            self.server = modbus_rtu.RtuServer(serial = serial.Serial(port=port, baudrate=9600), interframe_multiplier = 40, interchar_multiplier = 3)
        if serverType is "TCP":
            self.server = modbus_tcp.TcpServer(port = port)

        self.slaveID = slaveID

        #Init data banks now
        self.server.start()
        self.logger.info("Server initialized")

        self.slave = self.server.add_slave(self.slaveID)
        self.slave.add_block(self.BL_NAME, cst.HOLDING_REGISTERS, 100, 300)

        self.dataLock = Lock()

    def setRegister(self, addr, value):
        self.slave.set_values(self.BL_NAME, addr, value)

    def getRegister(self, addr) -> int:
        values = self.slave.get_values(self.BL_NAME, addr, 1)
        return values[0]

    def setBitInRegister(self, addr, bitNumber, value : bool = True):
        v = self.slave.get_values(self.BL_NAME, addr, 1)[0]
        if value:
            v = v | (1<<bitNumber)
        else:
            v = v & ~(1<<bitNumber)
        pass
        self.slave.set_values(self.BL_NAME, addr, v)
    
    def clrBitInRegister(self, addr, bitNumber):
        v = self.slave.get_values(self.BL_NAME, addr, 1)[0]
        v = v & ~(1<<bitNumber)
        self.slave.set_values(self.BL_NAME, addr, v)
        
    def getBitInRegister(self, addr, bitNumber) -> bool:
        v = self.slave.get_values(self.BL_NAME, addr, 1)[0]
        return (v & (1<<bitNumber)) != 0
        

#--- Application - related functions starts here

    def enableTestMode(self):
        with self.dataLock:
            self.setRegister(HMIWrite.REG_TestMode, TestMode.REG_TestMode_1)
            self.setBitInRegister(int(HMIWrite.REG_FLAGS), Flags.FLAG_SimTemp)
            self.setBitInRegister(int(HMIWrite.REG_FLAGS), Flags.FLAG_SimInputs)
        sleep(2) # Wait to be sure that value is updated in PLC

    def disableTestMode(self):
        with self.dataLock:
            self.setRegister(HMIWrite.REG_TestMode, TestMode.REG_TestMode_Off)
            self.clrBitInRegister(HMIWrite.REG_FLAGS, Flags.FLAG_SimTemp)
            self.clrBitInRegister(HMIWrite.REG_FLAGS, Flags.FLAG_SimInputs)
        sleep(2) # Wait to be sure that value is updated in PLC

    def setPLCReset(self):
        with self.dataLock:
            self.setBitInRegister(HMIWrite.REG_FLAGS, Flags.FLAG_PLCReset)
        self.waitForUpdate()
        self.clrBitInRegister(HMIWrite.REG_FLAGS, Flags.FLAG_PLCReset)

    def stop_server(self):
        self.server.stop()

    def waitForUpdate(self):
        sleep(1.6)

    def setTemperature(self, sensor : TempSensor, value : float):
        if type(value) != type(12.3):
            raise ValueError("Invalid temp type, should be float. Please use 12.3 format instead of just 12")
        value = Temp(value)
        if sensor < TempSensor.TS_3D or sensor > TempSensor.TS_INT:
            raise ValueError("Invalid temp sensor ID")
        with self.dataLock:
            self.setRegister(HMIWrite.REG_SIM_TEMP + sensor, int(value))

    def getTemperature(self, sensor : TempSensor) -> float:
        if sensor < TempSensor.TS_3D or sensor > TempSensor.TS_INT:
            raise ValueError("Invalid temp sensor ID")
        t = Temp(self.getRegister(HMIRead.REG_Temperatures + sensor))
        return float(t)

    def setInput(self, input : Devices_IN):
        with self.dataLock:
            self.setBitInRegister(HMIWrite.REG_SIM_INPUTS, input)
    
    def clrInput(self, input: Devices_IN):
        with self.dataLock:
            self.clrBitInRegister(HMIWrite.REG_SIM_INPUTS, input)

    def getInput(self, input: Devices_IN) -> bool:
        return self.getBitInRegister(HMIRead.REG_IO_Inputs, input)

    def getOutput(self, output: Devices_OUT) -> bool:
        return self.getBitInRegister(HMIRead.REG_DeviceStatus, int(output))

    def getOpmode(self) -> OPMODE:
        return self.getRegister(HMIRead.REG_OpMode)

    def setFlag(self, flag: Flags):
        with self.dataLock:
            self.setBitInRegister(HMIWrite.REG_FLAGS, flag)

    def clrFlag(self, flag: Flags):
        with self.dataLock:
            self.clrBitInRegister(HMIWrite.REG_FLAGS, flag)

    def setParameter(self, param : Param, value : float):
        with self.dataLock:
            self.setRegister(HMIWrite.REG_PARAMS + param, int(value))

    def saveParams(self): #Set value, clear after 2-3s
        with self.dataLock:
            self.setBitInRegister(HMIWrite.REG_FLAGS, Flags.FLAG_SaveParams)
        self.waitForUpdate()
        self.clrBitInRegister(HMIWrite.REG_FLAGS, Flags.FLAG_SaveParams)

    #def getOutput(self, output : Output) -> bool:
    #    pass

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


class ModbusServer():
    def __init__(self):
        log.setLevel(logging.INFO)
        log.info("Setting up server...")
        self._server = Modbus_ControllableServer("COM5", "Serial")
        self._server.enableTestMode()
        log.info("Done!")

    def __enter__(self):
        return self._server

    def __exit__(self, exc_type, exc_value, tb):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, tb)
            # return False # uncomment to pass exception through

        log.info("Closing server...")
        self._server.disableTestMode()
        self._server.stop_server()
        log.info("Done!")