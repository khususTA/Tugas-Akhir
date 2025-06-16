import socket
import struct
import hashlib
import json
import time

class ServerNetworkManager:
    def __init__(self, server_ip, server_port, password_hash, buffer_size=4096, client_timeout=60, max_concurrent_clients=10):
        """
        Initialize ServerNetworkManager dengan semua parameter yang diperlukan
        
        Args:
            server_ip (str): IP address server
            server_port (int): Port server
            password_hash (str): Hash password untuk autentikasi
            buffer_size (int): Ukuran buffer untuk transfer data
            client_timeout (int): Timeout untuk koneksi client dalam detik
            max_concurrent_clients (int): Maksimal client bersamaan
        """
        self.server_ip = server_ip
        self.server_port = server_port
        self.password_hash = password_hash
        self.buffer_size = buffer_size
        self.client_timeout = client_timeout
        self.max_concurrent_clients = max_concurrent_clients
        self.server_socket = None

    def create_server_socket(self):
        """
        Buat dan bind server socket dengan pengaturan yang optimal
        
        Returns:
            socket: Server socket yang sudah di-bind
        """
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            
            # Set timeout untuk server socket accept operations
            self.server_socket.settimeout(1.0)
            
            self.server_socket.bind((self.server_ip, self.server_port))
            self.server_socket.listen(self.max_concurrent_clients)
            
            return self.server_socket
            
        except Exception as e:
            raise Exception(f"Failed to create server socket: {e}")

    def authenticate_client(self, conn):
        """
        Handle client authentication dengan timeout yang sesuai
        
        Args:
            conn: Client connection socket
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Set timeout untuk authentication
            conn.settimeout(self.client_timeout)
            
            # Terima header AUTH
            header = conn.recv(4)
            if header != b'AUTH':
                return False, "Invalid auth header"

            # Terima password hash
            panjang_pw = struct.unpack('>I', conn.recv(4))[0]
            password_hash = conn.recv(panjang_pw).decode()
            
            if password_hash != self.password_hash:
                conn.sendall(b'AUTH_NO\x00')
                return False, "Invalid password"
            
            conn.sendall(b'AUTH_OK\x00')
            return True, "Authentication successful"
            
        except socket.timeout:
            return False, "Authentication timeout"
        except Exception as e:
            return False, f"Auth error: {e}"

    def receive_image_data(self, conn):
        """
        Terima data gambar dari client dengan timeout handling yang lebih baik
        
        Args:
            conn: Client connection socket
            
        Returns:
            tuple: (success, filename, file_data, message)
        """
        try:
            # Set timeout untuk receive operations
            conn.settimeout(self.client_timeout)
            
            # Terima header (filename_len, data_len)
            header_data = conn.recv(8)
            if not header_data:
                return False, None, None, "No header data"

            filename_len, data_len = struct.unpack('>II', header_data)
            
            # Validasi ukuran data yang masuk akal
            if filename_len > 1024 or data_len > 100 * 1024 * 1024:  # Max 100MB
                return False, None, None, "Invalid data size"
            
            # Terima filename
            filename = conn.recv(filename_len).decode()
            
            # Terima file data dengan progress tracking
            file_data = b''
            bytes_received = 0
            
            while bytes_received < data_len:
                try:
                    chunk_size = min(self.buffer_size, data_len - bytes_received)
                    chunk = conn.recv(chunk_size)
                    
                    if not chunk:
                        return False, None, None, "Connection closed during transfer"
                    
                    file_data += chunk
                    bytes_received += len(chunk)
                    
                except socket.timeout:
                    # Timeout individual chunk, bukan total timeout
                    continue
                except Exception as e:
                    return False, None, None, f"Receive error: {e}"

            return True, filename, file_data, "Data received successfully"
            
        except socket.timeout:
            return False, None, None, "Receive timeout"
        except Exception as e:
            return False, None, None, f"Receive error: {e}"

    def send_encrypted_data(self, conn, encrypted_data):
        """
        Kirim data terenkripsi ke client dengan error handling yang lebih baik
        
        Args:
            conn: Client connection socket
            encrypted_data (bytes): Data terenkripsi yang akan dikirim
            
        Returns:
            tuple: (success, message)
        """
        try:
            # Set timeout untuk send operations
            conn.settimeout(self.client_timeout)
            
            # Kirim panjang data
            conn.sendall(struct.pack('>I', len(encrypted_data)))
            
            # Kirim data terenkripsi dalam chunks untuk file besar
            bytes_sent = 0
            while bytes_sent < len(encrypted_data):
                chunk_size = min(self.buffer_size, len(encrypted_data) - bytes_sent)
                chunk = encrypted_data[bytes_sent:bytes_sent + chunk_size]
                
                conn.sendall(chunk)
                bytes_sent += len(chunk)
            
            return True, "Data sent successfully"
            
        except socket.timeout:
            return False, "Send timeout"
        except Exception as e:
            return False, f"Send error: {e}"

    def receive_client_timing_data(self, conn):
        """
        Terima data timing dari client dengan timeout yang lebih singkat
        
        Args:
            conn: Client connection socket
            
        Returns:
            dict atau None: Data timing dari client
        """
        try:
            # Timeout lebih singkat untuk timing data karena optional
            conn.settimeout(2.0)
            
            # Baca header TIMING
            header = conn.recv(6)
            if header != b'TIMING':
                return None

            # Baca panjang data JSON
            json_len = struct.unpack('>I', conn.recv(4))[0]
            
            # Validasi ukuran JSON yang masuk akal
            if json_len > 10240:  # Max 10KB untuk timing data
                return None
            
            # Baca data JSON
            json_data = conn.recv(json_len).decode('utf-8')
            timing_data = json.loads(json_data)
            
            # Kirim acknowledgment
            conn.sendall(b'ACK')
            
            return timing_data
            
        except (socket.timeout, json.JSONDecodeError, struct.error):
            return None
        except Exception:
            return None

    def close_server_socket(self):
        """
        Tutup server socket dengan cleanup yang proper
        """
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
            self.server_socket = None

    def get_connection_info(self):
        """
        Dapatkan informasi konfigurasi koneksi
        
        Returns:
            dict: Informasi konfigurasi network
        """
        return {
            'server_ip': self.server_ip,
            'server_port': self.server_port,
            'buffer_size': self.buffer_size,
            'client_timeout': self.client_timeout,
            'max_concurrent_clients': self.max_concurrent_clients,
            'server_socket_active': self.server_socket is not None
        }

    def set_client_timeout(self, timeout):
        """
        Ubah timeout client secara dinamis
        
        Args:
            timeout (int): Timeout baru dalam detik
        """
        self.client_timeout = timeout

    def validate_connection(self, conn):
        """
        Validasi koneksi client masih aktif
        
        Args:
            conn: Client connection socket
            
        Returns:
            bool: True jika koneksi masih aktif
        """
        try:
            # Test koneksi dengan mengirim data kosong
            conn.send(b'')
            return True
        except:
            return False