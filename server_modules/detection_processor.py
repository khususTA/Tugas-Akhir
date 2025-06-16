import os
import time
from ultralytics import YOLO
from PIL import Image

class DetectionProcessor:
    def __init__(self, model_path="model/best.pt", output_folder=None, confidence_threshold=0.5, iou_threshold=0.45):
        """
        Initialize detection processor dengan parameter lengkap dari config
        
        Args:
            model_path (str): Path ke model YOLO
            output_folder (str): Folder untuk hasil deteksi
            confidence_threshold (float): Threshold confidence untuk deteksi
            iou_threshold (float): Threshold IOU untuk NMS
        """
        self.model_path = model_path
        self.output_folder = output_folder or os.path.join("server_data", "hasil_identifikasi")
        self.confidence_threshold = confidence_threshold
        self.iou_threshold = iou_threshold
        self.model = None
        
        # Buat folder output jika belum ada
        os.makedirs(self.output_folder, exist_ok=True)

    def load_model(self):
        """
        Load model YOLO dengan error handling yang lebih baik
        
        Returns:
            tuple: (success, message)
        """
        try:
            # Cek apakah file model ada
            if not os.path.exists(self.model_path):
                return False, f"Model file tidak ditemukan: {self.model_path}"
            
            # Cek ukuran file model
            model_size = os.path.getsize(self.model_path)
            if model_size == 0:
                return False, f"Model file kosong: {self.model_path}"
            
            # Load model dengan konfigurasi threshold
            self.model = YOLO(self.model_path)
            
            # Set model parameters jika model berhasil di-load
            if hasattr(self.model, 'overrides'):
                self.model.overrides['conf'] = self.confidence_threshold
                self.model.overrides['iou'] = self.iou_threshold
            
            # Test model dengan validasi basic
            model_info = self.get_model_info()
            if not model_info.get('class_names'):
                return False, "Model loaded but no class names found"
            
            return True, f"Model loaded successfully: {self.model_path} ({model_size/(1024*1024):.1f} MB, {len(model_info['class_names'])} classes)"
            
        except Exception as e:
            return False, f"Gagal load model: {e}"

    def validate_image(self, image_path):
        """
        Validasi file gambar yang lebih comprehensive
        
        Args:
            image_path (str): Path ke file gambar
            
        Returns:
            tuple: (valid, message)
        """
        try:
            # Cek file ada
            if not os.path.exists(image_path):
                return False, "File gambar tidak ditemukan"
            
            # Cek ukuran file
            file_size = os.path.getsize(image_path)
            if file_size == 0:
                return False, "File gambar kosong"
            if file_size > 50 * 1024 * 1024:  # Max 50MB
                return False, f"File terlalu besar: {file_size/(1024*1024):.1f}MB (max: 50MB)"
            
            # Cek ekstensi file
            valid_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp']
            _, ext = os.path.splitext(image_path.lower())
            if ext not in valid_extensions:
                return False, f"Format file tidak didukung: {ext}"
            
            # Coba buka file dengan PIL untuk validasi format
            with Image.open(image_path) as img:
                # Validasi dimensi gambar
                width, height = img.size
                if width < 32 or height < 32:
                    return False, f"Gambar terlalu kecil: {width}x{height} (min: 32x32)"
                if width > 10000 or height > 10000:
                    return False, f"Gambar terlalu besar: {width}x{height} (max: 10000x10000)"
                
                # Verify image integrity
                img.verify()
            
            return True, f"File gambar valid: {width}x{height}, {file_size/1024:.1f}KB"
            
        except Exception as e:
            return False, f"File gambar rusak atau tidak valid: {e}"

    def process_detection(self, image_path, output_filename):
        """
        Jalankan deteksi YOLO dengan error handling dan optimasi yang lebih baik
        
        Args:
            image_path (str): Path ke gambar input
            output_filename (str): Nama file output
            
        Returns:
            tuple: (success, output_path, labels, confidence, detection_time, message)
        """
        try:
            # Cek apakah model sudah di-load
            if self.model is None:
                return False, None, None, 0, 0, "Model belum di-load"
            
            # Validasi gambar input
            valid, validation_msg = self.validate_image(image_path)
            if not valid:
                return False, None, None, 0, 0, validation_msg
            
            # Mulai timing deteksi
            start_time = time.time()
            
            # Jalankan deteksi YOLO dengan parameter yang telah dikonfigurasi
            results = self.model(
                image_path,
                conf=self.confidence_threshold,
                iou=self.iou_threshold,
                verbose=False  # Kurangi output log YOLO
            )
            result = results[0]
            
            # Extract labels dan confidence
            labels, confidences = [], []
            if result.boxes is not None and len(result.boxes) > 0:
                for box in result.boxes:
                    cls = int(box.cls[0])
                    conf = float(box.conf[0])
                    
                    # Double check confidence threshold (backup)
                    if conf >= self.confidence_threshold:
                        label = self.model.names[cls]
                        labels.append(label)
                        confidences.append(conf)
            
            # Hitung rata-rata confidence
            rata_conf = round(sum(confidences) / len(confidences), 3) if confidences else 0.0
            
            # Hitung waktu deteksi
            detection_time = time.time() - start_time
            
            # Generate nama output yang unik
            timestamp = int(time.time())
            nama_output = f"hasil_{timestamp}_{output_filename}"
            output_path = os.path.join(self.output_folder, nama_output)
            
            # Pastikan output path unik
            counter = 1
            while os.path.exists(output_path):
                nama_output = f"hasil_{timestamp}_{counter}_{output_filename}"
                output_path = os.path.join(self.output_folder, nama_output)
                counter += 1
            
            # Simpan hasil gambar dengan kualitas yang baik
            result_image_np = result.plot(
                conf=True,      # Show confidence
                labels=True,    # Show labels  
                boxes=True,     # Show bounding boxes
                line_width=2    # Line thickness
            )
            result_image = Image.fromarray(result_image_np)
            
            # Simpan dengan kualitas tinggi
            if output_filename.lower().endswith(('.jpg', '.jpeg')):
                result_image.save(output_path, 'JPEG', quality=90)
            else:
                result_image.save(output_path)
            
            # Validasi file hasil tersimpan
            if not os.path.exists(output_path):
                return False, None, None, 0, 0, "Gagal menyimpan hasil deteksi"
            
            detection_msg = f"Detected {len(labels)} objects" if labels else "No objects detected"
            return True, output_path, labels, rata_conf, detection_time, detection_msg
            
        except Exception as e:
            return False, None, None, 0, 0, f"Error saat deteksi: {e}"

    def get_model_info(self):
        """
        Dapatkan informasi lengkap tentang model
        
        Returns:
            dict: Informasi model
        """
        if self.model is None:
            return {
                "status": "Model not loaded",
                "model_path": self.model_path,
                "model_exists": os.path.exists(self.model_path)
            }
        
        try:
            info = {
                "status": "Model loaded",
                "model_path": self.model_path,
                "confidence_threshold": self.confidence_threshold,
                "iou_threshold": self.iou_threshold,
                "output_folder": self.output_folder
            }
            
            # Informasi class names
            if hasattr(self.model, 'names'):
                info["class_names"] = list(self.model.names.values())
                info["num_classes"] = len(self.model.names)
            else:
                info["class_names"] = []
                info["num_classes"] = 0
            
            # Informasi file model
            if os.path.exists(self.model_path):
                model_size = os.path.getsize(self.model_path)
                info["model_size_mb"] = round(model_size / (1024 * 1024), 2)
            
            return info
            
        except Exception as e:
            return {
                "status": f"Error getting model info: {e}",
                "model_path": self.model_path
            }

    def test_detection_performance(self, test_image_path=None):
        """
        Test performa deteksi untuk monitoring
        
        Args:
            test_image_path (str): Path ke gambar test (optional)
            
        Returns:
            dict: Hasil test performa
        """
        try:
            if self.model is None:
                return {"error": "Model not loaded"}
            
            # Jika tidak ada test image, buat gambar dummy
            if test_image_path is None or not os.path.exists(test_image_path):
                # Buat test image sederhana
                import numpy as np
                test_array = np.random.randint(0, 255, (640, 640, 3), dtype=np.uint8)
                test_image = Image.fromarray(test_array)
                test_image_path = os.path.join(self.output_folder, "test_image.jpg")
                test_image.save(test_image_path)
            
            # Jalankan test detection
            start_time = time.time()
            success, output_path, labels, confidence, detection_time, message = self.process_detection(
                test_image_path, "test_detection.jpg"
            )
            total_time = time.time() - start_time
            
            # Cleanup test files
            if test_image_path.endswith("test_image.jpg"):
                try:
                    os.remove(test_image_path)
                except:
                    pass
            
            if output_path and os.path.exists(output_path):
                try:
                    os.remove(output_path)
                except:
                    pass
            
            return {
                "test_successful": success,
                "detection_time_seconds": detection_time,
                "total_time_seconds": total_time,
                "labels_found": len(labels) if labels else 0,
                "average_confidence": confidence,
                "message": message,
                "performance_rating": "Good" if detection_time < 1.0 else "Slow" if detection_time > 3.0 else "Normal"
            }
            
        except Exception as e:
            return {
                "test_successful": False,
                "error": str(e)
            }

    def cleanup_old_results(self, days_to_keep=7):
        """
        Bersihkan hasil deteksi lama
        
        Args:
            days_to_keep (int): Jumlah hari file hasil yang disimpan
            
        Returns:
            tuple: (success, cleaned_count, message)
        """
        try:
            if not os.path.exists(self.output_folder):
                return True, 0, "Output folder does not exist"
            
            import time
            current_time = time.time()
            cutoff_time = current_time - (days_to_keep * 24 * 60 * 60)
            
            cleaned_count = 0
            for filename in os.listdir(self.output_folder):
                if filename.startswith('hasil_'):
                    file_path = os.path.join(self.output_folder, filename)
                    if os.path.getmtime(file_path) < cutoff_time:
                        os.remove(file_path)
                        cleaned_count += 1
            
            return True, cleaned_count, f"Cleaned {cleaned_count} old result files"
            
        except Exception as e:
            return False, 0, f"Cleanup error: {e}"

    def cleanup(self):
        """
        Cleanup resources dan reset model
        """
        try:
            if self.model is not None:
                # Clear model dari memory
                del self.model
                self.model = None
            
            # Force garbage collection
            import gc
            gc.collect()
            
            return True, "Cleanup successful"
            
        except Exception as e:
            return False, f"Cleanup error: {e}"

# Fungsi wrapper untuk backward compatibility dengan deteksi.py asli
def jalankan_deteksi(path_input, nama_file, model_path="model/best.pt", output_folder=None):
    """
    Wrapper function untuk kompatibilitas dengan deteksi.py asli
    
    Args:
        path_input (str): Path ke gambar input
        nama_file (str): Nama file output
        model_path (str): Path ke model (default: model/best.pt)
        output_folder (str): Folder output (default: server_data/hasil_identifikasi)
        
    Returns:
        tuple: (output_path, labels, rata_confidence) - sama seperti deteksi.py asli
    """
    # Default output folder
    if output_folder is None:
        output_folder = os.path.join("server_data", "hasil_identifikasi")
    
    processor = DetectionProcessor(model_path, output_folder)
    
    # Load model
    success, message = processor.load_model()
    if not success:
        raise Exception(f"Gagal load model: {message}")
    
    # Proses deteksi
    success, output_path, labels, rata_conf, detection_time, message = processor.process_detection(path_input, nama_file)
    
    if not success:
        raise Exception(f"Gagal deteksi: {message}")
    
    # Return format sama seperti deteksi.py asli
    return output_path, labels, rata_conf