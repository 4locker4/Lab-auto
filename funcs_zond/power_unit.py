import serial
from time import sleep, time
import os.path

print(dir(serial))

def check_sum(command):
    return (sum([int(i) for i in command]) % 256).to_bytes(1, 'big')

class PowerUnit(object):

    def __init__(self, addr):

        self.addr = addr

        if (addr < 0 or addr >= 256):
            raise ValueError('power unit address is a 1 byte number')
        self.port = None
        self.port = serial.Serial('/dev/ttyUSB0', 38400, timeout = 0, bytesize = 8, parity = serial.PARITY_NONE, stopbits = 1)
       
    def __del__(self):
        if self.port == None:
            return
        self.set_output(False)
        self.unset_remote()
        self.port.close()

    def start_bytes(self):
        return b'\xAA' + self.addr.to_bytes(1, 'big')

    def set_remote(self):
        command = self.start_bytes() + b'\x20\x01' + b'\x00' * 21
        command += check_sum(command)
        self.port.write(command)

    def unset_remote(self):
        command = self.start_bytes() + b'\x20\x00' + b'\x00' * 21
        command += check_sum(command)
        self.port.write(command)

    def set_output(self, state):
        off = b'\x00'
        on = b'\x01'
        state_byte = on if state else off
        command = self.start_bytes() + b'\x21' + state_byte + b'\x00' * 21
        command += check_sum(command)
        self.port.write(command)

    def set_voltage(self, voltage):
        try:
            byte_voltage = int(voltage).to_bytes(4, 'little')

            command = self.start_bytes() + b'\x23' + byte_voltage + b'\x00' * 18
            command += check_sum(command)
            self.port.write(command)

        except OverflowError:
            print('OverflowError: voltage value has more than 4 bytes')

    def set_max_voltage(self, voltage):
        try:
            byte_voltage = voltage.to_bytes(4, 'little')

            command = self.start_bytes() + b'\x22' + byte_voltage + b'\x00' * 18
            command += check_sum(command)
            self.port.write(command)

        except OverflowError:
            self.port.close()
            print('OverflowError: voltage value has more than 4 bytes')



        
