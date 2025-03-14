"""TCP client implementation for communicating with the UR robot."""

import socket
import struct
import threading
from typing import Callable, Optional
from PyQt6.QtCore import QObject, pyqtSignal

from config.settings import TCP_HOST, TCP_PORT

class URClient(QObject):
    # Signals for different types of data
    robot_state_changed = pyqtSignal(dict)  # Emitted when robot state data is received
    error_occurred = pyqtSignal(str)        # Emitted when an error occurs
    
    def __init__(self):
        super().__init__()
        self.socket: Optional[socket.socket] = None
        self.connected = False
        self.running = False
        self.receive_thread: Optional[threading.Thread] = None
    
    def connect(self) -> bool:
        """Connect to the robot's TCP server."""
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((TCP_HOST, TCP_PORT))
            self.connected = True
            self.running = True
            
            # Start receive thread
            self.receive_thread = threading.Thread(target=self._receive_loop)
            self.receive_thread.daemon = True
            self.receive_thread.start()
            
            return True
        except Exception as e:
            self.error_occurred.emit(f"Connection failed: {str(e)}")
            return False
    
    def disconnect(self):
        """Disconnect from the robot's TCP server."""
        self.running = False
        if self.socket:
            try:
                self.socket.close()
            except:
                pass
        self.connected = False
        if self.receive_thread:
            self.receive_thread.join(timeout=1.0)
    
    def _receive_loop(self):
        """Background thread for receiving data from the robot."""
        while self.running:
            try:
                # Read message size (first 4 bytes)
                size_data = self._recv_all(4)
                if not size_data:
                    break
                
                msg_size = struct.unpack("!I", size_data)[0]
                
                # Read the message
                msg_data = self._recv_all(msg_size)
                if not msg_data:
                    break
                
                # Parse and emit the data
                state_data = self._parse_state_data(msg_data)
                self.robot_state_changed.emit(state_data)
                
            except Exception as e:
                self.error_occurred.emit(f"Receive error: {str(e)}")
                break
        
        self.connected = False
    
    def _recv_all(self, size: int) -> Optional[bytes]:
        """Receive exactly 'size' bytes from the socket."""
        data = bytearray()
        while len(data) < size:
            try:
                packet = self.socket.recv(size - len(data))
                if not packet:
                    return None
                data.extend(packet)
            except:
                return None
        return bytes(data)
    
    def _parse_state_data(self, data: bytes) -> dict:
        """Parse the robot state data from the received bytes.
        
        This is a placeholder implementation. The actual parsing would depend
        on the specific message format used by the UR robot.
        """
        # TODO: Implement actual parsing based on UR robot protocol
        return {
            "raw_data": data.hex()
        }
    
    def send_command(self, command: str) -> bool:
        """Send a command to the robot.
        
        :param command: The command string to send
        :return: True if the command was sent successfully
        """
        if not self.connected:
            self.error_occurred.emit("Not connected to robot")
            return False
        
        try:
            # Add command terminator if needed
            if not command.endswith('\n'):
                command += '\n'
            
            # Send the command
            self.socket.sendall(command.encode('utf-8'))
            return True
        except Exception as e:
            self.error_occurred.emit(f"Send error: {str(e)}")
            return False 