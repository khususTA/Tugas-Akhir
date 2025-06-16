import os
import json
from datetime import datetime, timedelta
import threading

class TimingLogger:
    def __init__(self, folder_log_client):
        self.folder_log_client = folder_log_client
        self.lock = threading.Lock()
        self.session_start = datetime.now()
        self.total_operations = 0
        
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        try:
            os.makedirs(self.folder_log_client, exist_ok=True)
        except Exception as e:
            print(f"Failed to create log directory: {e}")

    def log_connection_info(self, server_host, server_port, connect_time, auth_time, success, error=None):
        """Log connection information"""
        with self.lock:
            try:
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'server': f"{server_host}:{server_port}",
                    'connect_time': round(connect_time, 4),
                    'auth_time': round(auth_time, 4),
                    'total_time': round(connect_time + auth_time, 4),
                    'status': 'SUCCESS' if success else 'FAILED',
                    'error': error
                }
                
                log_file = os.path.join(self.folder_log_client, f"connection_{datetime.now().strftime('%Y%m%d')}.log")
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{log_data['timestamp']}] CONNECTION {log_data['status']}\n")
                    f.write(f"Server: {log_data['server']}\n")
                    f.write(f"Connection: {log_data['connect_time']}s, Auth: {log_data['auth_time']}s, Total: {log_data['total_time']}s\n")
                    
                    if success:
                        quality = "FAST" if log_data['total_time'] < 2.0 else "SLOW"
                        f.write(f"Quality: {quality}\n")
                    else:
                        f.write(f"Error: {error}\n")
                    f.write("-" * 50 + "\n")
                
                # Also save to JSON for analysis
                self._log_to_json('connection', log_data)
                
            except Exception as e:
                print(f"Failed to log connection info: {e}")

    def log_communication_timing(self, timing_data):
        """Log communication timing with essential metrics"""
        with self.lock:
            try:
                self.total_operations += 1
                
                log_file = os.path.join(self.folder_log_client, f"transfer_{datetime.now().strftime('%Y%m%d')}.log")
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timing_data['timestamp']}] {timing_data['filename']}\n")
                    f.write(f"Sizes: {timing_data['ukuran_asli_kb']:.1f}KB -> {timing_data['ukuran_hasil_kb']:.1f}KB\n")
                    f.write(f"Times: Upload {timing_data['waktu_kirim']:.3f}s, Download {timing_data['waktu_terima']:.3f}s, Decrypt {timing_data['waktu_dekripsi']:.3f}s\n")
                    f.write(f"Speeds: {timing_data['kecepatan_upload_kbps']:.1f}KB/s up, {timing_data['kecepatan_download_kbps']:.1f}KB/s down\n")
                    f.write(f"Total: {timing_data['total_waktu_komunikasi']:.3f}s\n")
                    f.write("-" * 50 + "\n")

                # Console summary
                print(f"Transfer {timing_data['filename']}: {timing_data['total_waktu_komunikasi']:.3f}s "
                      f"({timing_data['kecepatan_upload_kbps']:.0f}KB/s↑ {timing_data['kecepatan_download_kbps']:.0f}KB/s↓)")

                # Save to JSON
                self._log_to_json('transfer', timing_data)
                
            except Exception as e:
                print(f"Failed to log communication timing: {e}")

    def log_error(self, filename, error_msg):
        """Log error with basic categorization"""
        with self.lock:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_file = os.path.join(self.folder_log_client, f"errors_{datetime.now().strftime('%Y%m%d')}.log")
                
                # Simple error categorization
                if 'timeout' in error_msg.lower():
                    category = 'TIMEOUT'
                elif 'connection' in error_msg.lower():
                    category = 'NETWORK'
                elif 'decrypt' in error_msg.lower():
                    category = 'CRYPTO'
                else:
                    category = 'GENERAL'
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] ERROR - {category}\n")
                    f.write(f"File: {filename}\n")
                    f.write(f"Message: {error_msg}\n")
                    f.write("-" * 30 + "\n")

                print(f"ERROR [{category}] {filename}: {error_msg}")
                
                # Save to JSON
                error_data = {
                    'timestamp': timestamp,
                    'filename': filename,
                    'error_message': error_msg,
                    'category': category
                }
                self._log_to_json('error', error_data)
                
            except Exception as e:
                print(f"Failed to log error: {e}")

    def log_disconnection(self):
        """Log disconnection with session summary"""
        with self.lock:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                session_duration = str(datetime.now() - self.session_start).split('.')[0]
                
                log_file = os.path.join(self.folder_log_client, f"connection_{datetime.now().strftime('%Y%m%d')}.log")
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write(f"[{timestamp}] SESSION ENDED\n")
                    f.write(f"Duration: {session_duration}\n")
                    f.write(f"Operations: {self.total_operations}\n")
                    f.write("-" * 30 + "\n")

                print(f"Session ended: {self.total_operations} operations in {session_duration}")
                
            except Exception as e:
                print(f"Failed to log disconnection: {e}")

    def _log_to_json(self, log_type, data):
        """Save structured data to JSON for analysis"""
        try:
            json_file = os.path.join(self.folder_log_client, f"{log_type}_{datetime.now().strftime('%Y%m%d')}.json")
            
            # Load existing data
            json_data = []
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                except:
                    json_data = []
            
            # Add new entry and limit to 100 entries
            json_data.append(data)
            if len(json_data) > 100:
                json_data = json_data[-100:]
            
            # Save back
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"Failed to log to JSON: {e}")

    def get_session_stats(self):
        """Get basic session statistics"""
        uptime = datetime.now() - self.session_start
        return {
            'total_operations': self.total_operations,
            'session_uptime': str(uptime).split('.')[0],
            'operations_per_hour': round(self.total_operations / max(uptime.total_seconds() / 3600, 0.1), 1)
        }

    def cleanup_old_logs(self, days_to_keep=7):
        """Clean up old log files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            removed_count = 0
            
            for filename in os.listdir(self.folder_log_client):
                if filename.endswith(('.log', '.json')):
                    filepath = os.path.join(self.folder_log_client, filename)
                    file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_date < cutoff_date:
                        os.remove(filepath)
                        removed_count += 1
            
            if removed_count > 0:
                print(f"Cleaned up {removed_count} old log files")
            
            return True, f"Removed {removed_count} old files"
            
        except Exception as e:
            print(f"Failed to cleanup logs: {e}")
            return False, str(e)