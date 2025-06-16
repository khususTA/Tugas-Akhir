import os
import hashlib
from datetime import datetime

class ServerConfig:
    """
    Konfigurasi server PestDetect - Semua konstanta dan pengaturan terpusat
    """
    
    # ===== NETWORK CONFIGURATION =====
    SERVER_IP = '0.0.0.0'
    SERVER_PORT = 12345
    BUFFER_SIZE = 4096
    CLIENT_TIMEOUT = 60  # seconds
    MAX_CONCURRENT_CLIENTS = 10
    
    # ===== AUTHENTICATION =====
    PASSWORD = "jagapadi2024"
    PASSWORD_HASH = hashlib.sha256(PASSWORD.encode()).hexdigest()
    
    # ===== AES ENCRYPTION =====
    AES_KEY = b'tEaXKE1f8Xe8k3SlVRMGxQAoGIcDAq0C'  # 32-byte key untuk AES-256
    
    # ===== FOLDERS (AUTO CREATE IN server_data/) =====
    BASE_DATA_FOLDER = "server_data"
    FOLDER_ORIGINAL = os.path.join(BASE_DATA_FOLDER, "original_images")
    FOLDER_HASIL = os.path.join(BASE_DATA_FOLDER, "hasil_identifikasi")
    FOLDER_CLIPPER = os.path.join(BASE_DATA_FOLDER, "clipper_file")
    FOLDER_LOG = os.path.join(BASE_DATA_FOLDER, "logs")
    
    # ===== MODEL CONFIGURATION =====
    MODEL_PATH = os.path.join("model", "best.pt")
    MODEL_CONFIDENCE_THRESHOLD = 0.5
    MODEL_IOU_THRESHOLD = 0.45
    
    # ===== FILE LIMITS =====
    MAX_FILE_SIZE_MB = 50  # Maximum upload file size
    MAX_FILES_PER_SESSION = 100
    ALLOWED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
    
    # ===== PERFORMANCE =====
    ENABLE_TIMING_LOGS = True
    ENABLE_CLIENT_TIMING = True
    LOG_CLEANUP_DAYS = 30
    
    # ===== SERVER INFO =====
    SERVER_NAME = "PestDetect Server"
    SERVER_VERSION = "v2.1"
    SERVER_DESCRIPTION = "Enhanced with Client Decryption Timing"
    
    @classmethod
    def get_all_folders(cls):
        """
        Return list semua folder yang diperlukan server
        
        Returns:
            list: Daftar folder paths
        """
        return [
            cls.FOLDER_ORIGINAL,
            cls.FOLDER_HASIL,
            cls.FOLDER_CLIPPER,
            cls.FOLDER_LOG
        ]
    
    @classmethod
    def create_required_folders(cls):
        """
        Buat semua folder yang diperlukan server
        
        Returns:
            tuple: (success, created_folders, message)
        """
        try:
            created_folders = []
            for folder in cls.get_all_folders():
                if not os.path.exists(folder):
                    os.makedirs(folder, exist_ok=True)
                    created_folders.append(folder)
            
            message = f"Created {len(created_folders)} folders" if created_folders else "All folders already exist"
            return True, created_folders, message
            
        except Exception as e:
            return False, [], f"Failed to create folders: {e}"
    
    @classmethod
    def validate_model_file(cls):
        """
        Validasi apakah file model YOLO ada
        
        Returns:
            tuple: (exists, message)
        """
        if os.path.exists(cls.MODEL_PATH):
            file_size = os.path.getsize(cls.MODEL_PATH) / (1024 * 1024)  # MB
            return True, f"Model found: {cls.MODEL_PATH} ({file_size:.1f} MB)"
        else:
            return False, f"Model not found: {cls.MODEL_PATH}"
    
    @classmethod
    def get_server_info(cls):
        """
        Dapatkan informasi server untuk startup banner
        
        Returns:
            dict: Server information
        """
        return {
            'name': cls.SERVER_NAME,
            'version': cls.SERVER_VERSION,
            'description': cls.SERVER_DESCRIPTION,
            'ip': cls.SERVER_IP,
            'port': cls.SERVER_PORT,
            'model_path': cls.MODEL_PATH,
            'folders': cls.get_all_folders(),
            'max_clients': cls.MAX_CONCURRENT_CLIENTS,
            'startup_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
    
    @classmethod
    def print_startup_banner(cls):
        """
        Print banner informasi saat server startup
        """
        info = cls.get_server_info()
        
        print("=" * 70)
        print(f"🌾 {info['name']} {info['version']} - {info['description']}")
        print("=" * 70)
        print(f"[+] Server aktif di {info['ip']}:{info['port']}")
        print(f"[+] Model YOLO: {info['model_path']}")
        print(f"[+] Max concurrent clients: {info['max_clients']}")
        print(f"[+] Folder log: {cls.FOLDER_LOG}")
        print(f"[+] Password: {cls.PASSWORD}")
        print(f"[+] Startup time: {info['startup_time']}")
        
        # Validasi model
        model_exists, model_msg = cls.validate_model_file()
        status_icon = "✓" if model_exists else "✗"
        print(f"[{status_icon}] {model_msg}")
        
        # Validasi folders
        success, created, folder_msg = cls.create_required_folders()
        if success:
            if created:
                print(f"[+] Created folders: {', '.join(created)}")
            else:
                print(f"[+] All required folders exist")
        else:
            print(f"[!] Folder setup failed: {folder_msg}")
        
        print("=" * 70)
    
    @classmethod
    def validate_file_upload(cls, filename, file_size_bytes):
        """
        Validasi file upload dari client
        
        Args:
            filename (str): Nama file
            file_size_bytes (int): Ukuran file dalam bytes
            
        Returns:
            tuple: (valid, message)
        """
        # Cek ekstensi file
        _, ext = os.path.splitext(filename.lower())
        if ext not in cls.ALLOWED_IMAGE_EXTENSIONS:
            return False, f"File extension not allowed: {ext}"
        
        # Cek ukuran file
        file_size_mb = file_size_bytes / (1024 * 1024)
        if file_size_mb > cls.MAX_FILE_SIZE_MB:
            return False, f"File too large: {file_size_mb:.1f}MB (max: {cls.MAX_FILE_SIZE_MB}MB)"
        
        return True, "File validation passed"
    
    @classmethod
    def get_network_config(cls):
        """
        Dapatkan konfigurasi network untuk NetworkManager
        
        Returns:
            dict: Network configuration
        """
        return {
            'server_ip': cls.SERVER_IP,
            'server_port': cls.SERVER_PORT,
            'buffer_size': cls.BUFFER_SIZE,
            'client_timeout': cls.CLIENT_TIMEOUT,
            'password_hash': cls.PASSWORD_HASH,
            'max_concurrent_clients': cls.MAX_CONCURRENT_CLIENTS
        }
    
    @classmethod
    def get_crypto_config(cls):
        """
        Dapatkan konfigurasi crypto untuk CryptoManager
        
        Returns:
            dict: Crypto configuration
        """
        return {
            'aes_key': cls.AES_KEY,
            'clipper_folder': cls.FOLDER_CLIPPER
        }
    
    @classmethod
    def get_detection_config(cls):
        """
        Dapatkan konfigurasi detection untuk DetectionProcessor
        
        Returns:
            dict: Detection configuration
        """
        return {
            'model_path': cls.MODEL_PATH,
            'output_folder': cls.FOLDER_HASIL,
            'confidence_threshold': cls.MODEL_CONFIDENCE_THRESHOLD,
            'iou_threshold': cls.MODEL_IOU_THRESHOLD
        }
    
    @classmethod
    def get_logger_config(cls):
        """
        Dapatkan konfigurasi logging untuk ServerLogger
        
        Returns:
            dict: Logger configuration
        """
        return {
            'log_folder': cls.FOLDER_LOG,
            'enable_timing_logs': cls.ENABLE_TIMING_LOGS,
            'enable_client_timing': cls.ENABLE_CLIENT_TIMING,
            'cleanup_days': cls.LOG_CLEANUP_DAYS
        }

# ===== UTILITY FUNCTIONS =====

def load_config_from_file(config_file="server_config.ini"):
    """
    Load konfigurasi dari file INI (opsional untuk future enhancement)
    
    Args:
        config_file (str): Path ke file konfigurasi
        
    Returns:
        bool: True jika berhasil load dari file
    """
    # Placeholder untuk future enhancement
    # Bisa menggunakan configparser untuk load dari file INI
    return False

def validate_server_environment():
    """
    Validasi environment server sebelum startup
    
    Returns:
        tuple: (valid, issues)
    """
    issues = []
    
    # Cek model file
    model_exists, model_msg = ServerConfig.validate_model_file()
    if not model_exists:
        issues.append(f"Missing model: {model_msg}")
    
    # Cek folder permissions
    try:
        ServerConfig.create_required_folders()
    except Exception as e:
        issues.append(f"Folder permission issue: {e}")
    
    # Cek port availability (basic check)
    if ServerConfig.SERVER_PORT < 1024:
        issues.append(f"Port {ServerConfig.SERVER_PORT} might require admin privileges")
    
    return len(issues) == 0, issues

def print_config_summary():
    """
    Print ringkasan konfigurasi untuk debugging
    """
    print("\n📋 SERVER CONFIGURATION SUMMARY:")
    print("-" * 50)
    print(f"Network    : {ServerConfig.SERVER_IP}:{ServerConfig.SERVER_PORT}")
    print(f"Model      : {ServerConfig.MODEL_PATH}")
    print(f"Password   : {ServerConfig.PASSWORD}")
    print(f"Max Upload : {ServerConfig.MAX_FILE_SIZE_MB} MB")
    print(f"Log Folder : {ServerConfig.FOLDER_LOG}")
    print(f"Timing     : {'Enabled' if ServerConfig.ENABLE_TIMING_LOGS else 'Disabled'}")
    print("-" * 50)