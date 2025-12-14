import serial
import serial.tools.list_ports


def listAvailablePorts():
    ports = serial.tools.list_ports.comports()
    return [port for port in ports if port.description != "n/a"]

def checkPorts():
    available_ports = listAvailablePorts()
    
    if not available_ports:
        print("COM ports not found")
        return 1
    
    print("Available COM ports:")
    for port in available_ports:
        print(f"\t{port.device}: {port.description}")
    
    return 0


class Serial:
    def __init__(self, port, baudrate):
        self.port = port
        self.baudrate = baudrate

    port = ""
    ser = None
    port_state = False
    baudrate = 38400

    def open(self):
        try:
            self.ser = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=1
            )
            self.port_state = True
            print(f"Порт {self.port} открыт успешно")
            return True
        
        except serial.SerialException as e:
            print(f"Ошибка открытия порта {self.port}: {e}")
            return False
    
    def close(self):
        if self.ser and self.ser.is_open:
            self.ser.close()
            self.port_state = False
            print("Порт закрыт")
    
    def purge(self):
        if not self.port_state:
            print("Порт не открыт для чтения")
            return False
        
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        # print("Буферы порта очищены")
        return True
    
    def write(self, buffer):
        if not self.port_state:
            print("Порт не открыт для записи")
            return False
        
        if isinstance(buffer, list):
            data_to_send = bytes(buffer)
        else:
            data_to_send = buffer
            
        # print(f"Отправка данных: {data_to_send} ({[hex(b) for b in data_to_send]})")
        
        self.ser.write(data_to_send)
        self.ser.flush()  # Ожидание завершения записи
        
    def read(self, len=1):
        if not self.port_state:
            print("Порт не открыт для чтения")
            return None
        
        data = self.ser.read(len)

        return data if data else None

    def checkPortState(self):
        return self.port_state
        
        