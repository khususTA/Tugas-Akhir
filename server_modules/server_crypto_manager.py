import base64
import os
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes

class ServerCryptoManager:
    def __init__(self, aes_key, clipper_folder=None):
        """
        Initialize crypto manager dengan AES key dan folder clipper
        
        Args:
            aes_key (bytes): 32-byte AES key untuk enkripsi
            clipper_folder (str): Folder untuk menyimpan file clipper
        """
        self.aes_key = aes_key
        self.clipper_folder = clipper_folder or os.path.join("server_data", "clipper_file")
        
        # Buat folder clipper jika belum ada
        os.makedirs(self.clipper_folder, exist_ok=True)

    def encrypt_AES_CTR(self, data: bytes):
        """
        Enkripsi data menggunakan AES CTR mode
        
        Args:
            data (bytes): Data yang akan dienkripsi
            
        Returns:
            tuple: (ciphertext, nonce)
        """
        try:
            nonce = get_random_bytes(8)  # 64-bit nonce untuk CTR
            cipher = AES.new(self.aes_key, AES.MODE_CTR, nonce=nonce)
            ciphertext = cipher.encrypt(data)
            return ciphertext, nonce
        except Exception as e:
            raise Exception(f"AES encryption failed: {e}")

    def prepare_encrypted_data(self, image_result_path):
        """
        Baca file hasil deteksi, enkripsi, dan siapkan untuk dikirim
        
        Args:
            image_result_path (str): Path ke file hasil deteksi
            
        Returns:
            tuple: (success, encrypted_data, base64_clipper, error_msg)
        """
        try:
            # Validasi file exists
            if not os.path.exists(image_result_path):
                return False, None, None, f"File not found: {image_result_path}"
            
            # Validasi file size
            file_size = os.path.getsize(image_result_path)
            if file_size == 0:
                return False, None, None, "Empty file detected"
            if file_size > 100 * 1024 * 1024:  # Max 100MB
                return False, None, None, f"File too large: {file_size / (1024*1024):.1f}MB"
            
            # Baca file hasil deteksi
            with open(image_result_path, "rb") as f:
                data_hasil = f.read()
            
            # Enkripsi data
            encrypted_data, nonce = self.encrypt_AES_CTR(data_hasil)
            
            # Gabungkan nonce + encrypted data
            full_data = nonce + encrypted_data
            
            # Buat base64 clipper untuk backup
            clipper = base64.b64encode(full_data).decode()
            
            return True, full_data, clipper, "Encryption successful"
            
        except FileNotFoundError:
            return False, None, None, f"File not found: {image_result_path}"
        except PermissionError:
            return False, None, None, f"Permission denied: {image_result_path}"
        except Exception as e:
            return False, None, None, f"Encryption error: {e}"

    def save_clipper_file(self, clipper_data, filename, clipper_folder=None):
        """
        Simpan file clipper (base64 encrypted data) untuk backup
        
        Args:
            clipper_data (str): Base64 encoded encrypted data
            filename (str): Nama file asli
            clipper_folder (str): Folder untuk menyimpan clipper (optional)
            
        Returns:
            tuple: (success, clipper_path, error_msg)
        """
        try:
            # Gunakan folder default jika tidak dispesifikasi
            target_folder = clipper_folder or self.clipper_folder
            
            # Buat folder jika belum ada
            os.makedirs(target_folder, exist_ok=True)
            
            # Generate nama file clipper yang unik
            clipper_filename = filename + ".clip"
            clipper_path = os.path.join(target_folder, clipper_filename)
            
            # Jika file sudah ada, tambahkan timestamp
            if os.path.exists(clipper_path):
                import time
                timestamp = int(time.time())
                name, ext = os.path.splitext(clipper_filename)
                clipper_filename = f"{name}_{timestamp}{ext}"
                clipper_path = os.path.join(target_folder, clipper_filename)
            
            # Simpan clipper data
            with open(clipper_path, "w", encoding='utf-8') as f:
                f.write(clipper_data)
            
            return True, clipper_path, "Clipper saved successfully"
            
        except Exception as e:
            return False, None, f"Clipper save error: {e}"

    def get_encryption_stats(self, original_size, encrypted_size):
        """
        Hitung statistik enkripsi dengan informasi yang lebih lengkap
        
        Args:
            original_size (int): Ukuran data asli dalam bytes
            encrypted_size (int): Ukuran data terenkripsi dalam bytes
            
        Returns:
            dict: Statistik enkripsi
        """
        stats = {
            'original_size_bytes': original_size,
            'encrypted_size_bytes': encrypted_size,
            'original_size_kb': original_size / 1024,
            'encrypted_size_kb': encrypted_size / 1024,
            'size_ratio': encrypted_size / original_size if original_size > 0 else 0,
            'overhead_bytes': encrypted_size - original_size,
            'compression_achieved': original_size > encrypted_size
        }
        
        if original_size > 0:
            stats['overhead_percentage'] = ((encrypted_size - original_size) / original_size * 100)
        else:
            stats['overhead_percentage'] = 0
            
        return stats

    def validate_aes_key(self):
        """
        Validasi AES key yang digunakan
        
        Returns:
            tuple: (valid, message)
        """
        try:
            if not isinstance(self.aes_key, bytes):
                return False, "AES key must be bytes"
            
            if len(self.aes_key) != 32:
                return False, f"AES key must be 32 bytes, got {len(self.aes_key)} bytes"
            
            # Test enkripsi sederhana
            test_data = b"test_encryption"
            encrypted, nonce = self.encrypt_AES_CTR(test_data)
            
            if len(encrypted) != len(test_data):
                return False, "Encryption test failed"
            
            return True, "AES key valid"
            
        except Exception as e:
            return False, f"AES key validation error: {e}"

    def get_crypto_info(self):
        """
        Dapatkan informasi konfigurasi crypto
        
        Returns:
            dict: Informasi crypto configuration
        """
        key_valid, key_msg = self.validate_aes_key()
        
        return {
            'aes_key_length': len(self.aes_key) if self.aes_key else 0,
            'aes_key_valid': key_valid,
            'aes_key_status': key_msg,
            'clipper_folder': self.clipper_folder,
            'clipper_folder_exists': os.path.exists(self.clipper_folder),
            'encryption_mode': 'AES-256-CTR',
            'nonce_size': 8
        }

    def decrypt_AES_CTR(self, encrypted_data_with_nonce: bytes):
        """
        Dekripsi data (untuk testing atau recovery)
        
        Args:
            encrypted_data_with_nonce (bytes): Data terenkripsi dengan nonce di depan
            
        Returns:
            tuple: (success, decrypted_data, error_msg)
        """
        try:
            if len(encrypted_data_with_nonce) < 8:
                return False, None, "Data too short to contain nonce"
            
            # Extract nonce dan encrypted data
            nonce = encrypted_data_with_nonce[:8]
            encrypted_data = encrypted_data_with_nonce[8:]
            
            # Dekripsi
            cipher = AES.new(self.aes_key, AES.MODE_CTR, nonce=nonce)
            decrypted_data = cipher.decrypt(encrypted_data)
            
            return True, decrypted_data, "Decryption successful"
            
        except Exception as e:
            return False, None, f"Decryption error: {e}"

    def cleanup_old_clippers(self, days_to_keep=7):
        """
        Bersihkan file clipper lama
        
        Args:
            days_to_keep (int): Jumlah hari file clipper yang disimpan
            
        Returns:
            tuple: (success, cleaned_count, message)
        """
        try:
            if not os.path.exists(self.clipper_folder):
                return True, 0, "Clipper folder does not exist"
            
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
            
            cleaned_count = 0
            for filename in os.listdir(self.clipper_folder):
                if filename.endswith('.clip'):
                    file_path = os.path.join(self.clipper_folder, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        cleaned_count += 1
            
            return True, cleaned_count, f"Cleaned {cleaned_count} old clipper files"
            
        except Exception as e:
            return False, 0, f"Cleanup error: {e}"

    def test_encryption_performance(self, test_data_size=1024*1024):
        """
        Test performa enkripsi untuk monitoring
        
        Args:
            test_data_size (int): Ukuran data test dalam bytes
            
        Returns:
            dict: Hasil test performa
        """
        try:
            import time
            
            # Generate test data
            test_data = os.urandom(test_data_size)
            
            # Test enkripsi
            start_time = time.time()
            encrypted_data, nonce = self.encrypt_AES_CTR(test_data)
            encrypt_time = time.time() - start_time
            
            # Test dekripsi
            start_time = time.time()
            success, decrypted_data, _ = self.decrypt_AES_CTR(nonce + encrypted_data)
            decrypt_time = time.time() - start_time
            
            # Validasi
            data_match = test_data == decrypted_data if success else False
            
            return {
                'test_data_size_mb': test_data_size / (1024 * 1024),
                'encrypt_time_seconds': encrypt_time,
                'decrypt_time_seconds': decrypt_time,
                'total_time_seconds': encrypt_time + decrypt_time,
                'encrypt_speed_mbps': (test_data_size / (1024 * 1024)) / encrypt_time if encrypt_time > 0 else 0,
                'decrypt_speed_mbps': (test_data_size / (1024 * 1024)) / decrypt_time if decrypt_time > 0 else 0,
                'data_integrity_ok': data_match,
                'test_successful': success and data_match
            }
            
        except Exception as e:
            return {
                'test_successful': False,
                'error': str(e)
            }