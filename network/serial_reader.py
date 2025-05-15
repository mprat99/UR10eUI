import serial
import time
from PyQt6.QtCore import QThread, pyqtSignal
from config.settings import IMU_SERIAL_PORT, IMU_SERIAL_BAUDRATE, AXIS_SIGN, ROTATION_OFFSET

class SerialReader(QThread):
    rotation_received = pyqtSignal(float)
    state_received = pyqtSignal(int)

    def __init__(self, port=IMU_SERIAL_PORT, baudrate=IMU_SERIAL_BAUDRATE):
        super().__init__()
        self.port = port
        self.baudrate = baudrate
        self.running = True
        self.reconnect_delay = 2  # seconds
        self.watchdog_timeout = 0.5  # seconds without data before reconnect

    def run(self):
        while self.running:
            try:
                with serial.Serial(self.port, self.baudrate, timeout=1) as ser:
                    print(f"[IMU] Connected to {self.port}")
                    last_data_time = time.time()

                    while self.running:
                        # Watchdog: check if data has stopped flowing
                        if time.time() - last_data_time > self.watchdog_timeout:
                            print("[IMU] Watchdog timeout: no data received in 10 seconds. Reconnecting...")
                            raise serial.SerialException("Watchdog timeout")

                        try:
                            line = ser.readline().decode(errors="ignore").strip()
                        except Exception as e:
                            print(f"[IMU] Read error: {e}")
                            break

                        if not line or ':' not in line:
                            continue

                        last_data_time = time.time()  # Reset watchdog

                        prefix, value = line.split(':', 1)
                        prefix = prefix.strip().lower()
                        value = value.strip()

                        if prefix == 'r':
                            try:
                                roll = float(value)
                                self.rotation_received.emit(AXIS_SIGN * roll + ROTATION_OFFSET)
                            except ValueError:
                                continue
                        elif prefix == 's':
                            try:
                                state = int(value)
                                if state in {1, 2, 3}:
                                    self.state_received.emit(state)
                            except ValueError:
                                continue

            except serial.SerialException as e:
                print(f"[IMU] Serial error: {e}")
                print(f"[IMU] Reattempting connection in {self.reconnect_delay} seconds...")
                time.sleep(self.reconnect_delay)

    def stop(self):
        self.running = False
        self.wait()
