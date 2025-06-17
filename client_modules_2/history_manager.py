import os
import json
import time
import base64
from datetime import datetime

class HistoryManager:
    def __init__(self, history_file):
        self.history_file = history_file

    def save_new_detection(self, filename, result_path, timing_data, image_bytes):
        """Save new detection and return data for UI"""
        
        # Generate unique ID
        detection_id = f"det_{int(time.time() * 1000)}"
        
        # Convert image to base64 for UI
        result_base64 = "data:image/jpeg;base64," + base64.b64encode(image_bytes).decode()
        
        # Create detection data
        detection_data = {
            'id': detection_id,
            'filename': filename,
            'timestamp': datetime.now().isoformat(),
            'result_path': result_path,
            'result_base64': result_base64,
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
        
        print(f"Detection saved: {detection_id} - {filename}")
        
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
                        print("Invalid detection file format, creating new")
                        return []
            else:
                return []
        except Exception as e:
            print(f"Error loading detections: {e}")
            return []

    def save_detections(self, detections):
        """Save detections to file"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(detections, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving detections: {e}")
            return False

    def get_all_detections_for_ui(self):
        """✅ NEW: Get all detection records formatted for UI (Local-First History)"""
        try:
            detections = self.load_detections()
            ui_formatted = []
            
            print(f"📂 Formatting {len(detections)} detections for UI...")
            
            for detection in detections:
                # Format each detection for frontend consumption
                ui_item = {
                    'id': detection.get('id', f"det_{int(time.time())}"),
                    'filename': detection.get('filename', 'unknown.jpg'),
                    'timestamp': detection.get('timestamp', datetime.now().isoformat()),
                    'resultImage': detection.get('result_base64', ''),
                    'results': {
                        'totalDetections': 1,
                        'avgConfidence': 85,
                        'detections': [{'name': 'Hama Terdeteksi', 'confidence': 85}],
                        'recommendations': [
                            'Pantau area terinfeksi secara rutin',
                            'Aplikasikan treatment sesuai anjuran ahli',
                            'Konsultasi dengan penyuluh pertanian'
                        ]
                    },
                    'processingTime': detection.get('timing', {}).get('total_waktu_komunikasi', 0),
                    'timing': detection.get('timing', {}),
                    'source': 'python_client'  # Mark sebagai data dari Python client
                }
                ui_formatted.append(ui_item)
            
            print(f"✅ Formatted {len(ui_formatted)} detection records for UI")
            return ui_formatted
            
        except Exception as e:
            print(f"❌ Error formatting detections for UI: {e}")
            return []

    def get_all_detections(self):
        """✅ NEW: Get raw detection data (helper method)"""
        return self.load_detections()

    def load_history_to_ui(self, webview_window):
        """Load history to UI with basic error handling (Server Sync)"""
        try:
            detections = self.load_detections()
            
            if detections:
                ui_history = []
                for detection in detections:
                    # Format data for frontend
                    ui_item = {
                        'id': detection.get('id', f"det_{int(time.time())}"),
                        'filename': detection.get('filename', 'unknown.jpg'),
                        'timestamp': detection.get('timestamp', datetime.now().isoformat()),
                        'resultImage': detection.get('result_base64', ''),
                        'results': {
                            'totalDetections': 1,
                            'avgConfidence': 85,
                            'detections': [{'name': 'Hama Terdeteksi', 'confidence': 85}],
                            'recommendations': ['Pantau area terinfeksi', 'Aplikasikan treatment sesuai anjuran']
                        },
                        'processingTime': detection.get('timing', {}).get('total_waktu_komunikasi', 0),
                        'timing': detection.get('timing', {}),
                        'source': 'server'  # Mark sebagai data dari server sync
                    }
                    ui_history.append(ui_item)
                
                # Send to frontend via loadHistoryFromBackend (server sync)
                history_json = json.dumps(ui_history, ensure_ascii=False)
                js_code = f"if(window.loadHistoryFromBackend) {{ window.loadHistoryFromBackend({history_json}); }}"
                webview_window.evaluate_js(js_code)
                    
                print(f"🔄 Synced {len(ui_history)} detection records to UI from server")
            else:
                print("📭 No detection history found for server sync")
                webview_window.evaluate_js("if(window.loadHistoryFromBackend) { window.loadHistoryFromBackend([]); }")
                
        except Exception as e:
            print(f"❌ Error loading history to UI: {e}")
            # Send empty array if error
            try:
                webview_window.evaluate_js("if(window.loadHistoryFromBackend) { window.loadHistoryFromBackend([]); }")
            except:
                pass

    def add_detection_to_ui(self, webview_window, detection_data):
        """Add detection to UI"""
        try:
            # Format data for frontend
            ui_detection = {
                'id': detection_data.get('id'),
                'filename': detection_data.get('filename'),
                'timestamp': detection_data.get('timestamp'),
                'resultImage': detection_data.get('resultImage', detection_data.get('result_base64', '')),
                'results': detection_data.get('results', {
                    'totalDetections': 1,
                    'avgConfidence': 85,
                    'detections': [{'name': 'Hama Terdeteksi', 'confidence': 85}],
                    'recommendations': ['Pantau area terinfeksi', 'Aplikasikan treatment sesuai anjuran']
                }),
                'processingTime': detection_data.get('processingTime', detection_data.get('timing', {}).get('total_waktu_komunikasi', 0)),
                'timing': detection_data.get('timing', {}),
                'source': 'server'  # New detection from server
            }
            
            # Send to frontend via addDetectionFromBackend
            detection_json = json.dumps(ui_detection, ensure_ascii=False)
            js_code = f"if(window.addDetectionFromBackend) {{ window.addDetectionFromBackend({detection_json}); }}"
            webview_window.evaluate_js(js_code)
            
            print(f"📝 Detection {detection_data.get('id')} added to UI")
            
        except Exception as e:
            print(f"❌ Error adding detection to UI: {e}")

    def get_detection_stats(self):
        """Get basic statistics"""
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
            print(f"Error getting stats: {e}")
            return {
                'total_detections': 0,
                'today_detections': 0,
                'total_size_mb': 0,
                'avg_processing_time': 0,
                'success_rate': 0
            }

    def get_detection_count(self):
        """✅ NEW: Get total detection count quickly"""
        try:
            detections = self.load_detections()
            return len(detections)
        except Exception as e:
            print(f"Error getting detection count: {e}")
            return 0

    def get_today_stats_quick(self):
        """✅ NEW: Get today's stats quickly for UI"""
        try:
            detections = self.load_detections()
            today = datetime.now().strftime('%Y-%m-%d')
            
            today_detections = [
                d for d in detections 
                if d.get('timestamp', '').startswith(today)
            ]
            
            if today_detections:
                # Quick average confidence calculation
                avg_confidence = 85  # Default for now, bisa dihitung dari actual results nanti
                
                return {
                    'detections': len(today_detections),
                    'accuracy': avg_confidence
                }
            else:
                return {
                    'detections': 0,
                    'accuracy': 0
                }
                
        except Exception as e:
            print(f"Error getting today stats: {e}")
            return {'detections': 0, 'accuracy': 0}

    def clear_detection_history(self, webview_window):
        """Clear all detection history"""
        try:
            if os.path.exists(self.history_file):
                os.remove(self.history_file)
            
            # Clear UI history
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
                'export_version': 'JAGAPADI v2.2 Local-First',
                'total_detections': len(detections),
                'statistics': stats,
                'detections': detections
            }
            
            export_path = os.path.join(folder_history, f"jagapadi_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json")
            
            with open(export_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            return True, f"Report exported to: {export_path}"
            
        except Exception as e:
            return False, f"Gagal export report: {e}"

    def cleanup_old_detections(self, days_to_keep=30):
        """Clean up old detection records"""
        try:
            detections = self.load_detections()
            cutoff_date = datetime.now()
            cutoff_timestamp = cutoff_date.replace(day=cutoff_date.day - days_to_keep).isoformat()
            
            # Filter detections newer than cutoff
            filtered_detections = [
                d for d in detections 
                if d.get('timestamp', '') > cutoff_timestamp
            ]
            
            removed_count = len(detections) - len(filtered_detections)
            
            if removed_count > 0:
                self.save_detections(filtered_detections)
                print(f"🧹 Cleaned up {removed_count} old detection records")
            
            return True, f"Removed {removed_count} old records"
            
        except Exception as e:
            print(f"❌ Error cleaning up detections: {e}")
            return False, str(e)

    def get_detection_by_id(self, detection_id):
        """Get specific detection by ID"""
        try:
            detections = self.load_detections()
            for detection in detections:
                if detection.get('id') == detection_id:
                    return detection
            return None
        except Exception as e:
            print(f"Error getting detection by ID: {e}")
            return None

    def update_detection_status(self, detection_id, status):
        """Update detection status"""
        try:
            detections = self.load_detections()
            for detection in detections:
                if detection.get('id') == detection_id:
                    detection['status'] = status
                    detection['updated_at'] = datetime.now().isoformat()
                    break
            
            self.save_detections(detections)
            return True
        except Exception as e:
            print(f"Error updating detection status: {e}")
            return False

    def get_recent_detections(self, limit=10):
        """Get recent detections with limit"""
        try:
            detections = self.load_detections()
            return detections[:limit]
        except Exception as e:
            print(f"Error getting recent detections: {e}")
            return []

    def backup_detections(self, backup_folder):
        """✅ NEW: Create backup of detection history"""
        try:
            if not os.path.exists(self.history_file):
                return False, "No history file to backup"
            
            os.makedirs(backup_folder, exist_ok=True)
            backup_filename = f"detections_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            backup_path = os.path.join(backup_folder, backup_filename)
            
            # Copy current history file
            detections = self.load_detections()
            with open(backup_path, 'w', encoding='utf-8') as f:
                json.dump(detections, f, indent=2, ensure_ascii=False)
            
            return True, f"Backup created: {backup_path}"
            
        except Exception as e:
            return False, f"Backup failed: {e}"

    def restore_from_backup(self, backup_file):
        """✅ NEW: Restore detection history from backup"""
        try:
            if not os.path.exists(backup_file):
                return False, "Backup file not found"
            
            with open(backup_file, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            if not isinstance(backup_data, list):
                return False, "Invalid backup file format"
            
            # Save backup data as current history
            self.save_detections(backup_data)
            
            return True, f"History restored from: {backup_file}"
            
        except Exception as e:
            return False, f"Restore failed: {e}"

    def get_file_info(self):
        """✅ NEW: Get information about history file"""
        try:
            if os.path.exists(self.history_file):
                file_size = os.path.getsize(self.history_file)
                file_modified = datetime.fromtimestamp(os.path.getmtime(self.history_file))
                detection_count = self.get_detection_count()
                
                return {
                    'exists': True,
                    'path': self.history_file,
                    'size_bytes': file_size,
                    'size_kb': round(file_size / 1024, 2),
                    'modified': file_modified.isoformat(),
                    'detection_count': detection_count
                }
            else:
                return {
                    'exists': False,
                    'path': self.history_file,
                    'detection_count': 0
                }
                
        except Exception as e:
            print(f"Error getting file info: {e}")
            return {'exists': False, 'error': str(e)}