import socket
import struct
import hashlib
import threading
import time

class NetworkManager:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None
        self.connected = False
        self.authenticated = False
        self.lock = threading.Lock()
        
        # Basic configuration
        self.connection_timeout = 10.0
        self.socket_timeout = 30.0
        self.auth_timeout = 5.0

    def hash_password(self, password):
        """Generate SHA256 hash of password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def connect_to_server(self, password):
        """Connect to server with authentication"""
        with self.lock:
            try:
                print(f"Connecting to {self.server_host}:{self.server_port}")
                
                # Create and configure socket
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.connection_timeout)
                
                # Connect
                connect_start = time.time()
                try:
                    self.sock.connect((self.server_host, self.server_port))
                    connect_time = time.time() - connect_start
                    print(f"Socket connected in {connect_time:.3f}s")
                except socket.timeout:
                    self.sock.close()
                    return False, 0, 0, f"Connection timeout ({self.connection_timeout}s)"
                except ConnectionRefusedError:
                    self.sock.close()
                    return False, 0, 0, "Server refused connection"
                except Exception as e:
                    self.sock.close()
                    return False, 0, 0, f"Connection error: {str(e)}"

                # Set socket timeout for operations
                self.sock.settimeout(self.socket_timeout)

                # Authentication
                auth_start = time.time()
                try:
                    password_hash = self.hash_password(password).encode()
                    auth_header = b'AUTH' + struct.pack('>I', len(password_hash))
                    
                    print("Sending authentication...")
                    self.sock.sendall(auth_header + password_hash)

                    print("Waiting for auth response...")
                    response = self._receive_exact(8, timeout=self.auth_timeout)
                    auth_time = time.time() - auth_start
                    
                    if response == b'AUTH_OK\x00':
                        self.connected = True
                        self.authenticated = True
                        success_msg = f"Connected successfully (conn: {connect_time:.3f}s, auth: {auth_time:.3f}s)"
                        print(success_msg)
                        return True, connect_time, auth_time, success_msg
                    elif response == b'AUTH_ERR\x00':
                        self.sock.close()
                        return False, connect_time, auth_time, "Authentication failed - invalid password"
                    else:
                        self.sock.close()
                        return False, connect_time, auth_time, f"Unexpected response: {response}"
                        
                except socket.timeout:
                    self.sock.close()
                    return False, connect_time, 0, f"Authentication timeout ({self.auth_timeout}s)"
                except Exception as e:
                    self.sock.close()
                    return False, connect_time, 0, f"Authentication error: {str(e)}"
                    
            except Exception as e:
                if self.sock:
                    self.sock.close()
                error_msg = f"Connection failed: {str(e)}"
                print(error_msg)
                return False, 0, 0, error_msg

    def send_data(self, header, filename_bytes, image_data):
        """Send data to server with basic progress tracking"""
        if not self._validate_connection():
            return False, "Not connected to server"
        
        try:
            print(f"Sending data: {len(image_data)} bytes")
            send_start = time.time()
            
            # Send data in chunks for large files
            total_data = header + filename_bytes + image_data
            total_size = len(total_data)
            sent_size = 0
            chunk_size = 8192
            
            while sent_size < total_size:
                chunk_end = min(sent_size + chunk_size, total_size)
                chunk = total_data[sent_size:chunk_end]
                
                try:
                    bytes_sent = self.sock.send(chunk)
                    sent_size += bytes_sent
                    
                    # Progress for large files
                    if total_size > 100000 and sent_size % (chunk_size * 10) == 0:
                        progress = (sent_size / total_size) * 100
                        print(f"Upload progress: {progress:.1f}%")
                            
                except socket.timeout:
                    return False, f"Send timeout after {sent_size}/{total_size} bytes"
                except Exception as e:
                    return False, f"Send error: {str(e)}"
            
            send_time = time.time() - send_start
            speed_kbps = (total_size / 1024) / send_time if send_time > 0 else 0
            print(f"Data sent: {total_size} bytes in {send_time:.3f}s ({speed_kbps:.1f} KB/s)")
            
            return True, send_time
            
        except Exception as e:
            error_msg = f"Failed to send data: {str(e)}"
            print(error_msg)
            return False, error_msg

    def receive_data(self):
        """Receive data from server with basic progress tracking"""
        if not self._validate_connection():
            return False, "Not connected to server", 0
        
        try:
            print("Waiting for response...")
            receive_start = time.time()
            
            # Get response length
            try:
                length_bytes = self._receive_exact(4, timeout=self.socket_timeout)
                expected_len = struct.unpack('>I', length_bytes)[0]
                print(f"Expecting {expected_len} bytes")
                
                if expected_len > 50 * 1024 * 1024:  # 50MB limit
                    return False, f"Response too large: {expected_len} bytes", 0
                
            except struct.error:
                return False, "Invalid response length format", 0
            except Exception as e:
                return False, f"Failed to read response length: {str(e)}", 0
            
            # Receive data with progress
            try:
                encrypted_data = self._receive_exact(expected_len, timeout=self.socket_timeout, show_progress=True)
                receive_time = time.time() - receive_start
                
                speed_kbps = (expected_len / 1024) / receive_time if receive_time > 0 else 0
                print(f"Data received: {expected_len} bytes in {receive_time:.3f}s ({speed_kbps:.1f} KB/s)")
                
                return True, encrypted_data, receive_time
                
            except Exception as e:
                return False, f"Failed to receive data: {str(e)}", 0
            
        except Exception as e:
            error_msg = f"Receive operation failed: {str(e)}"
            print(error_msg)
            return False, error_msg, 0

    def send_timing_data(self, timing_data):
        """Send timing data to server"""
        if not self._validate_connection():
            return False
        
        try:
            # Validate required fields
            required_fields = ['filename', 'waktu_dekripsi_client', 'ukuran_hasil_kb']
            for field in required_fields:
                if field not in timing_data:
                    print(f"Missing timing field: {field}")
                    return False
            
            print(f"Sending timing data for: {timing_data['filename']}")
            
            import json
            timing_json = json.dumps(timing_data, ensure_ascii=False).encode('utf-8')
            timing_header = b'TIMING' + struct.pack('>I', len(timing_json))
            
            # Send with timeout
            self.sock.settimeout(5.0)
            self.sock.sendall(timing_header + timing_json)
            
            # Wait for acknowledgment
            try:
                ack = self._receive_exact(3, timeout=5.0)
                if ack == b'ACK':
                    print("Timing data acknowledged")
                    return True
                else:
                    print(f"Unexpected timing ack: {ack}")
                    return False
            except socket.timeout:
                print("Timeout waiting for timing ack")
                return False
            
        except Exception as e:
            print(f"Failed to send timing data: {str(e)}")
            return False
        finally:
            # Restore original timeout
            if self.sock:
                self.sock.settimeout(self.socket_timeout)

    def _receive_exact(self, size, timeout=None, show_progress=False):
        """Receive exact amount of data with optional progress"""
        if timeout:
            original_timeout = self.sock.gettimeout()
            self.sock.settimeout(timeout)
        
        try:
            buffer = b""
            bytes_received = 0
            last_progress_log = 0
            
            while bytes_received < size:
                try:
                    chunk = self.sock.recv(min(size - bytes_received, 8192))
                    if not chunk:
                        raise ConnectionError(f"Connection closed after {bytes_received}/{size} bytes")
                    
                    buffer += chunk
                    bytes_received += len(chunk)
                    
                    # Progress for large data
                    if show_progress and size > 50000:
                        progress = (bytes_received / size) * 100
                        if progress - last_progress_log >= 10:
                            print(f"Receive progress: {progress:.1f}%")
                            last_progress_log = progress
                            
                except socket.timeout:
                    raise socket.timeout(f"Timeout receiving data after {bytes_received}/{size} bytes")
                except Exception as e:
                    raise Exception(f"Receive error at {bytes_received}/{size} bytes: {str(e)}")
            
            return buffer
            
        finally:
            if timeout:
                self.sock.settimeout(original_timeout)

    def _validate_connection(self):
        """Validate connection state"""
        if not self.connected:
            print("Not connected to server")
            return False
        if not self.authenticated:
            print("Not authenticated with server")
            return False
        if not self.sock:
            print("Socket not available")
            return False
        return True

    def disconnect(self):
        """Disconnect from server with cleanup"""
        with self.lock:
            if self.sock:
                try:
                    # Send disconnect notification
                    if self.connected and self.authenticated:
                        try:
                            print("Sending disconnect notification...")
                            self.sock.settimeout(2.0)
                            self.sock.sendall(b'DISCONNECT')
                        except:
                            pass  # Ignore errors during disconnect
                    
                    print("Closing socket...")
                    self.sock.close()
                    
                except Exception as e:
                    print(f"Error during disconnect: {e}")
                finally:
                    self.sock = None
            
            # Reset state
            self.connected = False
            self.authenticated = False
            
            print("Disconnected from server")
            return True, "Successfully disconnected from server"

    def get_connection_status(self):
        """Get current connection status"""
        return {
            'connected': self.connected,
            'authenticated': self.authenticated,
            'server_host': self.server_host,
            'server_port': self.server_port,
            'socket_available': self.sock is not None
        }

    def test_connection(self):
        """Test if connection is still alive"""
        if not self._validate_connection():
            return False, "Not connected"
        
        try:
            original_timeout = self.sock.gettimeout()
            self.sock.settimeout(3.0)
            
            self.sock.sendall(b'PING')
            response = self._receive_exact(4, timeout=3.0)
            
            if response == b'PONG':
                return True, "Connection healthy"
            else:
                return False, f"Unexpected ping response: {response}"
                
        except Exception as e:
            return False, f"Connection test failed: {str(e)}"
        finally:
            if self.sock:
                self.sock.settimeout(original_timeout)