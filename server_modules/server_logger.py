import os
import csv
import time
from datetime import datetime

class ServerLogger:
    def __init__(self, log_folder="logs", enable_timing_logs=True, enable_client_timing=True, cleanup_days=30):
        """
        Initialize server logger dengan parameter lengkap dari config
        
        Args:
            log_folder (str): Folder untuk menyimpan log files
            enable_timing_logs (bool): Enable logging timing details
            enable_client_timing (bool): Enable logging client timing data
            cleanup_days (int): Jumlah hari untuk auto cleanup log files
        """
        self.log_folder = log_folder
        self.enable_timing_logs = enable_timing_logs
        self.enable_client_timing = enable_client_timing
        self.cleanup_days = cleanup_days
        
        # Buat folder log jika belum ada
        os.makedirs(self.log_folder, exist_ok=True)

    def log_client_session(self, log_data, waktu_disconnect, durasi):
        """
        Log session client ke file TXT yang readable
        
        Args:
            log_data (dict): Data session client dengan file logs
            waktu_disconnect (datetime): Waktu disconnect
            durasi (float): Durasi koneksi dalam detik
        """
        try:
            # Format nama file log
            connect_time_str = log_data['connect_time'].strftime("%Y%m%d_%H%M%S")
            log_filename = f"session_{connect_time_str}.txt"
            log_path = os.path.join(self.log_folder, log_filename)
            
            # Statistik session
            jumlah_file = len(log_data['file_logs'])
            jumlah_deteksi = sum(1 for file_log in log_data['file_logs'] if file_log['labels'])
            
            # Confidence stats
            confidence_values = [f['confidence'] for f in log_data['file_logs'] if f['confidence'] > 0]
            rata_conf = sum(confidence_values) / len(confidence_values) if confidence_values else 0.0
            
            # Client timing stats (jika enabled)
            client_decrypt_times = []
            if self.enable_client_timing:
                client_decrypt_times = [f.get('waktu_dekripsi_client', 0) for f in log_data['file_logs'] if f.get('waktu_dekripsi_client', 0) > 0]
            rata_decrypt_client = sum(client_decrypt_times) / len(client_decrypt_times) if client_decrypt_times else 0.0
            
            with open(log_path, 'w', encoding='utf-8') as f:
                # Header session dengan labels
                f.write("=" * 80 + "\n")
                f.write("INFORMASI SESSION CLIENT\n")
                f.write("=" * 80 + "\n")
                f.write(f"IP Client             : {log_data['ip']}\n")
                f.write(f"Connected             : {log_data['connect_time'].strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Disconnected          : {waktu_disconnect.strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"Total Waktu Session   : {durasi:.2f} detik\n")
                f.write("-" * 40 + "\n")
                f.write("STATISTIK DETEKSI:\n")
                f.write(f"Jumlah File           : {jumlah_file}\n")
                f.write(f"Jumlah Deteksi        : {jumlah_deteksi}\n")
                f.write(f"Rata-rata Confidence  : {rata_conf:.3f}\n")
                f.write(f"Detection Rate        : {(jumlah_deteksi/jumlah_file*100):.1f}%\n" if jumlah_file > 0 else "Detection Rate        : 0.0%\n")
                
                # Client timing hanya jika enabled
                if self.enable_client_timing and client_decrypt_times:
                    f.write("-" * 40 + "\n")
                    f.write("PERFORMA CLIENT:\n")
                    f.write(f"Rata-rata Dekripsi Client : {rata_decrypt_client:.4f} detik\n")
                    f.write(f"Total Dekripsi Client     : {sum(client_decrypt_times):.4f} detik\n")
                
                f.write("=" * 80 + "\n")
                
                # Detail files dengan tabel yang jelas (hanya jika timing enabled)
                if jumlah_file > 0:
                    f.write("\nDETAIL TRANSFER & PROCESSING FILE:\n")
                    f.write("=" * 160 + "\n")
                    f.write("KETERANGAN KOLOM:\n")
                    f.write("• No      : Nomor urut file\n")
                    f.write("• Filename: Nama file gambar yang diproses\n")
                    f.write("• Detection Result: Hasil deteksi hama/penyakit\n") 
                    f.write("• Size Original: Ukuran file asli (KB)\n")
                    f.write("• Size Encrypted: Ukuran setelah enkripsi (KB)\n")
                    f.write("• YOLO Time: Waktu proses deteksi YOLO (detik)\n")
                    f.write("• AES Time: Waktu enkripsi AES (detik)\n")
                    if self.enable_client_timing:
                        f.write("• Client Decrypt: Waktu dekripsi di client (detik)\n")
                    f.write("• Confidence: Tingkat kepercayaan deteksi (0-1)\n")
                    f.write("-" * 160 + "\n")
                    
                    # Header tabel yang rapi
                    if self.enable_client_timing:
                        header = f"{'No':>3} | {'Filename':<25} | {'Detection Result':<20} | {'Size Ori':>10} | {'Size Enc':>10} | {'YOLO Time':>10} | {'AES Time':>9} | {'Client Dec':>11} | {'Confidence':>10}"
                    else:
                        header = f"{'No':>3} | {'Filename':<25} | {'Detection Result':<20} | {'Size Ori':>10} | {'Size Enc':>10} | {'YOLO Time':>10} | {'AES Time':>9} | {'Confidence':>10}"
                    f.write(header + "\n")
                    f.write("-" * 160 + "\n")
                    
                    # Data setiap file dalam format tabel
                    for i, file_log in enumerate(log_data['file_logs'], 1):
                        # Format filename
                        filename = file_log['filename']
                        if len(filename) > 24:
                            filename = filename[:21] + "..."
                        
                        # Format detection result
                        if file_log['labels']:
                            detection_result = ", ".join(file_log['labels'])
                            if len(detection_result) > 19:
                                detection_result = detection_result[:16] + "..."
                        else:
                            detection_result = "NO_DETECTION"
                        
                        # Format data dengan alignment yang rapi
                        if self.enable_client_timing:
                            row = f"{i:>3} | {filename:<25} | {detection_result:<20} | " \
                                  f"{file_log['size_ori']:>8.2f} KB | {file_log['size_enc']:>8.2f} KB | " \
                                  f"{file_log['waktu_deteksi']:>8.3f}s | {file_log['waktu_enkripsi']:>7.3f}s | " \
                                  f"{file_log.get('waktu_dekripsi_client', 0):>9.3f}s | " \
                                  f"{file_log['confidence']:>8.3f}"
                        else:
                            row = f"{i:>3} | {filename:<25} | {detection_result:<20} | " \
                                  f"{file_log['size_ori']:>8.2f} KB | {file_log['size_enc']:>8.2f} KB | " \
                                  f"{file_log['waktu_deteksi']:>8.3f}s | {file_log['waktu_enkripsi']:>7.3f}s | " \
                                  f"{file_log['confidence']:>8.3f}"
                        
                        f.write(row + "\n")
                    
                    f.write("-" * 160 + "\n")
                    
                    # Summary statistics dalam format tabel (hanya jika timing enabled)
                    if self.enable_timing_logs:
                        f.write("\nRINGKASAN STATISTIK PROCESSING:\n")
                        f.write("=" * 80 + "\n")
                        
                        # Hitung total dan rata-rata
                        total_size_ori = sum(f['size_ori'] for f in log_data['file_logs'])
                        total_size_enc = sum(f['size_enc'] for f in log_data['file_logs'])
                        total_yolo_time = sum(f['waktu_deteksi'] for f in log_data['file_logs'])
                        total_aes_time = sum(f['waktu_enkripsi'] for f in log_data['file_logs'])
                        total_client_decrypt = sum(f.get('waktu_dekripsi_client', 0) for f in log_data['file_logs']) if self.enable_client_timing else 0
                        
                        # Tabel statistik
                        f.write(f"{'Metric':<30} | {'Total':<15} | {'Average':<15} | {'Unit':<10}\n")
                        f.write("-" * 80 + "\n")
                        f.write(f"{'File Size Original':<30} | {total_size_ori:>13.2f} | {total_size_ori/jumlah_file:>13.2f} | {'KB':<10}\n")
                        f.write(f"{'File Size Encrypted':<30} | {total_size_enc:>13.2f} | {total_size_enc/jumlah_file:>13.2f} | {'KB':<10}\n")
                        f.write(f"{'YOLO Detection Time':<30} | {total_yolo_time:>13.3f} | {total_yolo_time/jumlah_file:>13.3f} | {'seconds':<10}\n")
                        f.write(f"{'AES Encryption Time':<30} | {total_aes_time:>13.3f} | {total_aes_time/jumlah_file:>13.3f} | {'seconds':<10}\n")
                        if self.enable_client_timing and total_client_decrypt > 0:
                            f.write(f"{'Client Decryption Time':<30} | {total_client_decrypt:>13.3f} | {total_client_decrypt/jumlah_file:>13.3f} | {'seconds':<10}\n")
                        f.write("-" * 80 + "\n")
                        
                        # Efficiency metrics
                        avg_confidence = sum(f['confidence'] for f in log_data['file_logs'] if f['confidence'] > 0) / max(1, len([f for f in log_data['file_logs'] if f['confidence'] > 0]))
                        encryption_overhead = ((total_size_enc - total_size_ori) / total_size_ori * 100) if total_size_ori > 0 else 0
                        
                        f.write(f"\nMETRIK EFISIENSI:\n")
                        f.write("-" * 50 + "\n")
                        f.write(f"Detection Success Rate    : {jumlah_deteksi}/{jumlah_file} ({jumlah_deteksi/jumlah_file*100:.1f}%)\n")
                        f.write(f"Average Confidence Score  : {avg_confidence:.3f}\n")
                        f.write(f"Encryption Overhead       : {encryption_overhead:.2f}%\n")
                        total_processing_time = total_yolo_time + total_aes_time
                        if self.enable_client_timing:
                            total_processing_time += total_client_decrypt
                        f.write(f"Total Processing Time     : {total_processing_time:.3f} seconds\n")
                
                f.write("\n")
            
            return True, f"Session log saved: {log_filename}"
            
        except Exception as e:
            return False, f"Failed to write session log: {e}"

    def log_to_csv(self, log_data):
        """
        Log data ke CSV untuk analisis
        
        Args:
            log_data (dict): Data session client
        """
        try:
            csv_path = os.path.join(self.log_folder, "detection_database.csv")
            file_exists = os.path.exists(csv_path)
            
            with open(csv_path, 'a', newline='', encoding='utf-8') as csvfile:
                fieldnames = [
                    'timestamp', 'client_ip', 'filename', 'labels', 
                    'size_ori_kb', 'size_enc_kb', 'waktu_deteksi', 
                    'waktu_enkripsi', 'confidence'
                ]
                
                # Tambahkan field client timing jika enabled
                if self.enable_client_timing:
                    fieldnames.append('waktu_dekripsi_client')
                
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                if not file_exists:
                    writer.writeheader()
                
                for file_log in log_data['file_logs']:
                    row_data = {
                        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                        'client_ip': log_data['ip'],
                        'filename': file_log['filename'],
                        'labels': "|".join(file_log['labels']) if file_log['labels'] else "",
                        'size_ori_kb': round(file_log['size_ori'], 2),
                        'size_enc_kb': round(file_log['size_enc'], 2),
                        'waktu_deteksi': round(file_log['waktu_deteksi'], 4),
                        'waktu_enkripsi': round(file_log['waktu_enkripsi'], 4),
                        'confidence': round(file_log['confidence'], 3)
                    }
                    
                    # Tambahkan client timing jika enabled
                    if self.enable_client_timing:
                        row_data['waktu_dekripsi_client'] = round(file_log.get('waktu_dekripsi_client', 0), 4)
                    
                    writer.writerow(row_data)
            
            return True, "CSV log updated"
            
        except Exception as e:
            return False, f"Failed to write CSV log: {e}"

    def log_timing_summary(self, filename, timing_data):
        """
        Log ringkasan timing untuk setiap file (hanya jika timing enabled)
        
        Args:
            filename (str): Nama file
            timing_data (dict): Data timing lengkap
        """
        if not self.enable_timing_logs:
            return True
            
        try:
            today = datetime.now().strftime('%Y%m%d')
            timing_log = os.path.join(self.log_folder, f"timing_{today}.log")
            
            with open(timing_log, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%H:%M:%S')}] TIMING ANALYSIS: {filename}\n")
                f.write(f"  - YOLO Detection: {timing_data.get('waktu_deteksi', 0):.3f}s\n")
                f.write(f"  - AES Encryption: {timing_data.get('waktu_enkripsi', 0):.3f}s\n")
                if self.enable_client_timing:
                    f.write(f"  - Client Decrypt: {timing_data.get('waktu_dekripsi_client', 0):.3f}s\n")
                total_time = timing_data.get('waktu_deteksi', 0) + timing_data.get('waktu_enkripsi', 0)
                if self.enable_client_timing:
                    total_time += timing_data.get('waktu_dekripsi_client', 0)
                f.write(f"  - Total Process:  {total_time:.3f}s\n")
                f.write("-" * 50 + "\n")
            
            return True
            
        except Exception as e:
            print(f"[!] Failed to write timing log: {e}")
            return False

    def log_error(self, client_ip, error_message, context=""):
        """
        Log error yang terjadi
        
        Args:
            client_ip (str): IP client
            error_message (str): Pesan error
            context (str): Konteks error
        """
        try:
            today = datetime.now().strftime('%Y%m%d')
            error_log = os.path.join(self.log_folder, f"errors_{today}.log")
            
            with open(error_log, 'a', encoding='utf-8') as f:
                f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] SYSTEM ERROR\n")
                f.write(f"  Client IP    : {client_ip}\n")
                f.write(f"  Error Context: {context}\n")
                f.write(f"  Error Message: {error_message}\n")
                f.write(f"  Severity     : {'HIGH' if 'failed' in error_message.lower() or 'error' in error_message.lower() else 'MEDIUM'}\n")
                f.write("-" * 60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"[!] Failed to write error log: {e}")
            return False

    def get_today_stats(self):
        """
        Ambil statistik hari ini dari CSV
        
        Returns:
            dict: Statistik hari ini
        """
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            csv_path = os.path.join(self.log_folder, "detection_database.csv")
            
            stats = {
                'total_files': 0,
                'total_detections': 0,
                'avg_confidence': 0.0,
                'avg_detection_time': 0.0,
                'unique_ips': set()
            }
            
            # Tambahkan client timing stats jika enabled
            if self.enable_client_timing:
                stats['avg_client_decrypt_time'] = 0.0
            
            if not os.path.exists(csv_path):
                if 'unique_ips' in stats:
                    stats['unique_ips'] = 0
                return stats
            
            confidence_values = []
            detection_times = []
            client_decrypt_times = []
            
            with open(csv_path, 'r', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row['timestamp'].startswith(today):
                        stats['total_files'] += 1
                        stats['unique_ips'].add(row['client_ip'])
                        
                        if row['labels']:
                            stats['total_detections'] += 1
                            if float(row['confidence']) > 0:
                                confidence_values.append(float(row['confidence']))
                        
                        detection_times.append(float(row['waktu_deteksi']))
                        
                        if self.enable_client_timing and 'waktu_dekripsi_client' in row and row['waktu_dekripsi_client'] and float(row['waktu_dekripsi_client']) > 0:
                            client_decrypt_times.append(float(row['waktu_dekripsi_client']))
            
            # Hitung rata-rata
            if confidence_values:
                stats['avg_confidence'] = sum(confidence_values) / len(confidence_values)
            if detection_times:
                stats['avg_detection_time'] = sum(detection_times) / len(detection_times)
            if self.enable_client_timing and client_decrypt_times:
                stats['avg_client_decrypt_time'] = sum(client_decrypt_times) / len(client_decrypt_times)
            
            stats['unique_ips'] = len(stats['unique_ips'])
            
            return stats
            
        except Exception as e:
            print(f"[!] Failed to get today stats: {e}")
            default_stats = {'total_files': 0, 'total_detections': 0, 'avg_confidence': 0.0, 
                           'avg_detection_time': 0.0, 'unique_ips': 0}
            if self.enable_client_timing:
                default_stats['avg_client_decrypt_time'] = 0.0
            return default_stats

    def cleanup_old_logs(self, days_to_keep=None):
        """
        Bersihkan log lama
        
        Args:
            days_to_keep (int): Jumlah hari log yang disimpan (gunakan instance variable jika None)
        """
        try:
            cleanup_days = days_to_keep or self.cleanup_days
            current_time = time.time()
            cutoff_time = current_time - (cleanup_days * 24 * 60 * 60)
            
            cleaned_files = 0
            for filename in os.listdir(self.log_folder):
                if filename.startswith(("session_", "timing_", "errors_")):
                    file_path = os.path.join(self.log_folder, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        cleaned_files += 1
            
            return True, f"Cleaned {cleaned_files} old log files"
            
        except Exception as e:
            return False, f"Failed to cleanup logs: {e}"

    def create_daily_summary(self):
        """
        Buat ringkasan harian
        
        Returns:
            tuple: (success, message)
        """
        try:
            stats = self.get_today_stats()
            today = datetime.now().strftime("%Y%m%d")
            summary_path = os.path.join(self.log_folder, f"daily_summary_{today}.txt")
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write("=" * 70 + "\n")
                f.write(f"LAPORAN HARIAN PESTDETECT SERVER - {today}\n")
                f.write("=" * 70 + "\n")
                f.write("RINGKASAN AKTIVITAS:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Total Files Processed    : {stats['total_files']}\n")
                f.write(f"Total Pest Detections    : {stats['total_detections']}\n")
                f.write(f"Unique Client IPs        : {stats['unique_ips']}\n")
                f.write("-" * 30 + "\n")
                f.write("PERFORMA SISTEM:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Avg Detection Confidence : {stats['avg_confidence']:.3f}\n")
                f.write(f"Avg YOLO Processing Time : {stats['avg_detection_time']:.3f} detik\n")
                if self.enable_client_timing and 'avg_client_decrypt_time' in stats:
                    f.write(f"Avg Client Decrypt Time  : {stats['avg_client_decrypt_time']:.3f} detik\n")
                if stats['total_files'] > 0:
                    detection_rate = (stats['total_detections'] / stats['total_files']) * 100
                    f.write(f"System Detection Rate    : {detection_rate:.1f}%\n")
                f.write("-" * 30 + "\n")
                f.write("INTERPRETASI:\n")
                if stats['total_files'] > 0:
                    detection_rate = (stats['total_detections'] / stats['total_files']) * 100
                    if detection_rate > 70:
                        f.write("- Tingkat deteksi tinggi: Area pemantauan perlu perhatian\n")
                    elif detection_rate > 30:
                        f.write("- Tingkat deteksi sedang: Monitoring rutin diperlukan\n")
                    else:
                        f.write("- Tingkat deteksi rendah: Kondisi tanaman relatif baik\n")
                    
                    if stats['avg_detection_time'] < 1.0:
                        f.write("- Performa server optimal: Waktu deteksi cepat\n")
                    elif stats['avg_detection_time'] < 2.0:
                        f.write("- Performa server normal: Waktu deteksi acceptable\n")
                    else:
                        f.write("- Performa server lambat: Perlu optimasi atau upgrade\n")
                f.write("=" * 70 + "\n")
            
            return True, f"Daily summary created: daily_summary_{today}.txt"
            
        except Exception as e:
            return False, f"Failed to create daily summary: {e}"

    def get_logger_info(self):
        """
        Dapatkan informasi konfigurasi logger
        
        Returns:
            dict: Informasi logger configuration
        """
        return {
            'log_folder': self.log_folder,
            'log_folder_exists': os.path.exists(self.log_folder),
            'enable_timing_logs': self.enable_timing_logs,
            'enable_client_timing': self.enable_client_timing,
            'cleanup_days': self.cleanup_days,
            'csv_database_exists': os.path.exists(os.path.join(self.log_folder, "detection_database.csv"))
        }