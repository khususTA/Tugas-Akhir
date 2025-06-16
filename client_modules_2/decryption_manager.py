from Crypto.Cipher import AES
import time

class CryptoManager:
    def __init__(self, aes_key):
        if not isinstance(aes_key, bytes):
            raise TypeError("AES key must be bytes")
        if len(aes_key) not in [16, 24, 32]:
            raise ValueError(f"Invalid AES key length: {len(aes_key)}. Must be 16, 24, or 32 bytes")
        
        self.aes_key = aes_key
        self.key_length = len(aes_key)
        self.operations_count = 0
        self.total_decrypt_time = 0
        self.total_bytes_decrypted = 0

    def decrypt_AES_CTR(self, ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
        """
        AES CTR decryption
        Args:
            ciphertext: encrypted data (without nonce)
            nonce: 8-byte nonce from server
            key: AES key (16/24/32 bytes)
        Returns:
            decrypted data (bytes)
        """
        # Basic validation
        if not all(isinstance(x, bytes) for x in [ciphertext, nonce, key]):
            raise TypeError("All parameters must be bytes")
        if len(nonce) != 8:
            raise ValueError(f"Invalid nonce length: {len(nonce)}. Must be 8 bytes")
        if len(key) not in [16, 24, 32]:
            raise ValueError(f"Invalid key length: {len(key)}. Must be 16, 24, or 32 bytes")
        if len(ciphertext) == 0:
            raise ValueError("Ciphertext cannot be empty")
        
        try:
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            plaintext = cipher.decrypt(ciphertext)
            return plaintext
            
        except Exception as e:
            raise RuntimeError(f"AES decryption failed: {e}")

    def decrypt_data(self, encrypted_data):
        """Decrypt data with timing and validation"""
        if not isinstance(encrypted_data, bytes):
            raise TypeError("Encrypted data must be bytes")
        if len(encrypted_data) < 8:
            raise ValueError(f"Encrypted data too short: {len(encrypted_data)} bytes")
        
        decrypt_start = time.time()
        
        try:
            # Extract nonce and ciphertext
            nonce = encrypted_data[:8]
            ciphertext = encrypted_data[8:]
            
            if len(ciphertext) == 0:
                raise ValueError("No ciphertext found after nonce")
            
            # Perform decryption
            hasil_bytes = self.decrypt_AES_CTR(ciphertext, nonce, self.aes_key)
            
            # Calculate metrics
            decrypt_time = time.time() - decrypt_start
            decrypt_speed_kbps = (len(ciphertext) / 1024) / decrypt_time if decrypt_time > 0 else 0
            
            # Update statistics
            self.operations_count += 1
            self.total_decrypt_time += decrypt_time
            self.total_bytes_decrypted += len(hasil_bytes)
            
            # Basic integrity check
            self._basic_integrity_check(hasil_bytes)
            
            print(f"Decryption successful: {len(hasil_bytes)} bytes in {decrypt_time:.4f}s ({decrypt_speed_kbps:.1f} KB/s)")
            
            return hasil_bytes
            
        except Exception as e:
            print(f"Data decryption failed: {e}")
            raise

    def _basic_integrity_check(self, decrypted_data):
        """Basic integrity verification"""
        try:
            if len(decrypted_data) < 10:
                print(f"Warning: Very small decrypted data ({len(decrypted_data)} bytes)")
                return
            
            # Check for common image signatures
            data_start = decrypted_data[:10]
            if data_start.startswith(b'\xff\xd8'):
                print("Detected: JPEG image data")
            elif data_start.startswith(b'\x89\x50\x4e\x47'):
                print("Detected: PNG image data")
            else:
                print(f"Unknown file format (header: {data_start[:4].hex()})")
            
            # Check null byte percentage (corruption indicator)
            null_count = decrypted_data.count(b'\x00')
            null_percentage = (null_count / len(decrypted_data)) * 100
            
            if null_percentage > 50:
                print(f"Warning: High null bytes ({null_percentage:.1f}%) - possible corruption")
            
        except Exception as e:
            print(f"Integrity check failed: {e}")

    def get_crypto_stats(self):
        """Get basic cryptographic operation statistics"""
        if self.operations_count == 0:
            return {
                'operations_count': 0,
                'total_decrypt_time': 0,
                'total_bytes_decrypted': 0,
                'avg_decrypt_time': 0,
                'avg_speed_kbps': 0,
                'key_length_bits': self.key_length * 8
            }
        
        avg_decrypt_time = self.total_decrypt_time / self.operations_count
        avg_bytes_per_op = self.total_bytes_decrypted / self.operations_count
        avg_speed_kbps = (avg_bytes_per_op / 1024) / avg_decrypt_time if avg_decrypt_time > 0 else 0
        
        return {
            'operations_count': self.operations_count,
            'total_decrypt_time': round(self.total_decrypt_time, 4),
            'total_bytes_decrypted': self.total_bytes_decrypted,
            'total_mb_decrypted': round(self.total_bytes_decrypted / (1024 * 1024), 2),
            'avg_decrypt_time': round(avg_decrypt_time, 4),
            'avg_bytes_per_operation': round(avg_bytes_per_op, 2),
            'avg_speed_kbps': round(avg_speed_kbps, 1),
            'key_length_bits': self.key_length * 8
        }

    def validate_key_strength(self):
        """Basic key strength validation"""
        try:
            # Check key entropy (simplified)
            unique_bytes = len(set(self.aes_key))
            diversity_ratio = unique_bytes / len(self.aes_key)
            
            # Check for patterns
            null_count = self.aes_key.count(0)
            null_ratio = null_count / len(self.aes_key)
            
            # Simple assessment
            issues = []
            if diversity_ratio < 0.8:
                issues.append(f"Low byte diversity: {unique_bytes}/{len(self.aes_key)}")
            if null_ratio > 0.1:
                issues.append(f"Too many null bytes: {null_count}")
            
            strength = "STRONG" if not issues else "WEAK"
            
            result = {
                'key_length_bits': self.key_length * 8,
                'byte_diversity': round(diversity_ratio, 3),
                'strength': strength,
                'issues': issues
            }
            
            print(f"Key validation: {self.key_length * 8}-bit, {strength}")
            if issues:
                print(f"Issues: {', '.join(issues)}")
            
            return result
            
        except Exception as e:
            print(f"Key validation failed: {e}")
            return None

    def reset_stats(self):
        """Reset operation statistics"""
        self.operations_count = 0
        self.total_decrypt_time = 0
        self.total_bytes_decrypted = 0
        print("Crypto statistics reset")

    def __str__(self):
        """String representation"""
        stats = self.get_crypto_stats()
        return (f"CryptoManager(AES-{self.key_length * 8}, "
                f"ops={stats['operations_count']}, "
                f"avg_speed={stats['avg_speed_kbps']}KB/s)")

    def __repr__(self):
        return f"CryptoManager(key_length={self.key_length})"