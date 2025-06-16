import threading
import signal
import sys
import time
from datetime import datetime

# Import semua modul yang sudah dipisahkan
from server_modules.server_config import ServerConfig, validate_server_environment
from server_modules.server_network_manager import ServerNetworkManager
from server_modules.server_crypto_manager import ServerCryptoManager
from server_modules.server_logger import ServerLogger
from server_modules.detection_processor import DetectionProcessor

# Global variables untuk shutdown
server_running = False
active_threads = []
network_manager = None

def signal_handler(signum, frame):
    """Handler untuk shutdown dengan Ctrl+C"""
    global server_running
    print("\n[!] Shutdown signal received...")
    server_running = False
    
    if network_manager:
        network_manager.close_server_socket()
    
    print("[!] Server shutdown complete")
    sys.exit(0)

def handle_client(conn, addr, crypto_manager, logger, detection_processor):
    """
    Handle client connection - orchestrator untuk semua proses
    
    Args:
        conn: Client connection
        addr: Client address
        crypto_manager: ServerCryptoManager instance
        logger: ServerLogger instance
        detection_processor: DetectionProcessor instance
    """
    global active_threads
    
    client_ip = addr[0]
    connect_time = datetime.now()
    
    # Data untuk logging session
    session_data = {
        'ip': client_ip,
        'connect_time': connect_time,
        'file_logs': []
    }
    
    print(f"[+] Client connected: {client_ip}")
    
    try:
        # 1. AUTHENTICATION
        auth_success, auth_message = network_manager.authenticate_client(conn)
        if not auth_success:
            logger.log_error(client_ip, auth_message, "Authentication")
            return
        
        print(f"[✓] Client authenticated: {client_ip}")
        
        # 2. MAIN PROCESSING LOOP
        while server_running:
            # Receive image data dari client
            success, filename, file_data, message = network_manager.receive_image_data(conn)
            
            if not success:
                if "timeout" not in message.lower():
                    logger.log_error(client_ip, message, "Data receive")
                break
            
            print(f"[📁] Received: {filename} ({len(file_data)/1024:.1f} KB) from {client_ip}")
            
            # Validate file upload
            valid, validation_msg = ServerConfig.validate_file_upload(filename, len(file_data))
            if not valid:
                logger.log_error(client_ip, validation_msg, "File validation")
                continue
            
            # === TIMING START ===
            process_start_time = time.time()
            
            # 3. SAVE ORIGINAL FILE
            timestamp = int(time.time())
            saved_filename = f"{timestamp}_{filename}"
            original_path = f"{ServerConfig.FOLDER_ORIGINAL}/{saved_filename}"
            
            with open(original_path, "wb") as f:
                f.write(file_data)
            
            # 4. YOLO DETECTION
            detection_start = time.time()
            det_success, result_path, labels, confidence, det_time, det_msg = detection_processor.process_detection(
                original_path, saved_filename
            )
            
            if not det_success:
                logger.log_error(client_ip, det_msg, "YOLO Detection")
                continue
            
            print(f"[🎯] Detection: {filename} -> {labels if labels else 'NO_DETECTION'} (conf: {confidence:.3f}, time: {det_time:.3f}s)")
            
            # 5. AES ENCRYPTION
            encrypt_start = time.time()
            enc_success, encrypted_data, clipper, enc_msg = crypto_manager.prepare_encrypted_data(result_path)
            encrypt_time = time.time() - encrypt_start
            
            if not enc_success:
                logger.log_error(client_ip, enc_msg, "AES Encryption")
                continue
            
            # Save clipper file
            crypto_manager.save_clipper_file(clipper, saved_filename, ServerConfig.FOLDER_CLIPPER)
            
            # 6. SEND ENCRYPTED DATA
            send_success, send_msg = network_manager.send_encrypted_data(conn, encrypted_data)
            
            if not send_success:
                logger.log_error(client_ip, send_msg, "Data send")
                break
            
            # 7. RECEIVE CLIENT TIMING (Optional)
            client_timing = network_manager.receive_client_timing_data(conn)
            
            # === TIMING END ===
            total_process_time = time.time() - process_start_time
            
            # 8. LOG FILE PROCESSING
            file_log_entry = {
                'filename': filename,
                'labels': labels,
                'size_ori': len(file_data) / 1024,
                'size_enc': len(encrypted_data) / 1024,
                'waktu_deteksi': det_time,
                'waktu_enkripsi': encrypt_time,
                'confidence': confidence,
                'waktu_dekripsi_client': client_timing.get('waktu_dekripsi_client', 0) if client_timing else 0
            }
            
            session_data['file_logs'].append(file_log_entry)
            
            # Log timing summary
            logger.log_timing_summary(filename, file_log_entry)
            
            print(f"[✓] Completed: {filename} | Total: {total_process_time:.3f}s | "
                  f"Detection: {det_time:.3f}s | Encryption: {encrypt_time:.3f}s")
    
    except Exception as e:
        if server_running:  # Only log errors if not shutting down
            logger.log_error(client_ip, str(e), "Client handling")
            print(f"[!] Error with {client_ip}: {e}")
    
    finally:
        # 9. CLEANUP & LOGGING
        disconnect_time = datetime.now()
        session_duration = (disconnect_time - connect_time).total_seconds()
        
        # Log session jika ada aktivitas
        if session_data['file_logs']:
            logger.log_client_session(session_data, disconnect_time, session_duration)
            logger.log_to_csv(session_data)
            print(f"[📝] Session logged: {client_ip} - {len(session_data['file_logs'])} files, {session_duration:.1f}s")
        
        conn.close()
        print(f"[-] Client disconnected: {client_ip}")
        
        # Remove from active threads
        current_thread = threading.current_thread()
        if current_thread in active_threads:
            active_threads.remove(current_thread)

