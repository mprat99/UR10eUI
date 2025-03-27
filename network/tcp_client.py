import json
import struct
from PyQt6.QtCore import QObject, pyqtSignal, QByteArray, QTimer
from PyQt6.QtNetwork import QTcpSocket, QAbstractSocket
from config.settings import TCP_HOST, TCP_PORT

RECONNECT_INTERVAL = 5000  # 5 seconds

class TCPClient(QObject):
    # Signals for parsed robot state data and errors
    message_received = pyqtSignal(dict)
    error_occurred = pyqtSignal(str)
    connection_lost = pyqtSignal()  # Signal for unexpected disconnection

    def __init__(self, parent=None):
        super().__init__(parent)
        self.socket = QTcpSocket(self)
        self.socket.readyRead.connect(self._on_ready_read)
        self.socket.errorOccurred.connect(self._on_error)
        self.socket.disconnected.connect(self._on_disconnected)  # Handle disconnections

        self._buffer = QByteArray()       # Buffer for accumulating incoming data
        self._message_queue = []          # List to hold messages pending emission

        self.reconnect_timer = QTimer(self)
        self.reconnect_timer.setInterval(RECONNECT_INTERVAL)
        self.reconnect_timer.timeout.connect(self._attempt_reconnect)

    def connect_to_robot(self):
        """Connect to the robot's TCP server."""
        self.socket.connectToHost(TCP_HOST, TCP_PORT)
        if not self.socket.waitForConnected(3000):
            self.error_occurred.emit(f"Connection failed: {self.socket.errorString()}")
            self._start_reconnect_attempts()
        else:
            print("Connected to robot.")

    def disconnect_from_robot(self):
        """Disconnect from the robot's TCP server."""
        if self.socket.state() == QAbstractSocket.SocketState.ConnectedState:
            self.socket.disconnectFromHost()
            if self.socket.state() != QAbstractSocket.SocketState.UnconnectedState:
                self.socket.waitForDisconnected(3000)
            print("Disconnected from robot.")
        self.reconnect_timer.stop()  # Stop reconnection attempts if user manually disconnects

    def _on_disconnected(self):
        """Handles unexpected disconnections and starts reconnection attempts."""
        self.error_occurred.emit("Connection lost. Attempting to reconnect...")
        self.connection_lost.emit()
        self._start_reconnect_attempts()

    def _start_reconnect_attempts(self):
        """Starts a timer to attempt reconnection at regular intervals."""
        if not self.reconnect_timer.isActive():
            self.reconnect_timer.start()

    def _attempt_reconnect(self):
        """Attempts to reconnect to the server."""
        if self.socket.state() == QAbstractSocket.SocketState.ConnectedState:
            self.reconnect_timer.stop()
            return  # Already connected

        print("Attempting to reconnect...")
        self.socket.abort()  # Reset any failed connection attempts
        self.socket.connectToHost(TCP_HOST, TCP_PORT)

    def _on_ready_read(self):
        """
        Called when new data is available from the socket.
        It appends data to an internal buffer, then processes complete messages.
        Each message begins with a 4-byte header that encodes the message length.
        """
        self._buffer.append(self.socket.readAll())

        # Process as many complete messages as possible
        while True:
            # Need at least 4 bytes to know message length
            if self._buffer.size() < 4:
                break

            # Peek at the first 4 bytes to determine message size
            header = self._buffer.left(4)
            msg_size = struct.unpack("!I", header)[0]

            # Wait until the entire message has arrived
            if self._buffer.size() < 4 + msg_size:
                break

            # Remove the header from the buffer
            self._buffer = self._buffer.mid(4)
            # Extract the message data
            msg_data = self._buffer.left(msg_size)
            self._buffer = self._buffer.mid(msg_size)

            # Parse the JSON message
            try:
                message = json.loads(msg_data.data().decode('utf-8'))
            except Exception as e:
                self.error_occurred.emit(f"JSON parse error: {str(e)}")
                continue

            # Remove any existing message in the queue with the same "type"
            if "type" in message:
                self._message_queue = [msg for msg in self._message_queue if msg.get("type") != message["type"]]

            # Insert the message in the queue:
            # If the message has high priority, insert it at the front;
            # otherwise, append to the end.
            if message.get("priority") == "high":
                self._message_queue.insert(0, message)
            else:
                self._message_queue.append(message)

        # Process the queued messages after reading all available data.
        self._process_message_queue()

    def _process_message_queue(self):
        """
        Emits messages stored in the queue.
        For safety, we sort the queue so that if both high and normal priority
        messages are queued, all high-priority messages are processed first.
        The relative order among messages with the same priority is maintained.
        """
        self._message_queue.sort(key=lambda msg: 0 if msg.get("priority") == "high" else 1)
        while self._message_queue:
            message = self._message_queue.pop(0)
            self.message_received.emit(message)

    def _on_error(self, socket_error):
        """Emits any socket errors and starts reconnection if needed."""
        self.error_occurred.emit(f"Socket error: {self.socket.errorString()}")
        self._start_reconnect_attempts()

