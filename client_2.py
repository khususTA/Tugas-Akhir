import webview
import base64
import struct
import os
import time
from datetime import datetime

# Import optimized modules
from client_modules_2.network_manager import NetworkManager
from client_modules_2.history_manager import HistoryManager
from client_modules_2.timing_logger import TimingLogger
from client_modules_2.decryption_manager import CryptoManager

SERVER_HOST = '192.168.29.138'
SERVER_PORT = 12345

# Auto create folders
BASE_CLIENT_FOLDER = "client_data"
FOLDER_HASIL = os.path.join(BASE_CLIENT_FOLDER, "hasil_dekripsi")
FOLDER_HISTORY = os.path.join(BASE_CLIENT_FOLDER, "cache_history")
FOLDER_LOG_CLIENT = os.path.join(BASE_CLIENT_FOLDER, "client_logs")
AES_KEY = b'tEaXKE1f8Xe8k3SlVRMGxQAoGIcDAq0C'

# Create folders
os.makedirs(FOLDER_HASIL, exist_ok=True)
os.makedirs(FOLDER_HISTORY, exist_ok=True)
os.makedirs(FOLDER_LOG_CLIENT, exist_ok=True)

# ✅ FIXED: Global reference to client app for frontend_ready signal
client_app_instance = None

class ClientApp:
    def __init__(self):
        global client_app_instance
        client_app_instance = self  # ✅ FIXED: Set global reference
        
        # Initialize managers
        self.network_manager = NetworkManager(SERVER_HOST, SERVER_PORT)
        self.history_manager = HistoryManager(os.path.join(FOLDER_HISTORY, "detections.json"))
        self.timing_logger = TimingLogger(FOLDER_LOG_CLIENT)
        self.crypto_manager = CryptoManager(AES_KEY)
        
        # Connection state
        self.webview_window = None
        self.frontend_ready = False  # Track frontend readiness
        
        print("🌾 PestDetect Client v2.2 (Final Fixed)")

    def connect_to_server(self, password):
        """Connect to server with improved history synchronization"""
        success, connect_time, auth_time, message = self.network_manager.connect_to_server(password)
        
        # Log connection
        self.timing_logger.log_connection_info(SERVER_HOST, SERVER_PORT, connect_time, auth_time, success, None if success else message)
        
        if success:
            print("✅ Connected successfully")
            # ✅ FIXED: Load history immediately if frontend is already ready
            if self.frontend_ready:
                self._load_history_safe()
            else:
                print("⏳ Waiting for frontend ready signal to load history...")
        else:
            print(f"❌ Connection failed: {message}")
        
        return success, message

    def on_frontend_ready(self):
        """Called when frontend signals it's ready"""
        print("🎯 Frontend ready signal received")
        self.frontend_ready = True
        
        # Load history if connected
        if self.network_manager.connected:
            self._load_history_safe()
        else:
            print("⚠️ Frontend ready but not connected to server")

    def _load_history_safe(self):
        """Safely load history with proper error handling"""
        try:
            print("📊 Loading history to UI...")
            time.sleep(0.2)  # Small delay for UI stability
            self._ensure_webview_ready()
            self.history_manager.load_history_to_ui(self.webview_window)
            print("✅ History loaded successfully")
        except Exception as e:
            print(f"❌ Failed to load history: {e}")
            # Fallback to empty history
            try:
                self._safe_js_call("if(window.loadHistoryFromBackend) { window.loadHistoryFromBackend([]); }")
            except Exception as fallback_error:
                print(f"❌ Fallback also failed: {fallback_error}")

    def send_image(self, filename, base64data):
        """Send image with optimized UI update sequence"""
        if not self.network_manager.connected or not self.network_manager.authenticated:
            return False, "Belum terhubung ke server"

        self._ensure_webview_ready()

        try:
            # Prepare data
            prep_start = time.time()
            image_data = base64.b64decode(base64data.split(',')[1])
            filename_bytes = filename.encode('utf-8')
            header = struct.pack('>II', len(filename_bytes), len(image_data))
            prep_time = time.time() - prep_start

            # Send data to server
            success, send_time = self.network_manager.send_data(header, filename_bytes, image_data)
            if not success:
                return False, send_time

            # Receive data from server
            success, encrypted_data, receive_time = self.network_manager.receive_data()
            if not success:
                return False, encrypted_data

            # Decrypt data
            decrypt_start = time.time()
            hasil_bytes = self.crypto_manager.decrypt_data(encrypted_data)
            decrypt_time = time.time() - decrypt_start

            # Save file
            save_start = time.time()
            path_hasil = os.path.join(FOLDER_HASIL, "hasil_" + filename)
            with open(path_hasil, "wb") as f:
                f.write(hasil_bytes)
            save_time = time.time() - save_start

            # Calculate metrics
            total_time = send_time + receive_time
            upload_speed = (len(image_data) / 1024) / send_time if send_time > 0 else 0
            download_speed = (len(encrypted_data) / 1024) / receive_time if receive_time > 0 else 0

            # Send timing data to server
            timing_data_for_server = {
                'filename': filename,
                'waktu_dekripsi_client': round(decrypt_time, 4),
                'ukuran_hasil_kb': len(hasil_bytes) / 1024,
                'waktu_simpan_client': round(save_time, 4)
            }
            
            self.network_manager.send_timing_data(timing_data_for_server)

            # Full timing data for client log
            full_timing_data = {
                'filename': filename,
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'ukuran_asli_kb': len(image_data) / 1024,
                'ukuran_terenkripsi_kb': len(encrypted_data) / 1024,
                'ukuran_hasil_kb': len(hasil_bytes) / 1024,
                'waktu_persiapan': round(prep_time, 4),
                'waktu_kirim': round(send_time, 4),
                'waktu_terima': round(receive_time, 4),
                'waktu_dekripsi': round(decrypt_time, 4),
                'waktu_simpan': round(save_time, 4),
                'total_waktu_komunikasi': round(total_time, 4),
                'total_waktu_proses': round(prep_time + decrypt_time + save_time, 4),
                'kecepatan_upload_kbps': round(upload_speed, 1),
                'kecepatan_download_kbps': round(download_speed, 1),
                'efisiensi_kompresi': round((len(encrypted_data) / len(image_data)) * 100, 1)
            }
            
            self.timing_logger.log_communication_timing(full_timing_data)

            # UI Update Sequence
            print("Saving detection to history...")
            detection_data = self.history_manager.save_new_detection(filename, path_hasil, full_timing_data, hasil_bytes)
            
            # Prepare result image
            b64_result = "data:image/jpeg;base64," + base64.b64encode(hasil_bytes).decode()
            
            # Update status
            status_msg = f"Success - Upload: {send_time:.2f}s, Download: {receive_time:.2f}s, Decrypt: {decrypt_time:.3f}s"
            self._safe_js_call(f"updateStatus('{status_msg}')")
            
            # Display result
            print("Displaying result image...")
            self._safe_js_call(f"tampilkanHasil('{b64_result}')")
            
            time.sleep(0.05)  # Brief delay
            
            # Add to history UI
            print("Adding to history UI...")
            self._add_detection_to_ui_safe(detection_data, full_timing_data)

            return True, status_msg
            
        except Exception as e:
            error_msg = f"Failed to process image: {e}"
            self.timing_logger.log_error(filename, error_msg)
            print(f"Error in send_image: {e}")
            return False, error_msg

    def _add_detection_to_ui_safe(self, detection_data, timing_data):
        """Safe method to add detection to UI"""
        try:
            ui_detection_data = {
                'id': detection_data['id'],
                'filename': detection_data['filename'], 
                'timestamp': detection_data['timestamp'],
                'resultImage': detection_data['result_base64'],
                'results': {
                    'totalDetections': 1,
                    'avgConfidence': 85,
                    'detections': [{'name': 'Hama Terdeteksi', 'confidence': 85}],
                    'recommendations': ['Pantau area terinfeksi', 'Aplikasikan treatment sesuai anjuran']
                },
                'processingTime': timing_data['total_waktu_komunikasi'],
                'timing': timing_data
            }
            
            self.history_manager.add_detection_to_ui(self.webview_window, ui_detection_data)
            
        except Exception as e:
            print(f"Error adding detection to UI: {e}")
            # Fallback
            try:
                self._safe_js_call("if(window.app && window.app.updateTodayStats) { window.app.updateTodayStats(); }")
            except:
                pass

    def _ensure_webview_ready(self):
        """Ensure webview window is ready"""
        if not self.webview_window and webview.windows:
            self.webview_window = webview.windows[0]
            print("WebView window reference established")

    def _safe_js_call(self, js_code, max_retries=3):
        """Safe JavaScript execution with retry"""
        if not self.webview_window:
            self._ensure_webview_ready()
        
        if not self.webview_window:
            print("WebView window not available")
            return False
        
        for attempt in range(max_retries):
            try:
                self.webview_window.evaluate_js(js_code)
                return True
            except Exception as e:
                print(f"JS call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.1)
                else:
                    print(f"JS call failed after {max_retries} attempts")
                    return False
        
        return False

    def get_detection_stats(self):
        """Get statistics for UI"""
        return self.history_manager.get_detection_stats()

    def clear_detection_history(self):
        """Clear detection history with UI sync"""
        try:
            self._ensure_webview_ready()
            success, message = self.history_manager.clear_detection_history(self.webview_window)
            
            if success:
                self._safe_js_call("if(window.app && window.app.updateTodayStats) { window.app.updateTodayStats(); }")
                print("History cleared and UI updated")
            
            return success, message
        except Exception as e:
            error_msg = f"Failed to clear history: {e}"
            print(f"Error in clear_detection_history: {e}")
            return False, error_msg

    def export_detection_report(self):
        """Export detection report"""
        try:
            return self.history_manager.export_detection_report(FOLDER_HISTORY)
        except Exception as e:
            print(f"Error exporting report: {e}")
            return False, f"Failed to export report: {e}"

    def disconnect(self):
        """Disconnect with UI state management"""
        try:
            success, message = self.network_manager.disconnect()
            self.timing_logger.log_disconnection()
            
            # Reset frontend ready state
            self.frontend_ready = False
            
            # Update UI connection state
            if self.webview_window:
                self._safe_js_call("if(window.app && window.app.setConnectionState) { window.app.setConnectionState('disconnected'); }")
            
            print(f"Disconnected: {message}")
            return success, message
        except Exception as e:
            print(f"Error in disconnect: {e}")
            return False, f"Failed to disconnect: {e}"

    def get_connection_info(self):
        """Get current connection information"""
        return {
            'connected': self.network_manager.connected,
            'authenticated': self.network_manager.authenticated,
            'server_host': SERVER_HOST,
            'server_port': SERVER_PORT
        }

class JSApi:
    """✅ FIXED: Simplified JSApi without circular references"""
    
    def __init__(self, connect_func, send_func, disconnect_func):
        self._connect = connect_func
        self._send = send_func
        self._disconnect = disconnect_func

    def frontend_ready(self):
        """Called when frontend is ready"""
        global client_app_instance
        if client_app_instance:
            client_app_instance.on_frontend_ready()
        else:
            print("❌ Client app instance not available")
        
    def connect_to_server(self, password):
        return self._connect(password)

    def send_image(self, filename, base64data):
        return self._send(filename, base64data)

    def disconnect(self):
        return self._disconnect()

def start_client():
    """Start client with basic error handling"""
    try:
        client_api = ClientApp()
        
        # ✅ FIXED: Simplified JSApi without circular reference
        js_api = JSApi(
            client_api.connect_to_server,
            client_api.send_image,
            client_api.disconnect
        )
        
        # Create window
        window = webview.create_window(
            title="JAGAPADI v2.2 (Final Fixed)",
            url="./ui_2/index.html",
            js_api=js_api,
            width=960,
            height=640,
            resizable=True
        )
        
        # Set webview window reference
        client_api.webview_window = window
        
        print("=" * 50)
        print("🌾 PESTDETECT CLIENT v2.2 (Final Fixed)")
        print("=" * 50)
        print(f"Results folder: {FOLDER_HASIL}")
        print(f"History file: {client_api.history_manager.history_file}")
        print(f"Logs folder: {FOLDER_LOG_CLIENT}")
        print(f"Target server: {SERVER_HOST}:{SERVER_PORT}")
        print("FINAL FIX: PyWebView circular reference and timing issues resolved")
        print("=" * 50)
        
        # Start webview
        try:
            webview.start(debug=False)
        except Exception as e:
            print(f"Error starting webview: {e}")
            raise
            
    except Exception as e:
        print(f"Fatal error starting client: {e}")
        raise

if __name__ == '__main__':
    try:
        start_client()
    except KeyboardInterrupt:
        print("\nClient stopped by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        exit(1)