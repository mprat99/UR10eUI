from PyQt6.QtCore import QObject, pyqtSignal, QTimer, QIODevice
from PyQt6.QtSerialPort import QSerialPort, QSerialPortInfo
from config.settings import IMU_SERIAL_PORT, IMU_SERIAL_BAUDRATE, AXIS_SIGN, ROTATION_OFFSET

class SerialReader(QObject):
    rotation_received = pyqtSignal(float)
    state_received = pyqtSignal(int)

    def __init__(self, port_name=IMU_SERIAL_PORT, baudrate=IMU_SERIAL_BAUDRATE, parent=None):
        super().__init__(parent)
        self.port_name = port_name
        self.baudrate = baudrate

        self.serial = QSerialPort()
        self.serial.setPortName(self.port_name)
        self.serial.setBaudRate(self.baudrate)
        self.serial.readyRead.connect(self.read_data)
        self.serial.errorOccurred.connect(self.handle_error)

        self.reconnect_timer = QTimer()
        self.reconnect_timer.setInterval(2000)
        self.reconnect_timer.timeout.connect(self.try_connect)

        self.buffer = b""

    def start(self):
        self.try_connect()

    def stop(self):
        self.reconnect_timer.stop()
        if self.serial.isOpen():
            self.serial.close()

    def try_connect(self):
        if not self.serial.isOpen():
            if self.serial.open(QIODevice.OpenModeFlag.ReadOnly):
                print(f"[IMU] Connected to {self.port_name}")
                self.reconnect_timer.stop()
            else:
                print(f"[IMU] Failed to open {self.port_name}, retrying...")

    def handle_error(self, error):
        if error == QSerialPort.SerialPortError.ResourceError:
            print(f"[IMU] Serial resource error — reconnecting...")
            self.serial.close()
            self.reconnect_timer.start()

    def read_data(self):
        self.buffer += self.serial.readAll().data()

        while b'\n' in self.buffer:
            line, self.buffer = self.buffer.split(b'\n', 1)
            try:
                text = line.decode(errors='ignore').strip()
                if not text or ':' not in text:
                    continue

                prefix, value = text.split(':', 1)
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
            except Exception as e:
                print(f"[IMU] Parse error: {e}")
