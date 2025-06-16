import socket
import struct
import hashlib
import threading
import time
import json

class NetworkManager:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port
        self.sock = None
        self.connected = False
        self.authenticated = False
        self.lock = threading.Lock()
        
        # ✅ FIXED: Enhanced configuration
        self.connection_timeout = 10.0  # seconds
        self.socket_timeout = 30.0     # seconds
        self.auth_timeout = 5.0        # seconds
        self.max_retries = 3
        
        print(f"[🌐] NetworkManager initialized - Target: {server_host}:{server_port}")

    def hash_password(self, password):
        """Generate SHA256 hash of password"""
        return hashlib.sha256(password.encode()).hexdigest()

    def connect_to_server(self, password):
        """✅ FIXED: Enhanced connection with better error handling and timeouts"""
        with self.lock:
            try:
                print(f"[🔌] Attempting connection to {self.server_host}:{self.server_port}")
                
                # ✅ FIXED: Enhanced socket configuration
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.settimeout(self.connection_timeout)
                
                # Timing koneksi
                connect_start = time.time()
                
                try:
                    self.sock.connect((self.server_host, self.server_port))
                    connect_time = time.time() - connect_start
                    print(f"[✅] Socket connected in {connect_time:.3f}s")
                except socket.timeout:
                    self.sock.close()
                    return False, 0, 0, f"Timeout connecting to server ({self.connection_timeout}s)"
                except ConnectionRefusedError:
                    self.sock.close()
                    return False, 0, 0, "Server refused connection - check if server is running"
                except socket.gaierror as e:
                    self.sock.close()
                    return False, 0, 0, f"DNS resolution failed: {str(e)}"
                except OSError as e:
                    self.sock.close()
                    return False, 0, 0, f"Network error: {str(e)}"

                # ✅ FIXED: Set socket timeout for subsequent operations
                self.sock.settimeout(self.socket_timeout)

                # Kirim header dan hash password
                auth_start = time.time()
                
                try:
                    password_hash = self.hash_password(password).encode()
                    auth_header = b'AUTH' + struct.pack('>I', len(password_hash))
                    
                    print(f"[🔐] Sending authentication data...")
                    self.sock.sendall(auth_header + password_hash)

                    # ✅ FIXED: Enhanced response handling
                    print(f"[⏳] Waiting for authentication response...")
                    response = self._receive_exact(8, timeout=self.auth_timeout)
                    auth_time = time.time() - auth_start
                    
                    if response == b'AUTH_OK\x00':
                        self.connected = True
                        self.authenticated = True
                        success_msg = f"Connected successfully (conn: {connect_time:.3f}s, auth: {auth_time:.3f}s)"
                        print(f"[🎉] {success_msg}")
                        return True, connect_time, auth_time, success_msg
                    elif response == b'AUTH_ERR\x00':
                        self.sock.close()
                        return False, connect_time, auth_time, "Authentication failed - invalid password"
                    else:
                        self.sock.close()
                        return False, connect_time, auth_time, f"Unexpected server response: {response}"
                        
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
                print(f"[❌] {error_msg}")
                return False, 0, 0, error_msg

    def send_data(self, header, filename_bytes, image_data):
        """✅ FIXED: Enhanced data sending with progress tracking"""
        if not self._validate_connection():
            return False, "Not connected to server"
        
        try:
            print(f"[📤] Sending data: {len(image_data)} bytes")
            send_start = time.time()
            
            # ✅ FIXED: Send data in chunks for large files
            total_data = header + filename_bytes + image_data
            total_size = len(total_data)
            sent_size = 0
            chunk_size = 8192  # 8KB chunks
            
            while sent_size < total_size:
                chunk_end = min(sent_size + chunk_size, total_size)
                chunk = total_data[sent_size:chunk_end]
                
                try:
                    bytes_sent = self.sock.send(chunk)
                    sent_size += bytes_sent
                    
                    # ✅ FIXED: Progress logging for large files
                    if total_size > 100000:  # 100KB+
                        progress = (sent_size / total_size) * 100
                        if sent_size % (chunk_size * 10) == 0:  # Log every 80KB
                            print(f"[📤] Upload progress: {progress:.1f}% ({sent_size}/{total_size})")
                            
                except socket.timeout:
                    return False, f"Send timeout after {sent_size}/{total_size} bytes"
                except Exception as e:
                    return False, f"Send error at {sent_size}/{total_size} bytes: {str(e)}"
            
            send_time = time.time() - send_start
            speed_kbps = (total_size / 1024) / send_time if send_time > 0 else 0
            print(f"[✅] Data sent successfully: {total_size} bytes in {send_time:.3f}s ({speed_kbps:.1f} KB/s)")
            
            return True, send_time
            
        except Exception as e:
            error_msg = f"Failed to send data: {str(e)}"
            print(f"[❌] {error_msg}")
            return False, error_msg

    def receive_data(self):
        """✅ FIXED: Enhanced data receiving with progress tracking"""
        if not self._validate_connection():
            return False, "Not connected to server", 0
        
        try:
            print(f"[📥] Waiting for response data...")
            receive_start = time.time()
            
            # ✅ FIXED: Enhanced response length handling
            try:
                length_bytes = self._receive_exact(4, timeout=self.socket_timeout)
                expected_len = struct.unpack('>I', length_bytes)[0]
                print(f"[📥] Expecting {expected_len} bytes")
                
                if expected_len > 50 * 1024 * 1024:  # 50MB limit
                    return False, f"Response too large: {expected_len} bytes", 0
                
            except struct.error:
                return False, "Invalid response length format", 0
            except Exception as e:
                return False, f"Failed to read response length: {str(e)}", 0
            
            # ✅ FIXED: Receive data with progress tracking
            try:
                encrypted_data = self._receive_exact(expected_len, timeout=self.socket_timeout, show_progress=True)
                receive_time = time.time() - receive_start
                
                speed_kbps = (expected_len / 1024) / receive_time if receive_time > 0 else 0
                print(f"[✅] Data received successfully: {expected_len} bytes in {receive_time:.3f}s ({speed_kbps:.1f} KB/s)")
                
                return True, encrypted_data, receive_time
                
            except Exception as e:
                return False, f"Failed to receive data: {str(e)}", 0
            
        except Exception as e:
            error_msg = f"Receive operation failed: {str(e)}"
            print(f"[❌] {error_msg}")
            return False, error_msg, 0

    def send_timing_data(self, timing_data):
        """✅ FIXED: Enhanced timing data sending with validation"""
        if not self._validate_connection():
            return False
        
        try:
            # ✅ FIXED: Validate timing data
            required_fields = ['filename', 'waktu_dekripsi_client', 'ukuran_hasil_kb']
            for field in required_fields:
                if field not in timing_data:
                    print(f"[!] Missing required timing field: {field}")
                    return False
            
            print(f"[📊] Sending timing data for: {timing_data['filename']}")
            
            timing_json = json.dumps(timing_data, ensure_ascii=False).encode('utf-8')
            timing_header = b'TIMING' + struct.pack('>I', len(timing_json))
            
            # ✅ FIXED: Send with timeout
            self.sock.settimeout(5.0)  # Short timeout for timing data
            self.sock.sendall(timing_header + timing_json)
            
            # ✅ FIXED: Enhanced acknowledgment handling
            try:
                ack = self._receive_exact(3, timeout=5.0)
                if ack == b'ACK':
                    print(f"[✅] Timing data acknowledged by server")
                    return True
                else:
                    print(f"[!] Unexpected timing acknowledgment: {ack}")
                    return False
            except socket.timeout:
                print(f"[!] Timeout waiting for timing acknowledgment")
                return False
            
        except Exception as e:
            print(f"[❌] Failed to send timing data: {str(e)}")
            return False
        finally:
            # ✅ FIXED: Restore original timeout
            if self.sock:
                self.sock.settimeout(self.socket_timeout)

    def _receive_exact(self, size, timeout=None, show_progress=False):
        """✅ FIXED: Enhanced exact-size data receiving with progress tracking"""
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
                        raise ConnectionError(f"Connection closed by server after {bytes_received}/{size} bytes")
                    
                    buffer += chunk
                    bytes_received += len(chunk)
                    
                    # ✅ FIXED: Progress logging for large data
                    if show_progress and size > 50000:  # 50KB+
                        progress = (bytes_received / size) * 100
                        if progress - last_progress_log >= 10:  # Log every 10%
                            print(f"[📥] Receive progress: {progress:.1f}% ({bytes_received}/{size})")
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
        """✅ FIXED: Enhanced connection validation"""
        if not self.connected:
            print("[!] Not connected to server")
            return False
        if not self.authenticated:
            print("[!] Not authenticated with server")
            return False
        if not self.sock:
            print("[!] Socket not available")
            return False
        return True

    def disconnect(self):
        """✅ FIXED: Enhanced disconnect with cleanup"""
        with self.lock:
            if self.sock:
                try:
                    # ✅ FIXED: Graceful disconnect notification
                    if self.connected and self.authenticated:
                        try:
                            print("[🔌] Sending disconnect notification...")
                            self.sock.settimeout(2.0)  # Short timeout for disconnect
                            self.sock.sendall(b'DISCONNECT')
                        except:
                            pass  # Ignore errors during disconnect notification
                    
                    print("[🔌] Closing socket connection...")
                    self.sock.close()
                    
                except Exception as e:
                    print(f"[!] Error during disconnect: {e}")
                finally:
                    self.sock = None
            
            # ✅ FIXED: Reset state
            self.connected = False
            self.authenticated = False
            
            print("[🔌] Disconnected from server")
            return True, "Successfully disconnected from server"

    # ✅ FIXED: Additional utility methods
    
    def get_connection_status(self):
        """Get detailed connection status"""
        return {
            'connected': self.connected,
            'authenticated': self.authenticated,
            'server_host': self.server_host,
            'server_port': self.server_port,
            'socket_available': self.sock is not None,
            'connection_timeout': self.connection_timeout,
            'socket_timeout': self.socket_timeout
        }
    
    def set_timeouts(self, connection_timeout=None, socket_timeout=None, auth_timeout=None):
        """Configure network timeouts"""
        if connection_timeout:
            self.connection_timeout = connection_timeout
            print(f"[⚙️] Connection timeout set to {connection_timeout}s")
        
        if socket_timeout:
            self.socket_timeout = socket_timeout
            if self.sock:
                self.sock.settimeout(socket_timeout)
            print(f"[⚙️] Socket timeout set to {socket_timeout}s")
        
        if auth_timeout:
            self.auth_timeout = auth_timeout
            print(f"[⚙️] Auth timeout set to {auth_timeout}s")
    
    def test_connection(self):
        """Test if connection is still alive"""
        if not self._validate_connection():
            return False, "Not connected"
        
        try:
            # Send a simple ping
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
    
    def get_network_stats(self):
        """Get network performance statistics"""
        # This would be implemented with actual stats tracking
        return {
            'total_bytes_sent': 0,
            'total_bytes_received': 0,
            'average_upload_speed': 0,
            'average_download_speed': 0,
            'connection_uptime': 0,
            'total_operations': 0
        }