import json
import serial
import serial.tools.list_ports
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from config.settings import UART_PORT, UART_BAUDRATE, UART_RECONNECT_INTERVAL, UART_READ_INTERVAL


class UARTClient(QObject):
    message_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.port = UART_PORT
        self.baudrate = UART_BAUDRATE
        self.ser = None
        self._buffer = bytearray()

        # Timer to poll serial input
        self.read_timer = QTimer(self)
        self.read_timer.setInterval(UART_READ_INTERVAL)
        self.read_timer.timeout.connect(self._read_serial_data)

        # Timer for auto-reconnect
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.setInterval(UART_RECONNECT_INTERVAL)
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)

    def connect_to_robot(self):
        """Try to open the serial port."""
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=0.1)
            self.read_timer.start()
            self.reconnect_timer.stop()
            print(f"Connected to UART on {self.port}")
        except serial.SerialException as e:
            self.error_occurred.emit(f"Serial connection failed: {str(e)}")
            self._start_reconnect_attempts()

    def _read_serial_data(self):
        """Read and parse JSON messages from UART."""
        try:
            if self.ser and self.ser.in_waiting:
                self._buffer += self.ser.read(self.ser.in_waiting)

                # Process complete messages separated by \r
                while True:
                    pos = self._buffer.find(b'\r')
                    if pos == -1:
                        break

                    msg_bytes = self._buffer[:pos]
                    self._buffer = self._buffer[pos+1:]

                    try:
                        message = json.loads(msg_bytes.decode('utf-8'))
                        self.message_received.emit(message)
                    except UnicodeDecodeError:
                        self.error_occurred.emit(f"Invalid UTF-8 in message: {msg_bytes}")
                    except json.JSONDecodeError as e:
                        self.error_occurred.emit(f"Invalid JSON: {e.doc} | Error: {str(e)}")

        except serial.SerialException as e:
            self.error_occurred.emit(f"Serial read error: {str(e)}")
            self.connection_lost.emit()
            self._start_reconnect_attempts()

    def disconnect_from_device(self):
        """Close the serial connection."""
        if self.ser and self.ser.is_open:
            self.ser.close()
            print("Disconnected from UART.")
        self.read_timer.stop()
        self.reconnect_timer.stop()

    def _start_reconnect_attempts(self):
        """Start reconnecting to UART."""
        if not self.reconnect_timer.isActive():
            self.reconnect_timer.start()
        self.read_timer.stop()

    def _attempt_reconnect(self):
        """Try reconnecting to the UART device."""
        if self.ser and self.ser.is_open:
            self.reconnect_timer.stop()
            return
        print("Attempting to reconnect to UART...")
        self.connect_to_robot()
