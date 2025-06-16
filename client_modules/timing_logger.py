import os
import json
from datetime import datetime, timedelta
import threading

class TimingLogger:
    def __init__(self, folder_log_client):
        self.folder_log_client = folder_log_client
        self.lock = threading.Lock()
        
        # ✅ FIXED: Enhanced configuration
        self.max_log_size_mb = 10  # Maximum log file size in MB
        self.max_log_files = 5     # Maximum number of log files to keep
        self.performance_stats = {
            'total_operations': 0,
            'total_upload_time': 0,
            'total_download_time': 0,
            'total_bytes_uploaded': 0,
            'total_bytes_downloaded': 0,
            'session_start': datetime.now()
        }
        
        print(f"[📊] TimingLogger initialized - Log folder: {folder_log_client}")
        self._ensure_log_directory()

    def _ensure_log_directory(self):
        """Ensure log directory exists"""
        try:
            os.makedirs(self.folder_log_client, exist_ok=True)
        except Exception as e:
            print(f"[!] Failed to create log directory: {e}")

    def log_connection_info(self, server_host, server_port, connect_time, auth_time, success, error=None):
        """✅ FIXED: Enhanced connection logging with better formatting"""
        with self.lock:
            try:
                log_data = {
                    'timestamp': datetime.now().isoformat(),
                    'server': f"{server_host}:{server_port}",
                    'waktu_koneksi': round(connect_time, 4),
                    'waktu_autentikasi': round(auth_time, 4),
                    'total_waktu': round(connect_time + auth_time, 4),
                    'status': 'SUCCESS' if success else 'FAILED',
                    'error': error
                }
                
                # ✅ FIXED: Enhanced log formatting
                log_file = os.path.join(self.folder_log_client, f"connection_{datetime.now().strftime('%Y%m%d')}.log")
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write("=" * 60 + "\n")
                    f.write(f"[{log_data['timestamp']}] CONNECTION {log_data['status']}\n")
                    f.write("=" * 60 + "\n")
                    f.write(f"Target Server    : {log_data['server']}\n")
                    f.write(f"Connection Time  : {log_data['waktu_koneksi']:.4f}s\n")
                    f.write(f"Authentication   : {log_data['waktu_autentikasi']:.4f}s\n")
                    f.write(f"Total Time       : {log_data['total_waktu']:.4f}s\n")
                    
                    if success:
                        f.write(f"Status           : ✅ CONNECTED\n")
                        # ✅ FIXED: Connection quality assessment
                        if log_data['total_waktu'] < 1.0:
                            f.write(f"Quality          : 🚀 EXCELLENT (< 1s)\n")
                        elif log_data['total_waktu'] < 3.0:
                            f.write(f"Quality          : ✅ GOOD (< 3s)\n")
                        elif log_data['total_waktu'] < 5.0:
                            f.write(f"Quality          : ⚠️  SLOW (< 5s)\n")
                        else:
                            f.write(f"Quality          : 🐌 VERY SLOW (> 5s)\n")
                    else:
                        f.write(f"Status           : ❌ FAILED\n")
                        f.write(f"Error Details    : {error}\n")
                        
                        # ✅ FIXED: Error categorization
                        if "timeout" in str(error).lower():
                            f.write(f"Error Category   : ⏰ TIMEOUT\n")
                        elif "refused" in str(error).lower():
                            f.write(f"Error Category   : 🚫 CONNECTION_REFUSED\n")
                        elif "dns" in str(error).lower():
                            f.write(f"Error Category   : 🌐 DNS_ERROR\n")
                        else:
                            f.write(f"Error Category   : ❓ UNKNOWN\n")
                    
                    f.write("=" * 60 + "\n\n")
                
                # ✅ FIXED: Also log to JSON for analysis
                self._log_to_json('connection', log_data)
                
                # ✅ FIXED: Rotate log if needed
                self._rotate_log_if_needed(log_file)
                
            except Exception as e:
                print(f"[!] Failed to log connection info: {e}")

    def log_communication_timing(self, timing_data):
        """✅ FIXED: Enhanced communication timing with performance analysis"""
        with self.lock:
            try:
                # ✅ FIXED: Update performance stats
                self.performance_stats['total_operations'] += 1
                self.performance_stats['total_upload_time'] += timing_data.get('waktu_kirim', 0)
                self.performance_stats['total_download_time'] += timing_data.get('waktu_terima', 0)
                self.performance_stats['total_bytes_uploaded'] += timing_data.get('ukuran_asli_kb', 0) * 1024
                self.performance_stats['total_bytes_downloaded'] += timing_data.get('ukuran_hasil_kb', 0) * 1024
                
                log_file = os.path.join(self.folder_log_client, f"transfer_{datetime.now().strftime('%Y%m%d')}.log")
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write("=" * 80 + "\n")
                    f.write(f"[{timing_data['timestamp']}] FILE TRANSFER: {timing_data['filename']}\n")
                    f.write("=" * 80 + "\n")
                    
                    # ✅ FIXED: File size analysis
                    f.write("📁 FILE INFORMATION:\n")
                    f.write(f"   Original Size     : {timing_data['ukuran_asli_kb']:.2f} KB\n")
                    f.write(f"   Encrypted Size    : {timing_data['ukuran_terenkripsi_kb']:.2f} KB\n")
                    f.write(f"   Result Size       : {timing_data['ukuran_hasil_kb']:.2f} KB\n")
                    f.write(f"   Compression Ratio : {timing_data['efisiensi_kompresi']:.1f}%\n")
                    
                    # ✅ FIXED: Timing breakdown
                    f.write("\n⏱️  TIMING BREAKDOWN:\n")
                    f.write(f"   Preparation       : {timing_data['waktu_persiapan']:.4f}s\n")
                    f.write(f"   Upload            : {timing_data['waktu_kirim']:.4f}s\n")
                    f.write(f"   Download          : {timing_data['waktu_terima']:.4f}s\n")
                    f.write(f"   Decryption        : {timing_data['waktu_dekripsi']:.4f}s\n")
                    f.write(f"   File Save         : {timing_data['waktu_simpan']:.4f}s\n")
                    
                    # ✅ FIXED: Performance metrics
                    f.write("\n🚀 PERFORMANCE METRICS:\n")
                    f.write(f"   Total Communication : {timing_data['total_waktu_komunikasi']:.4f}s\n")
                    f.write(f"   Total Processing    : {timing_data['total_waktu_proses']:.4f}s\n")
                    f.write(f"   Upload Speed        : {timing_data['kecepatan_upload_kbps']:.1f} KB/s\n")
                    f.write(f"   Download Speed      : {timing_data['kecepatan_download_kbps']:.1f} KB/s\n")
                    
                    # ✅ FIXED: Performance assessment
                    upload_speed = timing_data['kecepatan_upload_kbps']
                    download_speed = timing_data['kecepatan_download_kbps']
                    
                    f.write("\n📊 PERFORMANCE ASSESSMENT:\n")
                    
                    # Upload speed assessment
                    if upload_speed > 1000:
                        f.write(f"   Upload Quality    : 🚀 EXCELLENT (> 1 MB/s)\n")
                    elif upload_speed > 500:
                        f.write(f"   Upload Quality    : ✅ GOOD (> 500 KB/s)\n")
                    elif upload_speed > 100:
                        f.write(f"   Upload Quality    : ⚠️  AVERAGE (> 100 KB/s)\n")
                    else:
                        f.write(f"   Upload Quality    : 🐌 SLOW (< 100 KB/s)\n")
                    
                    # Download speed assessment
                    if download_speed > 1000:
                        f.write(f"   Download Quality  : 🚀 EXCELLENT (> 1 MB/s)\n")
                    elif download_speed > 500:
                        f.write(f"   Download Quality  : ✅ GOOD (> 500 KB/s)\n")
                    elif download_speed > 100:
                        f.write(f"   Download Quality  : ⚠️  AVERAGE (> 100 KB/s)\n")
                    else:
                        f.write(f"   Download Quality  : 🐌 SLOW (< 100 KB/s)\n")
                    
                    # ✅ FIXED: Session statistics
                    avg_upload = self.performance_stats['total_upload_time'] / max(self.performance_stats['total_operations'], 1)
                    avg_download = self.performance_stats['total_download_time'] / max(self.performance_stats['total_operations'], 1)
                    
                    f.write(f"\n📈 SESSION STATISTICS:\n")
                    f.write(f"   Total Operations  : {self.performance_stats['total_operations']}\n")
                    f.write(f"   Average Upload    : {avg_upload:.4f}s\n")
                    f.write(f"   Average Download  : {avg_download:.4f}s\n")
                    f.write(f"   Session Uptime    : {self._get_session_uptime()}\n")
                    
                    f.write("=" * 80 + "\n\n")

                # ✅ FIXED: Console output with performance info
                print(f"[📊] Transfer {timing_data['filename']}: "
                      f"Up={timing_data['waktu_kirim']:.3f}s "
                      f"Down={timing_data['waktu_terima']:.3f}s "
                      f"Decrypt={timing_data['waktu_dekripsi']:.3f}s "
                      f"Speed={timing_data['kecepatan_upload_kbps']:.1f}KB/s↑ "
                      f"{timing_data['kecepatan_download_kbps']:.1f}KB/s↓ "
                      f"Session#{self.performance_stats['total_operations']}")

                # ✅ FIXED: Log to JSON for analysis
                self._log_to_json('transfer', timing_data)
                
                # ✅ FIXED: Rotate log if needed
                self._rotate_log_if_needed(log_file)
                
            except Exception as e:
                print(f"[!] Failed to log communication timing: {e}")

    def log_error(self, filename, error_msg):
        """✅ FIXED: Enhanced error logging with categorization"""
        with self.lock:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_file = os.path.join(self.folder_log_client, f"errors_{datetime.now().strftime('%Y%m%d')}.log")
                
                # ✅ FIXED: Error categorization
                error_category = self._categorize_error(error_msg)
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write("⚠️ " + "=" * 60 + "\n")
                    f.write(f"[{timestamp}] ERROR OCCURRED\n")
                    f.write("⚠️ " + "=" * 60 + "\n")
                    f.write(f"File             : {filename}\n")
                    f.write(f"Error Category   : {error_category}\n")
                    f.write(f"Error Message    : {error_msg}\n")
                    f.write(f"Session Operation: #{self.performance_stats['total_operations']}\n")
                    f.write(f"Session Uptime   : {self._get_session_uptime()}\n")
                    f.write("⚠️ " + "=" * 60 + "\n\n")

                # ✅ FIXED: Console error with category
                print(f"[❌] ERROR [{error_category}] {filename}: {error_msg}")
                
                # ✅ FIXED: Log to JSON for analysis
                error_data = {
                    'timestamp': timestamp,
                    'filename': filename,
                    'error_message': error_msg,
                    'error_category': error_category,
                    'session_operation': self.performance_stats['total_operations']
                }
                self._log_to_json('error', error_data)
                
                # ✅ FIXED: Rotate log if needed
                self._rotate_log_if_needed(log_file)
                
            except Exception as e:
                print(f"[!] Failed to log error: {e}")

    def log_disconnection(self):
        """✅ FIXED: Enhanced disconnection logging with session summary"""
        with self.lock:
            try:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                log_file = os.path.join(self.folder_log_client, f"connection_{datetime.now().strftime('%Y%m%d')}.log")
                
                # ✅ FIXED: Calculate session statistics
                session_duration = self._get_session_uptime()
                avg_upload_time = self.performance_stats['total_upload_time'] / max(self.performance_stats['total_operations'], 1)
                avg_download_time = self.performance_stats['total_download_time'] / max(self.performance_stats['total_operations'], 1)
                total_data_mb = (self.performance_stats['total_bytes_uploaded'] + self.performance_stats['total_bytes_downloaded']) / (1024 * 1024)
                
                with open(log_file, 'a', encoding='utf-8') as f:
                    f.write("🔌 " + "=" * 60 + "\n")
                    f.write(f"[{timestamp}] SESSION DISCONNECTED\n")
                    f.write("🔌 " + "=" * 60 + "\n")
                    f.write(f"Session Duration     : {session_duration}\n")
                    f.write(f"Total Operations     : {self.performance_stats['total_operations']}\n")
                    f.write(f"Total Data Processed : {total_data_mb:.2f} MB\n")
                    f.write(f"Average Upload Time  : {avg_upload_time:.4f}s\n")
                    f.write(f"Average Download Time: {avg_download_time:.4f}s\n")
                    
                    # ✅ FIXED: Session performance summary
                    if self.performance_stats['total_operations'] > 0:
                        f.write(f"\n📊 SESSION PERFORMANCE:\n")
                        operations_per_minute = self.performance_stats['total_operations'] / max((datetime.now() - self.performance_stats['session_start']).total_seconds() / 60, 1)
                        f.write(f"   Operations/Minute : {operations_per_minute:.1f}\n")
                        
                        if operations_per_minute > 10:
                            f.write(f"   Session Rating    : 🚀 HIGHLY PRODUCTIVE\n")
                        elif operations_per_minute > 5:
                            f.write(f"   Session Rating    : ✅ PRODUCTIVE\n")
                        elif operations_per_minute > 1:
                            f.write(f"   Session Rating    : ⚠️  MODERATE\n")
                        else:
                            f.write(f"   Session Rating    : 🐌 LOW ACTIVITY\n")
                    
                    f.write("🔌 " + "=" * 60 + "\n\n")

                print(f"[🔌] Session ended: {self.performance_stats['total_operations']} operations in {session_duration}")
                
                # ✅ FIXED: Log to JSON for analysis
                disconnect_data = {
                    'timestamp': timestamp,
                    'session_duration': session_duration,
                    'total_operations': self.performance_stats['total_operations'],
                    'total_data_mb': total_data_mb,
                    'avg_upload_time': avg_upload_time,
                    'avg_download_time': avg_download_time
                }
                self._log_to_json('disconnection', disconnect_data)
                
            except Exception as e:
                print(f"[!] Failed to log disconnection: {e}")

    # ✅ FIXED: Utility methods for enhanced logging
    
    def _get_session_uptime(self):
        """Get formatted session uptime"""
        uptime = datetime.now() - self.performance_stats['session_start']
        return str(uptime).split('.')[0]  # Remove microseconds
    
    def _categorize_error(self, error_msg):
        """Categorize error messages for better analysis"""
        error_lower = error_msg.lower()
        
        if 'timeout' in error_lower:
            return '⏰ TIMEOUT'
        elif 'connection' in error_lower and 'refused' in error_lower:
            return '🚫 CONNECTION_REFUSED'
        elif 'network' in error_lower or 'socket' in error_lower:
            return '🌐 NETWORK_ERROR'
        elif 'decrypt' in error_lower or 'crypto' in error_lower:
            return '🔐 CRYPTO_ERROR'
        elif 'file' in error_lower or 'permission' in error_lower:
            return '📁 FILE_ERROR'
        elif 'memory' in error_lower or 'size' in error_lower:
            return '💾 MEMORY_ERROR'
        else:
            return '❓ UNKNOWN'
    
    def _log_to_json(self, log_type, data):
        """Log structured data to JSON for analysis"""
        try:
            json_file = os.path.join(self.folder_log_client, f"{log_type}_{datetime.now().strftime('%Y%m%d')}.json")
            
            # ✅ FIXED: Load existing data or create new
            json_data = []
            if os.path.exists(json_file):
                try:
                    with open(json_file, 'r', encoding='utf-8') as f:
                        json_data = json.load(f)
                except:
                    json_data = []  # Start fresh if corrupted
            
            # Add new entry
            json_data.append(data)
            
            # ✅ FIXED: Keep only recent entries (last 1000)
            if len(json_data) > 1000:
                json_data = json_data[-1000:]
            
            # Save back to file
            with open(json_file, 'w', encoding='utf-8') as f:
                json.dump(json_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            print(f"[!] Failed to log to JSON: {e}")
    
    def _rotate_log_if_needed(self, log_file):
        """Rotate log file if it exceeds maximum size"""
        try:
            if os.path.exists(log_file):
                file_size_mb = os.path.getsize(log_file) / (1024 * 1024)
                
                if file_size_mb > self.max_log_size_mb:
                    # ✅ FIXED: Rotate log files
                    base_name = log_file.replace('.log', '')
                    
                    # Remove oldest log file if we have too many
                    for i in range(self.max_log_files - 1, 0, -1):
                        old_file = f"{base_name}_{i}.log"
                        new_file = f"{base_name}_{i + 1}.log"
                        
                        if os.path.exists(old_file):
                            if i == self.max_log_files - 1:
                                os.remove(old_file)  # Remove oldest
                            else:
                                os.rename(old_file, new_file)  # Rotate
                    
                    # Move current log to _1
                    os.rename(log_file, f"{base_name}_1.log")
                    print(f"[🔄] Log rotated: {os.path.basename(log_file)} (was {file_size_mb:.1f}MB)")
                    
        except Exception as e:
            print(f"[!] Failed to rotate log: {e}")
    
    def get_performance_stats(self):
        """✅ FIXED: Get current performance statistics"""
        return {
            **self.performance_stats,
            'session_uptime': self._get_session_uptime(),
            'avg_upload_time': self.performance_stats['total_upload_time'] / max(self.performance_stats['total_operations'], 1),
            'avg_download_time': self.performance_stats['total_download_time'] / max(self.performance_stats['total_operations'], 1),
            'total_data_mb': (self.performance_stats['total_bytes_uploaded'] + self.performance_stats['total_bytes_downloaded']) / (1024 * 1024),
            'operations_per_minute': self.performance_stats['total_operations'] / max((datetime.now() - self.performance_stats['session_start']).total_seconds() / 60, 1)
        }
    
    def export_session_report(self):
        """✅ FIXED: Export comprehensive session report"""
        try:
            stats = self.get_performance_stats()
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            report_file = os.path.join(self.folder_log_client, f"session_report_{timestamp}.json")
            
            report = {
                'report_generated': datetime.now().isoformat(),
                'session_start': self.performance_stats['session_start'].isoformat(),
                'session_end': datetime.now().isoformat(),
                'performance_stats': stats,
                'log_files': self._get_log_files_info()
            }
            
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            print(f"[📄] Session report exported: {report_file}")
            return True, report_file
            
        except Exception as e:
            print(f"[!] Failed to export session report: {e}")
            return False, str(e)
    
    def _get_log_files_info(self):
        """Get information about all log files"""
        try:
            log_files = []
            for filename in os.listdir(self.folder_log_client):
                if filename.endswith('.log') or filename.endswith('.json'):
                    filepath = os.path.join(self.folder_log_client, filename)
                    stat = os.stat(filepath)
                    log_files.append({
                        'filename': filename,
                        'size_mb': stat.st_size / (1024 * 1024),
                        'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                        'modified': datetime.fromtimestamp(stat.st_mtime).isoformat()
                    })
            return sorted(log_files, key=lambda x: x['modified'], reverse=True)
        except Exception as e:
            print(f"[!] Failed to get log files info: {e}")
            return []
    
    def cleanup_old_logs(self, days_to_keep=7):
        """✅ FIXED: Clean up old log files"""
        try:
            cutoff_date = datetime.now() - timedelta(days=days_to_keep)
            removed_count = 0
            
            for filename in os.listdir(self.folder_log_client):
                if filename.endswith('.log') or filename.endswith('.json'):
                    filepath = os.path.join(self.folder_log_client, filename)
                    file_date = datetime.fromtimestamp(os.path.getmtime(filepath))
                    
                    if file_date < cutoff_date:
                        os.remove(filepath)
                        removed_count += 1
            
            if removed_count > 0:
                print(f"[🧹] Cleaned up {removed_count} old log files (older than {days_to_keep} days)")
            
            return True, f"Removed {removed_count} old log files"
            
        except Exception as e:
            print(f"[!] Failed to cleanup old logs: {e}")
            return False, str(e)