from .comm import *
from time import sleep


command = {"change": [1], "enable": [2], "clear": [3], "read": [5]}
Kv = 10.67
Ki = 6.4


def calcVoltNum(volt):
    number = int(volt * Kv)
    num_bytes = number.to_bytes(2, byteorder='big', signed=True)
    return num_bytes

def calcCurrNum(curr):
    number = int(curr * Ki)
    num_bytes = number.to_bytes(2, byteorder='big', signed=True)
    return num_bytes

def getVIMsg(volt, curr):
    msg = command["change"][:]
    
    volt_bytes = calcVoltNum(volt)
    curr_bytes = calcCurrNum(curr)
    
    msg.append(volt_bytes[1])  # Младший байт напряжения
    msg.append(volt_bytes[0])  # Старший байт напряжения
    msg.append(curr_bytes[1])  # Младший байт тока
    msg.append(curr_bytes[0])  # Старший байт тока
    
    return msg


class HV_source:
    def __init__(self, port):
        self.port = port
        self.ser = Serial(port, 38400)

    def __del__(self):
        if not self.ser.checkPortState():
            return
        self.deInit()
    
    ser = None

    def init(self):
        if self.ser.checkPortState():
            return 0
        
        if not (self.port in (port.device for port in listAvailablePorts())):
            print(f"COM-порт {self.port} не найден")
            return 1

        if self.ser.open() == False:
            return 1
        
        return 0

    def set(self, volt, curr):
        if not self.ser.checkPortState():
            return 1
        
        msg = getVIMsg(volt, curr)
        # print(f"Отправка сообщения: {msg}")
        self.ser.write(msg)
        self.ser.write(command["enable"])

        return 0
    
    def deInit(self):
        if not self.ser.checkPortState():
            return 1
        
        self.ser.write(command["clear"])
        self.ser.close()

        return 0

    def read(self):
        if not self.ser.checkPortState():
            return None

        self.ser.write(command["read"])
        data = self.ser.read(5)

        if data:
            data_list = [hex(byte) for byte in data]
            # print(f"Полученные данные: {data_list}")
        else:
            print("Не удалось получить данные")
        
        V = int(data_list[2][2:] + data_list[3][2:], 16)
        V //= Kv
        I = int(data_list[0][2:] + data_list[1][2:], 16)
        I //= Ki

        return [V, I]
    
    def stepToCur(self, curr_target, file = None, V1 = None, A1 = None):
        if file != None and (V1 == None or A1 == None):
            print("No meters")
            return
        
        volt_cur, curr_cur = self.read()

        print(f"Step to {curr_target} uA")
        print(f"Current V: {volt_cur} V, I: {curr_cur} uA\n")

        k = 30
        if curr_target < curr_cur:
            k *= -1
        
        sleep(0.5)
        cur_prev = curr_cur

        while (curr_target < curr_src) == (k < 0):
            volt_cur += k
            self.set(volt_cur, 5000)
            sleep(0.3)
            volt_src, curr_src = self.read()

            if abs(curr_src-cur_prev) > 300:
                read_tmp = 0
                volt_src, curr_src = 0, 0
                sleep(1)
                for i in range(10):
                    read_tmp = self.read()
                    volt_src += read_tmp[0]
                    curr_src += read_tmp[1]
                    sleep(0.1)
                curr_src /= 10
                volt_src /= 10

            cur_prev = curr_src
            print(f"V: {volt_src} V, I: {curr_src} uA")

            if file != None:
                sleep(0.2)
                V1.writeCommand("READ?")
                A1.writeCommand("READ?")
                volt_rd = V1.readCommand()*10
                cur_rd = A1.readCommand()*1000
                print(f"read V: {volt_rd} V, I: {cur_rd} mA")
                file.write(f"{volt_rd}\t{cur_rd}\n")

            print()

        print("End step\n")
        return [volt_src, curr_src]


