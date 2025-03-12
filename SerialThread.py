import serial
from PyQt6.QtCore import QThread, pyqtSignal
class SerialThread(QThread):
    
    dataReceived = pyqtSignal(bytes)
    errorMessage = pyqtSignal(str)
    successMessage = pyqtSignal(str)
    serial = {}
    port="COM1"
    baudrate=115200
    running = False
    def __init__(self):
        super().__init__()
        self.buffer = bytearray()

    def run(self):

        self.running = True
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as self.serial:
                self.successMessage.emit(self.port)
                while self.running:
                    if self.serial.in_waiting:
                        data = self.serial.read(self.serial.in_waiting or 1)
                        self.dataReceived.emit(data)
                        
        except serial.SerialException as e:
            data = f"Serial exception: {e}"
            self.errorMessage.emit(data)

    def send_data(self, data):
        try:
            if self.serial and self.serial.is_open:
                self.serial.write(data.encode('utf-8'))
                self.successMessage.emit("0指令下传: " + data)
            else:
                self.errorMessage.emit("串口未打开")
        except serial.SerialException as e:
            self.errorMessage.emit(f"Serial exception during send: {e}")

    def stop(self):
        self.running = False
        self.wait()
        if self.serial != {}:
            self.serial.close()
        self.requestInterruption()

serialThread = SerialThread()