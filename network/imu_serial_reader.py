import serial
import time
from PyQt6.QtCore import QThread, pyqtSignal
from config.settings import IMU_SERIAL_PORT, IMU_SERIAL_BAUDRATE, AXIS_SIGN, ROTATION_OFFSET

class IMUSerialReader(QThread):
    rotation_received = pyqtSignal(float)  # Signal to emit roll angle

    def __init__(self, port=IMU_SERIAL_PORT, baudrate=IMU_SERIAL_BAUDRATE):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.reconnect_delay = 2  # seconds

    def run(self):
        while self.running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                    print(f"[IMU] Connected to {self.port}")
                    while self.running:
                        line = ser.readline().decode(errors="ignore").strip()
                        try:
                            roll = float(line)
                            self.rotation_received.emit(AXIS_SIGN * roll + ROTATION_OFFSET)
                        except ValueError:
                            continue
            except serial.SerialException as e:
                print(f"[IMU] Serial error: {e}")
                print(f"[IMU] Reattempting connection in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)

    def stop(self):
        self.running = False
        self.wait()
