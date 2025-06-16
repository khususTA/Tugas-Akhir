import os
import json
import time
import base64
from datetime import datetime

class HistoryManager:
    def __init__(self, history_file):
        self.history_file = history_file

    def save_new_detection(self, filename, result_path, timing_data, image_bytes):
        """Simpan detection baru dan return data untuk UI"""
        
        # Generate unique ID
        detection_id = f"det_{int(time.time() * 1000)}"
        
        # Convert image to base64 untuk UI
        result_base64 = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode()
        
        # Buat data detection
        detection_data = {
            'id': detection_id,
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'result_path': result_path,
            'result_base64': result_base64,  # ✅ KONSISTEN: Gunakan result_base64
            'timing': timing_data,
            'status': 'completed'
        }
        
        # Load existing detections
        detections = self.load_detections()
        
        # Add new detection to the beginning
        detections.insert(0, detection_data)
        
        # Keep only last 100 detections
        detections = detections[:100]
        
        # Save back to file
        self.save_detections(detections)
        
        print(f"[📝] Detection saved: {detection_id} - {filename}")
        
        return detection_data

    def load_detections(self):
        """Load all detections from file"""
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Ensure it's a list
                    if isinstance(data, list):
                        return data
                    else:
                        print("[!] Invalid detection file format, creating new")
                        return []
            else:
                return []
        except Exception as e:
            print(f"[!] Error loading detections: {e}")
            return []

    def save_detections(self, detections):
        """Save detections to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(detections, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"[!] Error saving detections: {e}")
            return False

    def load_history_to_ui(self, webview_window):
        """✅ PERBAIKAN: Method untuk load history ke UI dengan error handling yang lebih baik"""
        try:
            detections = self.load_detections()
            
            if detections:
                ui_history = []
                for detection in detections:
                    # ✅ PERBAIKAN: Format data yang konsisten dengan frontend
                    ui_item = {
                        'id': detection.get('id', f"det_{int(time.time())}"),
                        'filename': detection.get('filename', 'unknown.jpg'),
                        'timestamp': detection.get('timestamp', datetime.now().isoformat()),
                        'resultImage': detection.get('result_base64', ''),  # ✅ NAMA FIELD KONSISTEN
                        'results': {
                            'totalDetections': 1,
                            'avgConfidence': 85,
                            'detections': [{'name': 'Hama Terdeteksi', 'confidence': 85}],
                            'recommendations': ['Pantau area terinfeksi', 'Aplikasikan treatment sesuai anjuran']
                        },
                        'processingTime': detection.get('timing', {}).get('total_waktu_komunikasi', 0),
                        'timing': detection.get('timing', {})
                    }
                    ui_history.append(ui_item)
                
                # ✅ PERBAIKAN: Gunakan global function yang ada di frontend
                history_json = json.dumps(ui_history, ensure_ascii=False)
                js_code = f"if(window.loadHistoryFromBackend) {{ window.loadHistoryFromBackend({history_json}); }} else {{ console.error('loadHistoryFromBackend function not found'); }}"
                webview_window.evaluate_js(js_code)
                    
                print(f"[📊] Loaded {len(ui_history)} detection records to UI")
            else:
                print("[📊] No detection history found")
                # ✅ PERBAIKAN: Panggil dengan array kosong
                webview_window.evaluate_js("if(window.loadHistoryFromBackend) { window.loadHistoryFromBackend([]); }")
                
        except Exception as e:
            print(f"[!] Error loading history to UI: {e}")
            # ✅ PERBAIKAN: Tetap panggil dengan array kosong jika error
            try:
                webview_window.evaluate_js("if(window.loadHistoryFromBackend) { window.loadHistoryFromBackend([]); }")
            except:
                pass

    def add_detection_to_ui(self, webview_window, detection_data):
        """✅ BARU: Method khusus untuk menambah detection ke UI"""
        try:
            # Format data untuk frontend
            ui_detection = {
                'id': detection_data.get('id'),
                'filename': detection_data.get('filename'),
                'timestamp': detection_data.get('timestamp'),
                'resultImage': detection_data.get('result_base64', ''),  # ✅ KONSISTEN
                'results': {
                    'totalDetections': 1,
                    'avgConfidence': 85,
                    'detections': [{'name': 'Hama Terdeteksi', 'confidence': 85}],
                    'recommendations': ['Pantau area terinfeksi', 'Aplikasikan treatment sesuai anjuran']
                },
                'processingTime': detection_data.get('timing', {}).get('total_waktu_komunikasi', 0),
                'timing': detection_data.get('timing', {})
            }
            
            # Kirim ke frontend
            detection_json = json.dumps(ui_detection, ensure_ascii=False)
            js_code = f"if(window.addDetectionFromBackend) {{ window.addDetectionFromBackend({detection_json}); }}"
            webview_window.evaluate_js(js_code)
            
            print(f"[📝] Detection {detection_data.get('id')} added to UI")
            
        except Exception as e:
            print(f"[!] Error adding detection to UI: {e}")

    def get_detection_stats(self):
        """Get statistics untuk UI"""
        try:
            detections = self.load_detections()
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Filter detections for today
            today_detections = [
                d for d in detections 
                if d.get('timestamp', '').startswith(today)
            ]
            
            stats = {
                'total_detections': len(detections),
                'today_detections': len(today_detections),
                'total_size_mb': 0,
                'avg_processing_time': 0,
                'success_rate': 100
            }
            
            if today_detections:
                # Calculate average processing time
                total_time = sum(
                    d.get('timing', {}).get('total_waktu_komunikasi', 0) 
                    for d in today_detections
                )
                stats['avg_processing_time'] = round(total_time / len(today_detections), 2)
                
                # Calculate total size
                total_size_kb = sum(
                    d.get('timing', {}).get('ukuran_hasil_kb', 0)
                    for d in today_detections
                )
                stats['total_size_mb'] = round(total_size_kb / 1024, 2)
            
            return stats
            
        except Exception as e:
            print(f"[!] Error getting stats: {e}")
            return {
                'total_detections': 0,
                'today_detections': 0,
                'total_size_mb': 0,
                'avg_processing_time': 0,
                'success_rate': 0
            }

    def clear_detection_history(self, webview_window):
        """Clear all detection history"""
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
            
            # ✅ PERBAIKAN: Clear UI history menggunakan global function
            webview_window.evaluate_js("if(window.clearHistoryFromBackend) { window.clearHistoryFromBackend(); }")
            
            return True, "History berhasil dihapus"
        except Exception as e:
            return False, f"Gagal hapus history: {e}"

    def export_detection_report(self, folder_history):
        """Export detection report as JSON"""
        try:
            detections = self.load_detections()
            stats = self.get_detection_stats()
            
            report = {
                'export_date': datetime.now().isoformat(),
                'total_detections': len(detections),
                'statistics': stats,
                'detections': detections
            }
            
            export_path = os.path.join(folder_history, f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True, f"Report exported to: {export_path}"
            
        except Exception as e:
            return False, f"Gagal export report: {e}"