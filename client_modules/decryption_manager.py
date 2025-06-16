from Crypto.Cipher import AES
import hashlib
import os
import time

class CryptoManager:
    def __init__(self, aes_key):
        # ✅ FIXED: Enhanced key validation
        if not isinstance(aes_key, bytes):
            raise TypeError("AES key must be bytes")
        if len(aes_key) not in [16, 24, 32]:
            raise ValueError(f"Invalid AES key length: {len(aes_key)}. Must be 16, 24, or 32 bytes")
        
        self.aes_key = aes_key
        self.key_length = len(aes_key)
        self.operations_count = 0
        self.total_decrypt_time = 0
        self.total_bytes_decrypted = 0
        
        print(f"[🔐] CryptoManager initialized with {self.key_length * 8}-bit AES key")

    def decrypt_AES_CTR(self, ciphertext: bytes, nonce: bytes, key: bytes) -> bytes:
        """
        ✅ FIXED: Enhanced AES CTR decryption with validation
        Parameter:
            - ciphertext: data terenkripsi (tanpa nonce)
            - nonce: 8-byte nonce yang dikirim dari server
            - key: 32-byte key (harus sama dengan server)
        Return:
            - plain data (bytes)
        """
        # ✅ FIXED: Input validation
        if not isinstance(ciphertext, bytes):
            raise TypeError("Ciphertext must be bytes")
        if not isinstance(nonce, bytes):
            raise TypeError("Nonce must be bytes")
        if not isinstance(key, bytes):
            raise TypeError("Key must be bytes")
        
        if len(nonce) != 8:
            raise ValueError(f"Invalid nonce length: {len(nonce)}. Must be 8 bytes")
        if len(key) not in [16, 24, 32]:
            raise ValueError(f"Invalid key length: {len(key)}. Must be 16, 24, or 32 bytes")
        if len(ciphertext) == 0:
            raise ValueError("Ciphertext cannot be empty")
        
        try:
            # ✅ FIXED: Enhanced cipher creation with error handling
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            plaintext = cipher.decrypt(ciphertext)
            
            # ✅ FIXED: Basic integrity check (optional)
            if len(plaintext) != len(ciphertext):
                print(f"[⚠️] Warning: Decrypted size mismatch - input: {len(ciphertext)}, output: {len(plaintext)}")
            
            return plaintext
            
        except Exception as e:
            print(f"[❌] AES decryption failed: {e}")
            raise RuntimeError(f"AES decryption failed: {e}")

    def decrypt_data(self, encrypted_data):
        """✅ FIXED: Enhanced data decryption with comprehensive validation and metrics"""
        
        # ✅ FIXED: Input validation
        if not isinstance(encrypted_data, bytes):
            raise TypeError("Encrypted data must be bytes")
        if len(encrypted_data) < 8:
            raise ValueError(f"Encrypted data too short: {len(encrypted_data)} bytes. Minimum is 8 bytes (nonce)")
        
        decrypt_start = time.time()
        
        try:
            # ✅ FIXED: Enhanced data parsing with validation
            nonce = encrypted_data[:8]
            ciphertext = encrypted_data[8:]
            
            print(f"[🔐] Decrypting {len(ciphertext)} bytes with {len(nonce)}-byte nonce")
            
            if len(ciphertext) == 0:
                raise ValueError("No ciphertext found after nonce")
            
            # ✅ FIXED: Perform decryption with enhanced error handling
            try:
                hasil_bytes = self.decrypt_AES_CTR(ciphertext, nonce, self.aes_key)
            except Exception as e:
                print(f"[❌] Decryption operation failed: {e}")
                raise
            
            # ✅ FIXED: Calculate metrics
            decrypt_time = time.time() - decrypt_start
            decrypt_speed_kbps = (len(ciphertext) / 1024) / decrypt_time if decrypt_time > 0 else 0
            
            # ✅ FIXED: Update statistics
            self.operations_count += 1
            self.total_decrypt_time += decrypt_time
            self.total_bytes_decrypted += len(hasil_bytes)
            
            # ✅ FIXED: Enhanced logging with performance metrics
            print(f"[✅] Decryption successful: {len(hasil_bytes)} bytes in {decrypt_time:.4f}s ({decrypt_speed_kbps:.1f} KB/s)")
            
            # ✅ FIXED: Performance assessment
            if decrypt_speed_kbps > 10000:  # > 10 MB/s
                print(f"[🚀] Decryption performance: EXCELLENT")
            elif decrypt_speed_kbps > 5000:  # > 5 MB/s
                print(f"[✅] Decryption performance: GOOD")
            elif decrypt_speed_kbps > 1000:  # > 1 MB/s
                print(f"[⚠️] Decryption performance: AVERAGE")
            else:
                print(f"[🐌] Decryption performance: SLOW")
            
            # ✅ FIXED: Optional integrity verification
            self._verify_decryption_integrity(hasil_bytes)
            
            return hasil_bytes
            
        except Exception as e:
            error_msg = f"Data decryption failed: {e}"
            print(f"[❌] {error_msg}")
            # ✅ FIXED: Don't re-raise as different exception type to preserve original error
            raise

    def _verify_decryption_integrity(self, decrypted_data):
        """✅ FIXED: Basic integrity verification for decrypted data"""
        try:
            # ✅ FIXED: Check if data looks like valid image data (basic heuristics)
            if len(decrypted_data) < 10:
                print(f"[⚠️] Warning: Decrypted data very small ({len(decrypted_data)} bytes)")
                return
            
            # Check for common image file signatures
            jpeg_signatures = [b'\xff\xd8\xff', b'\xff\xd8']
            png_signature = b'\x89\x50\x4e\x47'
            
            data_start = decrypted_data[:10]
            
            is_jpeg = any(data_start.startswith(sig) for sig in jpeg_signatures)
            is_png = data_start.startswith(png_signature)
            
            if is_jpeg:
                print(f"[✅] Integrity check: Detected JPEG image data")
            elif is_png:
                print(f"[✅] Integrity check: Detected PNG image data")
            else:
                print(f"[⚠️] Integrity check: Unknown file format (first 10 bytes: {data_start.hex()})")
            
            # ✅ FIXED: Check for null bytes (potential corruption indicator)
            null_count = decrypted_data.count(b'\x00')
            null_percentage = (null_count / len(decrypted_data)) * 100
            
            if null_percentage > 50:
                print(f"[⚠️] Warning: High null byte percentage ({null_percentage:.1f}%) - possible corruption")
            elif null_percentage > 20:
                print(f"[ℹ️] Info: Moderate null byte percentage ({null_percentage:.1f}%)")
            
        except Exception as e:
            print(f"[!] Integrity verification failed: {e}")

    def get_crypto_stats(self):
        """✅ FIXED: Get comprehensive cryptographic operation statistics"""
        avg_decrypt_time = self.total_decrypt_time / max(self.operations_count, 1)
        avg_bytes_per_op = self.total_bytes_decrypted / max(self.operations_count, 1)
        total_mb_decrypted = self.total_bytes_decrypted / (1024 * 1024)
        avg_speed_kbps = (avg_bytes_per_op / 1024) / avg_decrypt_time if avg_decrypt_time > 0 else 0
        
        return {
            'operations_count': self.operations_count,
            'total_decrypt_time': round(self.total_decrypt_time, 4),
            'total_bytes_decrypted': self.total_bytes_decrypted,
            'total_mb_decrypted': round(total_mb_decrypted, 2),
            'avg_decrypt_time': round(avg_decrypt_time, 4),
            'avg_bytes_per_operation': round(avg_bytes_per_op, 2),
            'avg_speed_kbps': round(avg_speed_kbps, 1),
            'key_length_bits': self.key_length * 8
        }

    def benchmark_decryption(self, test_data_size_kb=100):
        """✅ FIXED: Benchmark decryption performance"""
        try:
            print(f"[🏃] Running decryption benchmark with {test_data_size_kb}KB test data...")
            
            # ✅ FIXED: Generate test data
            test_data = os.urandom(test_data_size_kb * 1024)
            test_nonce = os.urandom(8)
            
            # Encrypt test data first
            cipher = AES.new(self.aes_key, AES.MODE_CTR, nonce=test_nonce)
            encrypted_test = cipher.encrypt(test_data)
            
            # Prepare encrypted data with nonce
            full_encrypted = test_nonce + encrypted_test
            
            # ✅ FIXED: Benchmark multiple runs
            runs = 5
            times = []
            
            for i in range(runs):
                start_time = time.time()
                decrypted = self.decrypt_data(full_encrypted)
                end_time = time.time()
                
                # Verify correctness
                if decrypted != test_data:
                    raise RuntimeError("Benchmark failed: decrypted data doesn't match original")
                
                times.append(end_time - start_time)
                print(f"[🏃] Benchmark run {i+1}/{runs}: {times[-1]:.4f}s")
            
            # ✅ FIXED: Calculate statistics
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)
            speed_kbps = (test_data_size_kb) / avg_time
            
            benchmark_results = {
                'test_size_kb': test_data_size_kb,
                'runs': runs,
                'avg_time': round(avg_time, 4),
                'min_time': round(min_time, 4),
                'max_time': round(max_time, 4),
                'avg_speed_kbps': round(speed_kbps, 1),
                'performance_rating': self._rate_performance(speed_kbps)
            }
            
            print(f"[📊] Benchmark results:")
            print(f"    Average time: {avg_time:.4f}s")
            print(f"    Speed: {speed_kbps:.1f} KB/s")
            print(f"    Rating: {benchmark_results['performance_rating']}")
            
            return benchmark_results
            
        except Exception as e:
            print(f"[❌] Benchmark failed: {e}")
            return None

    def _rate_performance(self, speed_kbps):
        """Rate decryption performance"""
        if speed_kbps > 10000:
            return "🚀 EXCELLENT"
        elif speed_kbps > 5000:
            return "✅ GOOD"
        elif speed_kbps > 1000:
            return "⚠️ AVERAGE"
        else:
            return "🐌 SLOW"

    def validate_key_security(self):
        """✅ FIXED: Validate AES key security properties"""
        try:
            # ✅ FIXED: Check key entropy
            key_entropy = self._calculate_entropy(self.aes_key)
            
            # ✅ FIXED: Check for weak patterns
            weak_patterns = self._check_weak_patterns(self.aes_key)
            
            # ✅ FIXED: Security assessment
            security_score = 0
            issues = []
            
            # Entropy check (ideal is close to 8 bits per byte)
            if key_entropy > 7.5:
                security_score += 40
            elif key_entropy > 6.0:
                security_score += 20
                issues.append(f"Moderate entropy: {key_entropy:.2f}")
            else:
                issues.append(f"Low entropy: {key_entropy:.2f}")
            
            # Pattern checks
            if not weak_patterns:
                security_score += 30
            else:
                issues.extend(weak_patterns)
            
            # Key length bonus
            if self.key_length == 32:  # AES-256
                security_score += 30
            elif self.key_length == 24:  # AES-192
                security_score += 20
            else:  # AES-128
                security_score += 10
            
            # ✅ FIXED: Generate security report
            if security_score >= 90:
                rating = "🛡️ EXCELLENT"
            elif security_score >= 70:
                rating = "✅ GOOD"
            elif security_score >= 50:
                rating = "⚠️ ACCEPTABLE"
            else:
                rating = "❌ WEAK"
            
            security_report = {
                'key_length_bits': self.key_length * 8,
                'entropy': round(key_entropy, 3),
                'security_score': security_score,
                'rating': rating,
                'issues': issues
            }
            
            print(f"[🔐] Key security validation:")
            print(f"    Length: {self.key_length * 8} bits")
            print(f"    Entropy: {key_entropy:.3f}")
            print(f"    Score: {security_score}/100")
            print(f"    Rating: {rating}")
            
            if issues:
                print(f"    Issues: {', '.join(issues)}")
            
            return security_report
            
        except Exception as e:
            print(f"[!] Key validation failed: {e}")
            return None

    def _calculate_entropy(self, data):
        """Calculate Shannon entropy of data"""
        if len(data) == 0:
            return 0
        
        # Count byte frequencies
        byte_counts = [0] * 256
        for byte in data:
            byte_counts[byte] += 1
        
        # Calculate entropy
        entropy = 0
        for count in byte_counts:
            if count > 0:
                probability = count / len(data)
                entropy -= probability * (probability.bit_length() - 1)
        
        return entropy

    def _check_weak_patterns(self, key):
        """Check for weak patterns in the key"""
        issues = []
        
        # Check for repeated bytes
        unique_bytes = len(set(key))
        if unique_bytes < len(key) * 0.8:
            issues.append(f"Low byte diversity: {unique_bytes}/{len(key)}")
        
        # Check for sequential patterns
        sequential_count = 0
        for i in range(len(key) - 1):
            if abs(key[i] - key[i + 1]) <= 1:
                sequential_count += 1
        
        if sequential_count > len(key) * 0.3:
            issues.append("Sequential byte patterns detected")
        
        # Check for null bytes
        null_count = key.count(0)
        if null_count > len(key) * 0.1:
            issues.append(f"Too many null bytes: {null_count}")
        
        return issues

    def reset_stats(self):
        """✅ FIXED: Reset operation statistics"""
        self.operations_count = 0
        self.total_decrypt_time = 0
        self.total_bytes_decrypted = 0
        print("[📊] Crypto statistics reset")

    def __str__(self):
        """String representation of CryptoManager"""
        stats = self.get_crypto_stats()
        return (f"CryptoManager(AES-{self.key_length * 8}, "
                f"ops={stats['operations_count']}, "
                f"avg_speed={stats['avg_speed_kbps']}KB/s)")

    def __repr__(self):
        return f"CryptoManager(key_length={self.key_length})"