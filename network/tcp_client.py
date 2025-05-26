import json
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtNetwork import QTcpSocket, QAbstractSocket
from config.settings import TCP_HOST, TCP_PORT, TCP_MESSAGE_DELIMITER   

RECONNECT_INTERVAL = 5000

class TCPClient(QObject):
    message_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    connection_lost = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = QTcpSocket(self)
        self.socket.readyRead.connect(self._on_ready_read)
        self.socket.errorOccurred.connect(self._on_error)
        self.socket.disconnected.connect(self._on_disconnected)

        self._buffer = bytearray()
        
        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.setInterval(RECONNECT_INTERVAL)
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)

    def connect_to_robot(self):
        """Connect to the TCP host using parameters from config.settings."""
        self.socket.connectToHost(TCP_HOST, TCP_PORT)
        if not self.socket.waitForConnected(3000):
            self.error_occurred.emit(f"Connection failed: {self.socket.errorString()}")
            self._start_reconnect_attempts()
        else:
            print("Connected to robot.")

    def _on_ready_read(self):
        """Handle incoming data as \r-separated JSON messages with proper buffer management."""
        self._buffer += self.socket.readAll().data()
        
        while True:

            pos = self._buffer.find(TCP_MESSAGE_DELIMITER)
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


    def disconnect_from_robot(self):
        """Disconnect and stop reconnection attempts."""
        if self.socket.state() == QAbstractSocket.SocketState.ConnectedState:
            self.socket.disconnectFromHost()
            self.socket.waitForDisconnected(3000)
            print("Disconnected from robot.")
        self.reconnect_timer.stop()

    def _on_disconnected(self):
        """Handle unexpected disconnections."""
        self.error_occurred.emit("Connection lost. Attempting to reconnect...")
        self.connection_lost.emit()
        self._start_reconnect_attempts()

    def _start_reconnect_attempts(self):
        """Start the reconnection timer if it’s not already active."""
        if not self.reconnect_timer.isActive():
            self.reconnect_timer.start()

    def _attempt_reconnect(self):
        """Try to reconnect if not currently connected."""
        if self.socket.state() == QAbstractSocket.SocketState.ConnectedState:
            self.reconnect_timer.stop()
            print("Connected to Robot!")
            return
        print("Attempting to reconnect...")
        self.socket.abort()
        self.socket.connectToHost(TCP_HOST, TCP_PORT)

    def _on_error(self, socket_error):
        """Handle socket errors and trigger reconnection attempts."""
        self.error_occurred.emit(f"Socket error: {self.socket.errorString()}")
        self._start_reconnect_attempts()