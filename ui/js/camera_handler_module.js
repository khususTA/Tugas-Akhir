/**
 * JAGAPADI v2.2 - Camera Handler Module
 * Mengelola semua fungsi yang berhubungan dengan akses kamera:
 * - Akses kamera device
 * - Mengambil foto
 * - Preview kamera
 * - Pengaturan kamera
 */

class CameraHandler {
    constructor(app) {
        this.app = app; // Reference ke aplikasi utama
        this.currentStream = null;
        this.isModalOpen = false;
        this.cameraSettings = {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            facingMode: 'environment' // Kamera belakang untuk foto objek
        };
        
        console.log('📷 Camera Handler initialized');
    }

    /**
     * Menangani aksi kamera - membuka kamera device
     */
    async handleCameraAction() {
        if (!this.app.connectionManager.isConnected) {
            this.app.showNotification('Hubungkan ke server terlebih dahulu', 'warning');
            return;
        }

        if (!this.isCameraSupported()) {
            this.app.showNotification('Kamera tidak didukung di device ini', 'error');
            return;
        }

        try {
            await this.openCamera();
        } catch (error) {
            this.handleCameraError(error);
        }
    }

    /**
     * Cek apakah device mendukung akses kamera
     */
    isCameraSupported() {
        return !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia);
    }

    /**
     * Membuka akses kamera untuk mengambil foto
     */
    async openCamera() {
        try {
            console.log('📷 Requesting camera access...');
            
            // Minta akses kamera
            const stream = await navigator.mediaDevices.getUserMedia({
                video: this.cameraSettings
            });

            this.currentStream = stream;
            this.showCameraModal(stream);

        } catch (error) {
            console.error('❌ Camera access error:', error);
            throw error;
        }
    }

    /**
     * Menangani error akses kamera
     */
    handleCameraError(error) {
        let message = 'Gagal mengakses kamera';
        
        switch (error.name) {
            case 'NotAllowedError':
                message = 'Akses kamera ditolak. Berikan izin kamera di browser.';
                break;
            case 'NotFoundError':
                message = 'Kamera tidak ditemukan di device ini.';
                break;
            case 'NotReadableError':
                message = 'Kamera sedang digunakan aplikasi lain.';
                break;
            case 'OverconstrainedError':
                message = 'Pengaturan kamera tidak didukung.';
                break;
            case 'SecurityError':
                message = 'Koneksi tidak aman. Gunakan HTTPS untuk akses kamera.';
                break;
            default:
                message = `Error kamera: ${error.message}`;
        }
        
        this.app.showNotification(message, 'error');
        
        // Fallback ke file picker
        setTimeout(() => {
            this.app.showNotification('Membuka file picker sebagai alternatif...', 'info');
            this.app.imageHandler.handleFileAction();
        }, 2000);
    }

    /**
     * Menampilkan modal kamera untuk mengambil foto
     */
    showCameraModal(stream) {
        if (this.isModalOpen) {
            console.log('⚠️ Camera modal already open');
            return;
        }

        // Buat elemen modal kamera
        const cameraModal = this.createCameraModal();
        const video = cameraModal.querySelector('#cameraVideo');
        const captureBtn = cameraModal.querySelector('#captureBtn');
        const closeCameraBtn = cameraModal.querySelector('#closeCameraBtn');
        const switchCameraBtn = cameraModal.querySelector('#switchCameraBtn');

        // Set video stream
        video.srcObject = stream;
        video.play();

        // Event listener untuk tombol capture
        captureBtn.addEventListener('click', () => {
            this.capturePhoto(video);
        });

        // Event listener untuk tombol close
        closeCameraBtn.addEventListener('click', () => {
            this.closeCameraModal(cameraModal);
        });

        // Event listener untuk switch kamera (jika ada multiple camera)
        switchCameraBtn.addEventListener('click', () => {
            this.switchCamera(video);
        });

        // Event listener untuk keyboard
        document.addEventListener('keydown', this.handleCameraKeyboard.bind(this));

        // Tampilkan modal
        document.body.appendChild(cameraModal);
        setTimeout(() => {
            cameraModal.classList.add('show');
        }, 10);
        
        this.isModalOpen = true;
        console.log('📷 Camera modal opened');
    }

    /**
     * Membuat elemen modal kamera
     */
    createCameraModal() {
        const modal = document.createElement('div');
        modal.className = 'camera-modal';
        modal.innerHTML = `
            <div class="camera-modal-content">
                <div class="camera-header">
                    <h3>📷 Ambil Foto Tanaman</h3>
                    <button id="closeCameraBtn" class="close-btn" title="Tutup">&times;</button>
                </div>
                <div class="camera-body">
                    <div class="camera-preview">
                        <video id="cameraVideo" autoplay playsinline muted></video>
                        <div class="camera-overlay">
                            <div class="focus-frame"></div>
                        </div>
                    </div>
                    <div class="camera-controls">
                        <button id="switchCameraBtn" class="camera-control-btn" title="Ganti Kamera">🔄</button>
                        <button id="captureBtn" class="capture-btn" title="Ambil Foto">📷</button>
                        <button class="camera-control-btn" title="Pengaturan">⚙️</button>
                    </div>
                    <div class="camera-tips">
                        <p>💡 Tips: Pastikan tanaman terlihat jelas dan pencahayaan cukup</p>
                    </div>
                </div>
            </div>
        `;
        
        // Tambahkan CSS untuk modal
        this.addCameraModalStyles();
        
        return modal;
    }

    /**
     * Menambahkan CSS untuk modal kamera
     */
    addCameraModalStyles() {
        if (document.getElementById('camera-modal-styles')) return;
        
        const style = document.createElement('style');
        style.id = 'camera-modal-styles';
        style.textContent = `
            .camera-modal {
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                background: rgba(0, 0, 0, 0.9);
                display: flex;
                align-items: center;
                justify-content: center;
                z-index: 10000;
                opacity: 0;
                transition: opacity 0.3s ease;
            }
            
            .camera-modal.show {
                opacity: 1;
            }
            
            .camera-modal-content {
                background: var(--bg-secondary, #1e1e1e);
                border-radius: 12px;
                max-width: 90vw;
                max-height: 90vh;
                overflow: hidden;
                box-shadow: 0 20px 40px rgba(0, 0, 0, 0.5);
            }
            
            .camera-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                padding: 16px 20px;
                border-bottom: 1px solid var(--border-color, #333);
                background: var(--bg-primary, #000);
            }
            
            .camera-header h3 {
                margin: 0;
                color: var(--text-primary, #fff);
                font-size: 1.1rem;
            }
            
            .close-btn {
                background: none;
                border: none;
                color: var(--text-primary, #fff);
                font-size: 24px;
                cursor: pointer;
                padding: 0;
                width: 32px;
                height: 32px;
                border-radius: 50%;
                display: flex;
                align-items: center;
                justify-content: center;
                transition: background 0.2s;
            }
            
            .close-btn:hover {
                background: rgba(255, 255, 255, 0.1);
            }
            
            .camera-body {
                padding: 20px;
            }
            
            .camera-preview {
                position: relative;
                border-radius: 8px;
                overflow: hidden;
                background: #000;
                margin-bottom: 16px;
            }
            
            #cameraVideo {
                width: 100%;
                height: auto;
                max-width: 640px;
                max-height: 480px;
                display: block;
            }
            
            .camera-overlay {
                position: absolute;
                top: 0;
                left: 0;
                right: 0;
                bottom: 0;
                pointer-events: none;
            }
            
            .focus-frame {
                position: absolute;
                top: 50%;
                left: 50%;
                transform: translate(-50%, -50%);
                width: 200px;
                height: 200px;
                border: 2px solid rgba(255, 255, 255, 0.5);
                border-radius: 8px;
            }
            
            .camera-controls {
                display: flex;
                justify-content: center;
                align-items: center;
                gap: 16px;
                margin-bottom: 12px;
            }
            
            .capture-btn {
                background: var(--primary-color, #4CAF50);
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 50px;
                font-size: 1rem;
                cursor: pointer;
                transition: all 0.2s;
                box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
            }
            
            .capture-btn:hover {
                background: var(--primary-hover, #45a049);
                transform: scale(1.05);
            }
            
            .camera-control-btn {
                background: rgba(255, 255, 255, 0.1);
                color: var(--text-primary, #fff);
                border: none;
                padding: 10px;
                border-radius: 50%;
                font-size: 1.2rem;
                cursor: pointer;
                transition: background 0.2s;
                width: 44px;
                height: 44px;
            }
            
            .camera-control-btn:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            
            .camera-tips {
                text-align: center;
                color: var(--text-muted, #aaa);
                font-size: 0.9rem;
            }
            
            @media (max-width: 768px) {
                .camera-modal-content {
                    max-width: 95vw;
                    max-height: 95vh;
                }
                
                .camera-body {
                    padding: 16px;
                }
                
                .focus-frame {
                    width: 150px;
                    height: 150px;
                }
            }
        `;
        
        document.head.appendChild(style);
    }

    /**
     * Mengambil foto dari video stream
     */
    capturePhoto(video) {
        try {
            console.log('📸 Capturing photo...');
            
            // Buat canvas untuk menangkap gambar
            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');

            // Set ukuran canvas sesuai video
            canvas.width = video.videoWidth;
            canvas.height = video.videoHeight;

            // Gambar frame video ke canvas
            context.drawImage(video, 0, 0, canvas.width, canvas.height);

            // Konversi ke base64 dengan kualitas tinggi
            const base64Data = canvas.toDataURL('image/jpeg', 0.9);
            
            // Generate filename dengan timestamp
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-');
            const filename = `camera_capture_${timestamp}.jpg`;
            
            // Kirim ke image handler untuk diproses
            this.app.imageHandler.createFileFromBase64(base64Data, filename);

            // Tutup modal kamera
            this.closeCameraModal();
            
            this.app.showNotification('📷 Foto berhasil diambil!', 'success');
            
            console.log('✅ Photo captured successfully');

        } catch (error) {
            console.error('❌ Error capturing photo:', error);
            this.app.showNotification('Gagal mengambil foto', 'error');
        }
    }

    /**
     * Switch antara kamera depan dan belakang
     */
    async switchCamera(video) {
        try {
            console.log('🔄 Switching camera...');
            
            // Toggle facingMode
            const currentFacingMode = this.cameraSettings.facingMode;
            this.cameraSettings.facingMode = currentFacingMode === 'environment' ? 'user' : 'environment';
            
            // Stop current stream
            if (this.currentStream) {
                this.currentStream.getTracks().forEach(track => track.stop());
            }
            
            // Request new stream with different camera
            const newStream = await navigator.mediaDevices.getUserMedia({
                video: this.cameraSettings
            });
            
            this.currentStream = newStream;
            video.srcObject = newStream;
            
            const cameraType = this.cameraSettings.facingMode === 'environment' ? 'belakang' : 'depan';
            this.app.showNotification(`Berganti ke kamera ${cameraType}`, 'info');
            
        } catch (error) {
            console.error('❌ Error switching camera:', error);
            this.app.showNotification('Gagal mengganti kamera', 'error');
            
            // Revert to previous setting
            this.cameraSettings.facingMode = this.cameraSettings.facingMode === 'environment' ? 'user' : 'environment';
        }
    }

    /**
     * Handle keyboard shortcuts untuk modal kamera
     */
    handleCameraKeyboard(e) {
        if (!this.isModalOpen) return;
        
        switch (e.key) {
            case 'Escape':
                e.preventDefault();
                this.closeCameraModal();
                break;
            case ' ':
            case 'Enter':
                e.preventDefault();
                const captureBtn = document.getElementById('captureBtn');
                if (captureBtn) captureBtn.click();
                break;
            case 's':
            case 'S':
                e.preventDefault();
                const switchBtn = document.getElementById('switchCameraBtn');
                if (switchBtn) switchBtn.click();
                break;
        }
    }

    /**
     * Menutup modal kamera dan menghentikan stream
     */
    closeCameraModal(modalElement = null) {
        try {
            console.log('🔒 Closing camera modal...');
            
            // Hentikan stream kamera
            if (this.currentStream) {
                this.currentStream.getTracks().forEach(track => {
                    track.stop();
                    console.log(`🛑 Stopped camera track: ${track.kind}`);
                });
                this.currentStream = null;
            }
            
            // Hapus event listener keyboard
            document.removeEventListener('keydown', this.handleCameraKeyboard);
            
            // Tutup modal
            const modal = modalElement || document.querySelector('.camera-modal');
            if (modal) {
                modal.classList.remove('show');
                setTimeout(() => {
                    if (modal.parentNode) {
                        modal.parentNode.removeChild(modal);
                    }
                }, 300);
            }
            
            this.isModalOpen = false;
            console.log('✅ Camera modal closed');
            
        } catch (error) {
            console.error('❌ Error closing camera modal:', error);
            this.isModalOpen = false;
        }
    }

    /**
     * Mendapatkan daftar kamera yang tersedia
     */
    async getAvailableCameras() {
        try {
            const devices = await navigator.mediaDevices.enumerateDevices();
            const cameras = devices.filter(device => device.kind === 'videoinput');
            
            console.log(`📷 Found ${cameras.length} camera(s)`);
            return cameras;
            
        } catch (error) {
            console.error('❌ Error getting camera list:', error);
            return [];
        }
    }

    /**
     * Update pengaturan kamera
     */
    updateCameraSettings(newSettings) {
        this.cameraSettings = {
            ...this.cameraSettings,
            ...newSettings
        };
        
        console.log('⚙️ Camera settings updated:', this.cameraSettings);
    }

    /**
     * Cek apakah modal kamera sedang terbuka
     */
    isModalActive() {
        return this.isModalOpen;
    }

    /**
     * Force close modal (untuk cleanup)
     */
    forceCloseModal() {
        if (this.isModalOpen) {
            this.closeCameraModal();
        }
    }

    /**
     * Cleanup saat aplikasi ditutup
     */
    cleanup() {
        this.forceCloseModal();
        
        // Hapus CSS styles
        const styles = document.getElementById('camera-modal-styles');
        if (styles) {
            styles.remove();
        }
        
        console.log('🧹 Camera handler cleanup completed');
    }
}

// Export untuk digunakan di file lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CameraHandler;
}