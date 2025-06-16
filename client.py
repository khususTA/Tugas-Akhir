import webview
import base64
import struct
import os
import json
import time
from datetime import datetime

# Import modul yang dipisahkan
from client_modules.network_manager import NetworkManager
from client_modules.history_manager import HistoryManager
from client_modules.timing_logger import TimingLogger
from client_modules.decryption_manager import CryptoManager

SERVER_HOST = '192.168.29.138'
SERVER_PORT = 12345

# Auto create folders in client_data/
BASE_CLIENT_FOLDER = "client_data"
FOLDER_HASIL = os.path.join(BASE_CLIENT_FOLDER, "hasil_dekripsi")
FOLDER_HISTORY = os.path.join(BASE_CLIENT_FOLDER, "cache_history")
FOLDER_LOG_CLIENT = os.path.join(BASE_CLIENT_FOLDER, "client_logs")
AES_KEY = b'tEaXKE1f8Xe8k3SlVRMGxQAoGIcDAq0C'

# Create all client folders
os.makedirs(FOLDER_HASIL, exist_ok=True)
os.makedirs(FOLDER_HISTORY, exist_ok=True)
os.makedirs(FOLDER_LOG_CLIENT, exist_ok=True)

class ClientApp:
    def __init__(self):
        # Inisialisasi semua manager
        self.network_manager = NetworkManager(SERVER_HOST, SERVER_PORT)
        self.history_manager = HistoryManager(os.path.join(FOLDER_HISTORY, "detections.json"))
        self.timing_logger = TimingLogger(FOLDER_LOG_CLIENT)
        self.crypto_manager = CryptoManager(AES_KEY)
        
        # ✅ FIXED: Connection state tracking
        self.webview_window = None
        self.is_webview_ready = False
        
        print("🌾 PestDetect Client v2.2 - UI Update Sequence Fixed")

    def connect_to_server(self, password):
        """✅ FIXED: Enhanced connection with better UI synchronization"""
        success, connect_time, auth_time, message = self.network_manager.connect_to_server(password)
        
        # Log koneksi
        self.timing_logger.log_connection_info(SERVER_HOST, SERVER_PORT, connect_time, auth_time, success, None if success else message)
        
        if success:
            # ✅ FIXED: Wait for webview to be ready before loading history
            self._ensure_webview_ready()
            
            # ✅ FIXED: Load history with proper error handling and timing
            try:
                print("[📊] Loading history after successful connection...")
                # Small delay to ensure UI is fully initialized
                time.sleep(0.1)
                
                self.history_manager.load_history_to_ui(self.webview_window)
                print("[📊] History loading completed successfully")
                
            except Exception as e:
                print(f"[!] Failed to load history after connection: {e}")
                # ✅ FIXED: Try to send empty history if loading fails
                self._safe_js_call("if(window.loadHistoryFromBackend) { window.loadHistoryFromBackend([]); }")
        else:
            print(f"[!] Connection failed: {message}")
        
        return success, message

    def send_image(self, filename, base64data):
        """✅ FIXED: Optimized UI update sequence and error handling"""
        if not self.network_manager.connected or not self.network_manager.authenticated:
            return False, "Belum terhubung ke server"

        # ✅ FIXED: Ensure webview is ready
        self._ensure_webview_ready()

        try:
            # === TIMING: Persiapan data ===
            prep_start = time.time()
            image_data = base64.b64decode(base64data.split(',')[1])
            filename_bytes = filename.encode('utf-8')
            header = struct.pack('>II', len(filename_bytes), len(image_data))
            prep_time = time.time() - prep_start

            # === TIMING: Kirim data ke server ===
            success, send_time = self.network_manager.send_data(header, filename_bytes, image_data)
            if not success:
                return False, send_time  # send_time contains error message

            # === TIMING: Terima data dari server ===
            success, encrypted_data, receive_time = self.network_manager.receive_data()
            if not success:
                return False, encrypted_data  # encrypted_data contains error message

            # === TIMING: Dekripsi data ===
            decrypt_start = time.time()
            hasil_bytes = self.crypto_manager.decrypt_data(encrypted_data)
            decrypt_time = time.time() - decrypt_start

            # === TIMING: Simpan file ===
            save_start = time.time()
            path_hasil = os.path.join(FOLDER_HASIL, "hasil_" + filename)
            with open(path_hasil, "wb") as f:
                f.write(hasil_bytes)
            save_time = time.time() - save_start

            # Hitung total waktu dan kecepatan
            total_time = send_time + receive_time
            upload_speed = (len(image_data) / 1024) / send_time if send_time > 0 else 0
            download_speed = (len(encrypted_data) / 1024) / receive_time if receive_time > 0 else 0

            # === KIRIM DATA TIMING DEKRIPSI KE SERVER ===
            timing_data_for_server = {
                'filename': filename,
                'waktu_dekripsi_client': round(decrypt_time, 4),
                'ukuran_hasil_kb': len(hasil_bytes) / 1024,
                'waktu_simpan_client': round(save_time, 4)
            }
            
            self.network_manager.send_timing_data(timing_data_for_server)

            # Data timing lengkap untuk log client
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

            # === ✅ FIXED: OPTIMIZED UI UPDATE SEQUENCE ===
            
            # STEP 1: Save detection to history first (data persistence)
            print("[📝] Saving detection to history...")
            detection_data = self.history_manager.save_new_detection(filename, path_hasil, full_timing_data, hasil_bytes)
            
            # STEP 2: Prepare result image data
            b64_result = "data:image/jpeg;base64," + base64.b64encode(hasil_bytes).decode()
            
            # STEP 3: Update status immediately
            status_msg = f"Berhasil - Upload: {send_time:.2f}s, Download: {receive_time:.2f}s, Dekripsi: {decrypt_time:.3f}s"
            self._safe_js_call(f"updateStatus('{status_msg}')")
            
            # STEP 4: Display result image to user
            print("[🖼️] Displaying result image...")
            self._safe_js_call(f"tampilkanHasil('{b64_result}')")
            
            # Small delay to ensure tampilkanHasil is processed
            time.sleep(0.05)
            
            # STEP 5: Add to history UI (this should be after result is shown)
            print("[📊] Adding detection to history UI...")
            self._add_detection_to_ui_safe(detection_data, full_timing_data)

            return True, status_msg
            
        except Exception as e:
            error_msg = f"Gagal proses gambar: {e}"
            self.timing_logger.log_error(filename, error_msg)
            print(f"[!] Error in send_image: {e}")
            return False, error_msg

    def _add_detection_to_ui_safe(self, detection_data, timing_data):
        """✅ FIXED: Safe method to add detection to UI with proper error handling"""
        try:
            # Format data yang konsisten dengan frontend
            ui_detection_data = {
                'id': detection_data['id'],
                'filename': detection_data['filename'], 
                'timestamp': detection_data['timestamp'],
                'resultImage': detection_data['resultImage'],  # ✅ FIXED: Use consistent field name
                'results': {
                    'totalDetections': 1,
                    'avgConfidence': 85,
                    'detections': [{'name': 'Hama Terdeteksi', 'confidence': 85}],
                    'recommendations': ['Pantau area terinfeksi', 'Aplikasikan treatment sesuai anjuran']
                },
                'processingTime': timing_data['total_waktu_komunikasi'],
                'timing': timing_data
            }
            
            # ✅ FIXED: Use history manager method for consistent UI update
            self.history_manager.add_detection_to_ui(self.webview_window, ui_detection_data)
            
        except Exception as e:
            print(f"[!] Error adding detection to UI: {e}")
            # ✅ FIXED: Fallback - try direct JS call
            try:
                self._safe_js_call("if(window.app && window.app.updateTodayStats) { window.app.updateTodayStats(); }")
            except:
                pass

    def _ensure_webview_ready(self):
        """✅ FIXED: Ensure webview window is ready for JS calls"""
        if not self.webview_window and webview.windows:
            self.webview_window = webview.windows[0]
            self.is_webview_ready = True
            print("[🌐] WebView window reference established")
        
        # Additional check for window readiness
        if self.webview_window and not self.is_webview_ready:
            try:
                # Test if we can execute JS
                self.webview_window.evaluate_js("console.log('WebView ready test')")
                self.is_webview_ready = True
                print("[🌐] WebView window confirmed ready")
            except Exception as e:
                print(f"[!] WebView not ready yet: {e}")
                self.is_webview_ready = False

    def _safe_js_call(self, js_code, max_retries=3):
        """✅ FIXED: Safe JavaScript execution with retry mechanism"""
        if not self.webview_window:
            self._ensure_webview_ready()
        
        if not self.webview_window:
            print("[!] WebView window not available for JS call")
            return False
        
        for attempt in range(max_retries):
            try:
                self.webview_window.evaluate_js(js_code)
                return True
            except Exception as e:
                print(f"[!] JS call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(0.1)  # Small delay before retry
                else:
                    print(f"[!] JS call failed after {max_retries} attempts: {js_code[:50]}...")
                    return False
        
        return False

    def get_detection_stats(self):
        """Get statistics untuk UI"""
        return self.history_manager.get_detection_stats()

    def clear_detection_history(self):
        """✅ FIXED: Clear detection history with improved UI synchronization"""
        try:
            # ✅ FIXED: Ensure webview is ready
            self._ensure_webview_ready()
            
            success, message = self.history_manager.clear_detection_history(self.webview_window)
            
            if success:
                # ✅ FIXED: Additional UI cleanup
                self._safe_js_call("if(window.app && window.app.updateTodayStats) { window.app.updateTodayStats(); }")
                print("[📊] History cleared and UI updated")
            
            return success, message
        except Exception as e:
            error_msg = f"Gagal clear history: {e}"
            print(f"[!] Error in clear_detection_history: {e}")
            return False, error_msg

    def export_detection_report(self):
        """Export detection report as JSON"""
        try:
            return self.history_manager.export_detection_report(FOLDER_HISTORY)
        except Exception as e:
            print(f"[!] Error exporting report: {e}")
            return False, f"Gagal export report: {e}"

    def disconnect(self):
        """✅ FIXED: Enhanced disconnect with UI state management"""
        try:
            success, message = self.network_manager.disconnect()
            self.timing_logger.log_disconnection()
            
            # ✅ FIXED: Update UI connection state
            if self.webview_window:
                self._safe_js_call("if(window.app && window.app.setConnectionState) { window.app.setConnectionState('disconnected'); }")
            
            print(f"[🔌] Disconnected: {message}")
            return success, message
        except Exception as e:
            print(f"[!] Error in disconnect: {e}")
            return False, f"Gagal disconnect: {e}"

    # ✅ FIXED: Additional utility methods for better error handling
    
    def _log_js_error(self, operation, error, js_code=None):
        """Log JavaScript execution errors"""
        print(f"[!] JS Error in {operation}: {error}")
        if js_code:
            print(f"[!] Failed JS Code: {js_code[:100]}...")
    
    def _validate_connection_state(self):
        """Validate connection state before operations"""
        if not self.network_manager.connected:
            raise ConnectionError("Not connected to server")
        if not self.network_manager.authenticated:
            raise ConnectionError("Not authenticated with server")
        return True
    
    def _get_connection_info(self):
        """Get current connection information"""
        return {
            'connected': self.network_manager.connected,
            'authenticated': self.network_manager.authenticated,
            'server_host': SERVER_HOST,
            'server_port': SERVER_PORT,
            'webview_ready': self.is_webview_ready
        }

def start_client():
    """✅ FIXED: Enhanced client startup with better error handling"""
    try:
        client_api = ClientApp()
        
        # ✅ FIXED: Create window with error handling
        window = webview.create_window(
            title="PestDetect v2.2 - UI Update Sequence Fixed",
            url="./ui/index.html",
            js_api=client_api,
            width=960,
            height=640,
            resizable=True
        )
        
        # ✅ FIXED: Set webview window reference immediately
        client_api.webview_window = window
        
        print("=" * 70)
        print("🌾 PESTDETECT CLIENT v2.2 - UI Update Sequence Fixed")
        print("=" * 70)
        print(f"[+] Folder hasil: {FOLDER_HASIL}")
        print(f"[+] Detection history: {client_api.history_manager.history_file}")
        print(f"[+] Folder log: {FOLDER_LOG_CLIENT}")
        print(f"[+] Target server: {SERVER_HOST}:{SERVER_PORT}")
        print("[+] HISTORY SYSTEM: Persistent detection records with auto-sync")
        print("[+] UI UPDATE: Optimized sequence for better user experience")
        print("[+] ERROR HANDLING: Enhanced robustness and retry mechanisms")
        print("=" * 70)
        
        # ✅ FIXED: Start with error handling
        try:
            webview.start(debug=False)
        except Exception as e:
            print(f"[!] Error starting webview: {e}")
            raise
            
    except Exception as e:
        print(f"[!] Fatal error starting client: {e}")
        raise

if __name__ == '__main__':
    try:
        start_client()
    except KeyboardInterrupt:
        print("\n[🛑] Client stopped by user")
    except Exception as e:
        print(f"[💥] Fatal error: {e}")
        exit(1)