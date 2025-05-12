import serial
from PyQt6.QtCore import QThread, pyqtSignal
from config.settings import IMU_SERIAL_PORT, IMU_SERIAL_BAUDRATE

class IMUSerialReader(QThread):
    rotation_received = pyqtSignal(float)  # Signal to emit roll angle

    def __init__(self, port=IMU_SERIAL_PORT, baudrate=IMU_SERIAL_BAUDRATE):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True

    def run(self):
        try:
            with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                while self.running:
                    line = ser.readline().decode().strip()
                    try:
                        roll = float(line)
                        self.rotation_received.emit(-roll)
                    except ValueError:
                        pass
        except serial.SerialException as e:
            print(f"Serial error: {e}")

    def stop(self):
        self.running = False
        self.wait()
