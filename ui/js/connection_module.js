/**
 * JAGAPADI v2.2 - Connection Module
 * Mengelola koneksi ke server dan komunikasi dengan backend Python
 */

class ConnectionManager {
    constructor(app) {
        this.app = app; // Reference ke aplikasi utama
        this.isConnected = false;
        this.connectionState = 'disconnected';
        
        console.log('🔌 Connection Manager initialized');
    }

    /**
     * Mengatur status koneksi dan memperbarui tampilan UI
     */
    setConnectionState(state) {
        console.log(`🔄 Connection state: ${this.connectionState} → ${state}`);
        
        this.connectionState = state;
        const { elements } = this.app;
        
        // Hapus semua class status sebelumnya
        elements.statusIndicator?.classList.remove('connected', 'connecting');
        elements.connectBtn?.classList.remove('connected', 'connecting');
        elements.mainStatusDot?.classList.remove('connected', 'connecting');
        
        switch(state) {
            case 'connected':
                this.updateUIForConnected(elements);
                break;
                
            case 'connecting':
                this.updateUIForConnecting(elements);
                break;
                
            case 'disconnected':
            default:
                this.updateUIForDisconnected(elements);
                break;
        }
    }

    /**
     * Memperbarui tampilan UI ketika status terhubung
     */
    updateUIForConnected(elements) {
        if (elements.connectBtn) {
            elements.connectBtn.textContent = 'Terhubung';
            elements.connectBtn.classList.add('connected');
        }
        if (elements.statusIndicator) {
            elements.statusIndicator.classList.add('connected');
        }
        if (elements.statusText) {
            elements.statusText.textContent = 'Terhubung';
        }
        if (elements.mainStatusDot) {
            elements.mainStatusDot.classList.add('connected');
        }
        if (elements.mainStatusText) {
            elements.mainStatusText.textContent = 'Server terhubung';
        }
    }

    /**
     * Memperbarui tampilan UI ketika sedang menghubungkan
     */
    updateUIForConnecting(elements) {
        if (elements.connectBtn) {
            elements.connectBtn.textContent = 'Menghubungkan...';
            elements.connectBtn.classList.add('connecting');
        }
        if (elements.statusIndicator) {
            elements.statusIndicator.classList.add('connecting');
        }
        if (elements.statusText) {
            elements.statusText.textContent = 'Menghubungkan...';
        }
        if (elements.mainStatusDot) {
            elements.mainStatusDot.classList.add('connecting');
        }
        if (elements.mainStatusText) {
            elements.mainStatusText.textContent = 'Menghubungkan...';
        }
    }

    /**
     * Memperbarui tampilan UI ketika terputus
     */
    updateUIForDisconnected(elements) {
        if (elements.connectBtn) {
            elements.connectBtn.textContent = 'Connect';
        }
        if (elements.statusText) {
            elements.statusText.textContent = 'Tidak Terhubung';
        }
        if (elements.mainStatusText) {
            elements.mainStatusText.textContent = 'Hubungkan ke server';
        }
    }

    /**
     * Memperbarui status tombol berdasarkan koneksi
     */
    updateButtonStates() {
        const { elements } = this.app;
        const buttonsToUpdate = [
            elements.cameraBtn,
            elements.fileBtn,
            elements.detectBtn
        ];
        
        buttonsToUpdate.forEach(button => {
            if (button) {
                button.disabled = !this.isConnected;
            }
        });
    }

    /**
     * Proses koneksi ke server dengan password
     */
    async connect() {
        const password = this.app.elements.passwordInput?.value;
        
        if (!password) {
            this.app.showNotification('Masukkan password!', 'error');
            return;
        }

        try {
            this.setConnectionState('connecting');
            
            // Cek apakah PyWebView API tersedia
            if (this.isPyWebViewAvailable()) {
                await this.connectViaPyWebView(password);
            } else {
                // Mode demo jika tidak ada PyWebView
                await this.connectDemoMode();
            }
        } catch (error) {
            console.error('❌ Connection error:', error);
            this.setConnectionState('disconnected');
            this.app.showNotification('Gagal terhubung ke server', 'error');
        }
    }

    /**
     * Cek apakah PyWebView API tersedia
     */
    isPyWebViewAvailable() {
        return window.pywebview && 
               window.pywebview.api && 
               window.pywebview.api.connect_to_server;
    }

    /**
     * Koneksi melalui PyWebView API
     */
    async connectViaPyWebView(password) {
        console.log('🔌 Connecting via PyWebView API...');
        
        const result = await window.pywebview.api.connect_to_server(password);
        
        if (result[0]) {
            // Koneksi berhasil
            this.isConnected = true;
            this.setConnectionState('connected');
            this.updateButtonStates();
            this.app.hideAuthModal();
            this.app.showNotification(result[1], 'success');
            
            // History akan dimuat melalui sinyal frontend_ready
            console.log('🔌 Connected successfully, history will load after frontend_ready signal');
        } else {
            // Koneksi gagal
            this.setConnectionState('disconnected');
            this.app.showNotification(result[1], 'error');
        }
    }