def start_server():
    """
    Main server function - orchestrator utama
    """
    global server_running, network_manager, active_threads
    
    # 1. VALIDATE ENVIRONMENT
    print("🔍 Validating server environment...")
    valid, issues = validate_server_environment()
    if not valid:
        print("❌ Server environment validation failed:")
        for issue in issues:
            print(f"   - {issue}")
        print("Please fix the issues above and restart the server.")
        return
    
    # 2. PRINT STARTUP BANNER
    ServerConfig.print_startup_banner()
    
    # 3. INITIALIZE ALL MANAGERS
    print("⚙️  Initializing server components...")
    
    try:
        # Network Manager
        network_config = ServerConfig.get_network_config()
        network_manager = ServerNetworkManager(**network_config)
        server_socket = network_manager.create_server_socket()
        
        # Crypto Manager
        crypto_config = ServerConfig.get_crypto_config()
        crypto_manager = ServerCryptoManager(**crypto_config)
        
        # Logger
        logger_config = ServerConfig.get_logger_config()
        logger = ServerLogger(**logger_config)
        
        # Detection Processor
        detection_config = ServerConfig.get_detection_config()
        detection_processor = DetectionProcessor(**detection_config)
        
        # Load YOLO model
        model_success, model_msg = detection_processor.load_model()
        if not model_success:
            print(f"❌ Failed to load YOLO model: {model_msg}")
            return
        
        print(f"✅ {model_msg}")
        
    except Exception as e:
        print(f"❌ Failed to initialize server components: {e}")
        return
    
    # 4. SETUP SIGNAL HANDLERS
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # 5. START SERVER LOOP
    server_running = True
    print("🚀 Server ready for connections!")
    print("   Press Ctrl+C to shutdown")
    print("=" * 70)
    
    try:
        while server_running:
            try:
                # Accept client connection
                server_socket.settimeout(1.0)  # Non-blocking accept
                conn, addr = server_socket.accept()
                
                if not server_running:
                    conn.close()
                    break
                
                # Create thread untuk handle client
                client_thread = threading.Thread(
                    target=handle_client,
                    args=(conn, addr, crypto_manager, logger, detection_processor)
                )
                
                active_threads.append(client_thread)
                client_thread.start()
                
                # Cleanup finished threads
                active_threads = [t for t in active_threads if t.is_alive()]
                
            except OSError:
                if server_running:
                    time.sleep(0.1)  # Brief pause jika socket timeout
                else:
                    break  # Server shutdown
                    
    except Exception as e:
        if server_running:
            print(f"❌ Server error: {e}")
    
    finally:
        # 6. CLEANUP
        print("\n🛑 Shutting down server...")
        server_running = False
        
        # Wait untuk semua client threads selesai
        for thread in active_threads:
            thread.join(timeout=5)
        
        if network_manager:
            network_manager.close_server_socket()
        
        print("✅ Server shutdown complete")

if __name__ == '__main__':
    start_server()