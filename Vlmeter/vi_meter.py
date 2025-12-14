from .call import *
from time import sleep
import glob


dev_name_def = "/dev/usbtmc0" # "*IDN?" -> name


def getMeters():
    devices = glob.glob("/dev/usbtmc*")
    return devices

def checkMeters():
    devices = glob.glob("/dev/usbtmc*")

    if devices == []:
        print("Meters not found")
        return 1

    print(f"Meters:")
    for device in devices:
        print(f"\t{device}: {getId(device)}")

    return 0

def getId(device):
    if device == None:
        return 1
    
    write_cmd("*IDN?", device)
    sleep(0.01)
    id = read_cmd(device)
    # print(f"File: {device} - {id}")

    return id


class VI_meter:
    def __init__(self, id):
        self.id = id
        
    def __del__(self):
        if self.device == "":
            return
        self.reset()
        
    id = ""
    device = ""

    def init(self, mode):
        for device in getMeters():
            if getId(device) == self.id:
                self.device = device
                break
        
        if self.device == "":
            return 1
        
        self.setMode(mode)
        
        return 0
    
    def setMode(self, mode):
        if self.device == None:
            return 1
        
        if mode == "V":
            write_cmd("CONF:VOLT:DC 1000V", self.device)
        elif mode == "A":
            write_cmd("CONF:CURR:DC 20mA", self.device)
        else:
            print("Incorrect mode")
            return 1

        write_cmd("VOLT:DC:NPLC 10", self.device)

        return 0

    def writeCommand(self, command = "READ?"):
        if self.device == "":
            return 1
        write_cmd(command, self.device)
        return 0

    def readCommand(self):
        if self.device == None:
            return 0
        val = float(read_cmd(self.device))
        return val

    def readVal(self):
        if self.device == None:
            return 0
        write_cmd("READ?", self.device)
        sleep(0.01)
        val = float(read_cmd(self.device))
        return val
    
    def reset(self):
        if self.device == "":
            return 1
        write_cmd("*CLS", self.device)
        sleep(0.01)
        write_cmd("*RST", self.device)
        return 0