    /**
     * Mode demo untuk testing tanpa server
     */
    async connectDemoMode() {
        console.log('🔌 Connecting in demo mode...');
        
        // Simulasi delay koneksi
        await new Promise(resolve => setTimeout(resolve, 1500));
        
        this.isConnected = true;
        this.setConnectionState('connected');
        this.updateButtonStates();
        this.app.hideAuthModal();
        this.app.showNotification('Demo mode: Terhubung ke server', 'success');
        
        // Muat history demo
        const demoHistory = this.generateDemoHistory();
        this.app.historyManager.loadHistoryFromBackend(demoHistory);
    }

    /**
     * Proses pemutusan koneksi
     */
    async disconnect() {
        try {
            // Coba putuskan koneksi melalui API jika tersedia
            if (window.pywebview && window.pywebview.api && window.pywebview.api.disconnect) {
                await window.pywebview.api.disconnect();
            }
            
            this.isConnected = false;
            this.setConnectionState('disconnected');
            this.updateButtonStates();
            
            // Reset ke kondisi awal jika tidak sedang memproses
            if (this.app.currentState !== 'processing') {
                this.app.setState('initial');
            }
            
            this.app.showNotification('Terputus dari server', 'info');
            
        } catch (error) {
            console.error('❌ Disconnect error:', error);
            
            // Tetap reset status meskipun ada error
            this.isConnected = false;
            this.setConnectionState('disconnected');
            this.updateButtonStates();
            this.app.showNotification('Terputus dari server', 'info');
        }
    }

    /**
     * Sinyal ke backend Python bahwa frontend sudah siap
     */
    signalFrontendReady() {
        try {
            console.log('🎯 Signaling frontend ready to backend...');
            
            if (window.pywebview && window.pywebview.api && window.pywebview.api.frontend_ready) {
                console.log('🔌 Signaling Python backend via API...');
                window.pywebview.api.frontend_ready();
            } else {
                console.log('⚠️ PyWebView API not available, using fallback method');
                // Metode cadangan: set flag global
                window._frontendReady = true;
            }
        } catch (error) {
            console.error('❌ Failed to signal frontend ready:', error);
            // Set flag cadangan
            window._frontendReady = true;
        }
    }

    /**
     * Kirim gambar ke backend untuk diproses
     */
    async sendImageToBackend(filename, base64Data) {
        if (!this.isConnected) {
            throw new Error('Tidak terhubung ke server');
        }

        try {
            if (this.isPyWebViewAvailable() && window.pywebview.api.send_image) {
                console.log('📤 Sending image to backend via API...');
                return await window.pywebview.api.send_image(filename, base64Data);
            } else {
                // Mode demo - return success
                console.log('📤 Demo mode: Simulating image send...');
                return [true, 'Demo: Gambar berhasil dikirim'];
            }
        } catch (error) {
            console.error('❌ Error sending image to backend:', error);
            throw error;
        }
    }

    /**
     * Generate history demo untuk mode testing
     */
    generateDemoHistory() {
        const demoItems = [];
        const pestTypes = ['Wereng Batang Coklat', 'Penggerek Batang Padi', 'Walang Sangit'];
        
        for (let i = 0; i < 3; i++) {
            const timestamp = new Date();
            timestamp.setHours(timestamp.getHours() - i * 2);
            
            demoItems.push({
                id: `demo_${Date.now()}_${i}`,
                filename: `demo_image_${i + 1}.jpg`,
                timestamp: timestamp.toISOString(),
                resultImage: '/placeholder-image.jpg',
                results: {
                    totalDetections: Math.floor(Math.random() * 3) + 1,
                    avgConfidence: Math.floor(Math.random() * 20) + 80,
                    detections: [{
                        name: pestTypes[Math.floor(Math.random() * pestTypes.length)],
                        confidence: Math.floor(Math.random() * 20) + 80
                    }],
                    recommendations: ['Demo recommendation 1', 'Demo recommendation 2']
                },
                processingTime: (Math.random() * 5 + 1).toFixed(1),
                timing: {
                    total_waktu_komunikasi: Math.random() * 5 + 1,
                    ukuran_hasil_kb: Math.random() * 100 + 50
                }
            });
        }
        
        return demoItems;
    }

    /**
     * Mendapatkan status koneksi saat ini
     */
    getConnectionStatus() {
        return {
            isConnected: this.isConnected,
            state: this.connectionState,
            hasAPI: this.isPyWebViewAvailable()
        };
    }

    /**
     * Cek apakah sedang dalam proses koneksi
     */
    isConnecting() {
        return this.connectionState === 'connecting';
    }

    /**
     * Tunggu sampai koneksi selesai (berhasil atau gagal)
     */
    async waitForConnection() {
        return new Promise((resolve) => {
            const checkConnection = () => {
                if (this.connectionState !== 'connecting') {
                    resolve(this.isConnected);
                } else {
                    setTimeout(checkConnection, 100);
                }
            };
            checkConnection();
        });
    }
}

// Export untuk digunakan di file lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ConnectionManager;
}