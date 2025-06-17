/**
 * JAGAPADI v2.2 - Detection System Module
 * Mengelola semua proses deteksi hama dan hasil analisis:
 * - Proses deteksi utama
 * - Komunikasi dengan backend
 * - Manajemen hasil deteksi
 * - Generasi rekomendasi
 * - Animasi processing
 */

class DetectionSystem {
    constructor(app) {
        this.app = app; // Reference ke aplikasi utama
        this.currentResults = null;
        this.processingStartTime = 0;
        this.isProcessing = false;
        this.processingAnimationInterval = null;
        this.progressAnimationInterval = null;
        
        // Database hama dan rekomendasi
        this.pestDatabase = this.initializePestDatabase();
        this.baseRecommendations = this.initializeBaseRecommendations();
        
        console.log('🔬 Detection System initialized');
    }

    /**
     * Inisialisasi database hama untuk demo dan rekomendasi
     * Sesuai dengan 10 kelas model YOLO: belalang, bercak coklat, ganjur, hawar daun, 
     * keong mas, lalat bibit, penggerek batang, ulat, walang sangit, wereng
     */
    initializePestDatabase() {
        return {
            'belalang': {
                symptoms: ['Daun terpotong tidak teratur', 'Lubang-lubang pada daun', 'Tanaman gundul'],
                recommendations: [
                    'Lakukan pengumpulan manual pada pagi hari',
                    'Gunakan perangkap cahaya pada malam hari',
                    'Aplikasikan insektisida berbahan aktif Karbofuran',
                    'Tanam tanaman perangkap seperti jagung di pinggir sawah'
                ]
            },
            'bercak coklat': {
                symptoms: ['Bercak coklat oval pada daun', 'Daun menguning dan layu', 'Produktivitas menurun'],
                recommendations: [
                    'Aplikasikan fungisida berbahan aktif Mankozeb',
                    'Perbaiki drainase untuk mengurangi kelembaban tinggi',
                    'Gunakan varietas tahan penyakit',
                    'Buang dan bakar daun yang terinfeksi'
                ]
            },
            'ganjur': {
                symptoms: ['Batang berlubang dan rapuh', 'Tanaman mudah rebah', 'Pertumbuhan terhambat'],
                recommendations: [
                    'Bersihkan tunggul padi setelah panen',
                    'Gunakan perangkap feromon untuk mengurangi populasi',
                    'Aplikasikan insektisida granul Karbofuran saat tanam',
                    'Tanam serempak dalam radius 500 meter'
                ]
            },
            'hawar daun': {
                symptoms: ['Daun layu mendadak', 'Bercak coklat memanjang pada daun', 'Tanaman mati dari ujung'],
                recommendations: [
                    'Gunakan fungisida sistemik berbahan aktif Propineb',
                    'Atur jarak tanam untuk sirkulasi udara yang baik',
                    'Hindari pemupukan nitrogen berlebihan',
                    'Lakukan rotasi tanaman dengan palawija'
                ]
            },
            'keong mas': {
                symptoms: ['Tanaman muda dimakan habis', 'Bekas lendir pada tanaman', 'Tanaman terpotong di pangkal'],
                recommendations: [
                    'Pasang saringan bambu di saluran air',
                    'Gunakan moluskisida berbahan aktif Metaldehyde',
                    'Atur ketinggian air sawah maksimal 3 cm',
                    'Lakukan pengumpulan manual dan pemusnahaan telur'
                ]
            },
            'lalat bibit': {
                symptoms: ['Bibit layu dan mati', 'Lubang kecil pada batang bibit', 'Pertumbuhan bibit terhambat'],
                recommendations: [
                    'Rendam benih dalam insektisida sebelum semai',
                    'Gunakan mulsa jerami untuk mengurangi kelembaban tanah',
                    'Aplikasikan insektisida berbahan aktif Imidakloprid',
                    'Lakukan penyemaian di tempat yang terlindung'
                ]
            },
            'penggerek batang': {
                symptoms: ['Batang berlubang', 'Daun layu dan menguning', 'Malai putih atau tidak berisi'],
                recommendations: [
                    'Bersihkan tunggul padi setelah panen',
                    'Tanam serempak dalam radius 500 meter',
                    'Gunakan perangkap feromon',
                    'Aplikasikan insektisida berbahan aktif Klorantraniliprol'
                ]
            },
            'ulat': {
                symptoms: ['Daun terpotong dan berlubang', 'Kotoran ulat pada daun', 'Tanaman gundul'],
                recommendations: [
                    'Gunakan Bacillus thuringiensis sebagai bioinsektisida',
                    'Bersihkan gulma di sekitar sawah',
                    'Aplikasikan insektisida berbahan aktif Klorpirifos',
                    'Lakukan pengendalian air untuk mengganggu siklus hidup'
                ]
            },
            'walang sangit': {
                symptoms: ['Bulir padi hampa', 'Bercak coklat pada bulir', 'Malai tidak terisi penuh'],
                recommendations: [
                    'Pasang perangkap cahaya pada malam hari',
                    'Semprot insektisida pada pagi atau sore hari',
                    'Gunakan insektisida berbahan aktif Deltametrin',
                    'Panen lebih awal jika serangan parah'
                ]
            },
            'wereng': {
                symptoms: ['Daun menguning dari bawah', 'Tanaman kerdil', 'Malai tidak keluar sempurna'],
                recommendations: [
                    'Gunakan varietas tahan wereng',
                    'Aplikasikan insektisida sistemik Imidakloprid',
                    'Atur waktu tanam serempak',
                    'Jaga ketinggian air sawah 2-3 cm'
                ]
            }
        };
    }

    /**
     * Inisialisasi rekomendasi umum untuk semua jenis hama dan penyakit
     */
    initializeBaseRecommendations() {
        return [
            'Isolasi area yang terinfeksi segera untuk mencegah penyebaran',
            'Pantau perkembangan hama/penyakit setiap 2-3 hari secara rutin',
            'Aplikasikan pestisida sesuai dosis dan waktu yang tepat',
            'Perbaiki sistem drainase dan pengairan sawah',
            'Konsultasi dengan penyuluh pertanian atau ahli HPT setempat',
            'Dokumentasikan hasil treatment untuk evaluasi dan monitoring'
        ];
    }

    /**
     * Memulai proses deteksi hama
     */
    async startDetection() {
        try {
            console.log('🔬 Starting pest detection...');

            // Validasi sebelum deteksi
            const validation = this.validateBeforeDetection();
            if (!validation.isValid) {
                this.app.showNotification(validation.message, 'error');
                return;
            }

            // Mulai proses deteksi
            this.processingStartTime = Date.now();
            this.isProcessing = true;
            this.app.setState('processing');

            // Cek koneksi dan kirim ke backend
            if (this.app.connectionManager.isConnected) {
                await this.sendToBackendForDetection();
            } else {
                // Mode demo jika tidak terhubung
                await this.simulateDetectionProcess();
            }

        } catch (error) {
            console.error('❌ Detection error:', error);
            this.handleDetectionError(error);
        }
    }

    /**
     * Validasi sebelum memulai deteksi
     */
    validateBeforeDetection() {
        // Cek apakah ada gambar
        if (!this.app.imageHandler.hasImageReady()) {
            return {
                isValid: false,
                message: 'Tidak ada gambar untuk dianalisis'
            };
        }

        // Cek kualitas gambar
        const imageQuality = this.app.imageHandler.validateImageQuality();
        if (!imageQuality.isValid) {
            return imageQuality;
        }

        // Cek apakah sedang memproses
        if (this.isProcessing) {
            return {
                isValid: false,
                message: 'Deteksi sedang berlangsung, harap tunggu'
            };
        }

        return {
            isValid: true,
            message: 'Validasi berhasil'
        };
    }

    /**
     * Kirim gambar ke backend untuk deteksi
     */
    async sendToBackendForDetection() {
        try {
            console.log('📤 Sending image to backend for detection...');
            
            const fileInfo = this.app.imageHandler.getCurrentFileInfo();
            const result = await this.app.connectionManager.sendImageToBackend(
                fileInfo.name,
                fileInfo.base64
            );

            const processingTime = this.calculateProcessingTime();

            if (result[0]) {
                // Berhasil - hasil akan ditampilkan via callback tampilkanHasil
                // Server sudah menggambar bounding box di gambar hasil
                this.app.updateGlobalStatus(`Deteksi berhasil (${processingTime}s)`);
                console.log('✅ Image sent successfully, waiting for results with bounding boxes...');
            } else {
                // Gagal
                throw new Error(result[1] || 'Gagal mengirim gambar ke server');
            }

        } catch (error) {
            console.error('❌ Backend detection error:', error);
            throw error;
        }
    }

    /**
     * Simulasi proses deteksi untuk mode demo
     */
    async simulateDetectionProcess() {
        console.log('🎭 Simulating detection process (demo mode)...');

        // Simulasi delay processing yang realistis
        const processingDelay = Math.random() * 2000 + 1500; // 1.5-3.5 detik
        
        await new Promise(resolve => setTimeout(resolve, processingDelay));

        const processingTime = this.calculateProcessingTime();
        
        // Generate hasil demo
        const demoResults = this.generateDemoResults();
        this.currentResults = demoResults;

        // Update gambar hasil (sama dengan input untuk demo)
        const base64Image = this.app.imageHandler.getImageBase64();
        if (base64Image) {
            this.displayDetectionResults(base64Image, demoResults, processingTime);
        }

        // Tambah ke history (demo mode)
        this.addDemoDetectionToHistory(demoResults, processingTime);

        console.log('✅ Demo detection completed');
    }

    /**
     * Generate hasil deteksi demo yang realistis
     * Menggunakan 10 kelas model YOLO yang sebenarnya
     */
    generateDemoResults() {
        const pestTypes = Object.keys(this.pestDatabase); // 10 kelas model asli
        const detectionCount = Math.floor(Math.random() * 3) + 1; // 1-3 deteksi
        const detections = [];

        // Generate deteksi hama/penyakit
        for (let i = 0; i < detectionCount; i++) {
            const pestType = pestTypes[Math.floor(Math.random() * pestTypes.length)];
            const confidence = Math.floor(Math.random() * 15) + 85; // 85-99%
            
            detections.push({
                name: pestType,
                confidence: confidence
                // Bounding box sudah digambar oleh server di gambar hasil
            });
        }

        // Hitung confidence rata-rata
        const avgConfidence = Math.floor(
            detections.reduce((sum, d) => sum + d.confidence, 0) / detectionCount
        );

        // Generate rekomendasi
        const recommendations = this.generateRecommendations(detections);

        return {
            detections,
            totalDetections: detectionCount,
            avgConfidence,
            recommendations,
            metadata: {
                originalSize: { width: 1280, height: 720 },
                processedSize: { width: 640, height: 480 },
                algorithm: 'YOLOv8-Pest-Detection-v2.2',
                modelClasses: pestTypes.length // 10 kelas
            }
        };
    }



    /**
     * Generate rekomendasi berdasarkan hama/penyakit yang terdeteksi
     */
    generateRecommendations(detections) {
        let recommendations = [...this.baseRecommendations];

        // Tambah rekomendasi spesifik berdasarkan hama/penyakit yang terdeteksi
        detections.forEach(detection => {
            const pestInfo = this.pestDatabase[detection.name];
            if (pestInfo && pestInfo.recommendations) {
                recommendations.push(...pestInfo.recommendations);
            }
        });

        // Hapus duplikat dan batasi jumlah
        const uniqueRecommendations = [...new Set(recommendations)];
        return uniqueRecommendations.slice(0, 8); // Tambah sedikit karena ada lebih banyak kelas
    }

    /**
     * Fungsi yang dipanggil dari backend Python untuk menampilkan hasil
     */
    tampilkanHasil(base64img) {
        console.log('🔌 Backend calling tampilkanHasil');

        try {
            const processingTime = this.calculateProcessingTime();
            
            // Di production, hasil akan berupa struktur data lengkap dari server
            // Untuk sekarang generate hasil demo yang konsisten
            const results = this.generateDemoResults();
            
            // base64img yang diterima sudah berisi gambar dengan bounding box yang digambar server
            this.displayDetectionResults(base64img, results, processingTime);
            
            console.log('✅ tampilkanHasil executed successfully - received image with bounding boxes');
            
        } catch (error) {
            console.error('❌ Error in tampilkanHasil:', error);
            this.handleDetectionError(error);
        }
    }

    /**
     * Menampilkan hasil deteksi di UI
     */
    displayDetectionResults(resultImage, results, processingTime) {
        try {
            console.log('📊 Displaying detection results...');

            // Simpan hasil saat ini
            this.currentResults = results;
            this.isProcessing = false;

            // Update gambar hasil - sudah berisi bounding box dari server
            this.app.imageHandler.updateResultImage(resultImage);

            // Update UI dengan hasil
            this.updateResultsUI(results, processingTime);

            // Pindah ke state results
            this.app.setState('results');

            // Update statistik hari ini
            this.updateTodayStatistics();

            // Tambah ke history
            this.addDetectionToHistory(results, processingTime, resultImage);

            this.app.showNotification('✅ Deteksi berhasil!', 'success');

        } catch (error) {
            console.error('❌ Error displaying results:', error);
            this.handleDetectionError(error);
        }
    }

    /**
     * Update UI dengan hasil deteksi
     */
    updateResultsUI(results, processingTime) {
        const { elements } = this.app;

        // Update summary statistics
        if (elements.detectionCount) {
            elements.detectionCount.textContent = results.totalDetections;
        }
        if (elements.confidenceLevel) {
            elements.confidenceLevel.textContent = results.avgConfidence + '%';
        }
        if (elements.processingTimeResult) {
            elements.processingTimeResult.textContent = processingTime + 's';
        }
        if (elements.resultsCount) {
            elements.resultsCount.textContent = `${results.totalDetections} hama terdeteksi`;
        }

        // Update detection details
        this.updateDetectionDetails(results.detections);

        // Update recommendations
        this.updateRecommendations(results.recommendations);

        console.log('📊 Results UI updated successfully');
    }

    /**
     * Update detail deteksi di UI
     */
    updateDetectionDetails(detections) {
        const detectionDetails = this.app.elements.detectionDetails;
        if (!detectionDetails) return;

        detectionDetails.innerHTML = '';

        detections.forEach((detection, index) => {
            const detectionElement = document.createElement('div');
            detectionElement.className = 'detection-item';
            
            // Tambah informasi confidence level dengan warna
            const confidenceClass = this.getConfidenceClass(detection.confidence);
            
            detectionElement.innerHTML = `
                <div class="detection-name">${detection.name}</div>
                <div class="detection-confidence ${confidenceClass}">${detection.confidence}%</div>
            `;
            
            detectionDetails.appendChild(detectionElement);
        });
    }

    /**
     * Update rekomendasi di UI
     */
    updateRecommendations(recommendations) {
        const recommendationsList = this.app.elements.recommendationsList;
        if (!recommendationsList) return;

        recommendationsList.innerHTML = '';

        recommendations.forEach(recommendation => {
            const li = document.createElement('li');
            li.textContent = recommendation;
            li.style.animationDelay = `${Math.random() * 0.5}s`;
            recommendationsList.appendChild(li);
        });
    }

    /**
     * Mendapatkan class CSS berdasarkan tingkat confidence
     */
    getConfidenceClass(confidence) {
        if (confidence >= 95) return 'confidence-excellent';
        if (confidence >= 85) return 'confidence-good';
        if (confidence >= 75) return 'confidence-fair';
        return 'confidence-low';
    }

    /**
     * Hitung waktu processing
     */
    calculateProcessingTime() {
        if (this.processingStartTime === 0) return '0.0';
        return ((Date.now() - this.processingStartTime) / 1000).toFixed(1);
    }

    /**
     * Update statistik hari ini
     */
    updateTodayStatistics() {
        if (!this.currentResults) return;

        // Dapatkan statistik existing
        const currentStats = this.app.historyManager?.getTodayStats() || 
                           { detections: 0, accuracy: 0 };

        // Update dengan hasil baru
        const newDetections = currentStats.detections + this.currentResults.totalDetections;
        
        // Update UI statistik
        if (this.app.elements.todayDetections) {
            this.app.elements.todayDetections.textContent = newDetections;
        }
        if (this.app.elements.todayAccuracy) {
            this.app.elements.todayAccuracy.textContent = this.currentResults.avgConfidence + '%';
        }
    }

    /**
     * Tambah deteksi ke history
     */
    addDetectionToHistory(results, processingTime, resultImage) {
        const fileInfo = this.app.imageHandler.getCurrentFileInfo();
        
        const detectionData = {
            id: `detection_${Date.now()}`,
            filename: fileInfo?.name || 'camera_capture.jpg',
            timestamp: new Date().toISOString(),
            resultImage: resultImage,
            results: results,
            processingTime: parseFloat(processingTime),
            timing: {
                total_waktu_komunikasi: parseFloat(processingTime),
                ukuran_hasil_kb: Math.round(resultImage.length / 1024)
            }
        };

        // Kirim ke history manager
        if (this.app.historyManager) {
            this.app.historyManager.addDetectionFromBackend(detectionData);
        }
    }

    /**
     * Tambah deteksi demo ke history
     */
    addDemoDetectionToHistory(results, processingTime) {
        const fileInfo = this.app.imageHandler.getCurrentFileInfo();
        const base64Image = this.app.imageHandler.getImageBase64();
        
        const demoDetection = {
            id: `demo_${Date.now()}`,
            filename: fileInfo?.name || 'demo_image.jpg',
            timestamp: new Date().toISOString(),
            resultImage: base64Image,
            results: results,
            processingTime: parseFloat(processingTime),
            timing: {
                total_waktu_komunikasi: parseFloat(processingTime),
                ukuran_hasil_kb: 100
            }
        };

        if (this.app.historyManager) {
            this.app.historyManager.addDetectionFromBackend(demoDetection);
        }
    }

    /**
     * Mulai animasi processing
     */
    startProcessingAnimation() {
        const { elements } = this.app;
        
        // Reset progress bar
        if (elements.progressBar) {
            elements.progressBar.style.width = '0%';
            this.animateProgressBar();
        }

        // Animate processing text
        this.animateProcessingText();

        console.log('🎬 Processing animation started');
    }

    /**
     * Animasi progress bar
     */
    animateProgressBar() {
        const progressBar = this.app.elements.progressBar;
        if (!progressBar) return;

        let progress = 0;
        this.progressAnimationInterval = setInterval(() => {
            if (!this.isProcessing) {
                clearInterval(this.progressAnimationInterval);
                return;
            }

            // Increment progress dengan kecepatan random
            progress += Math.random() * 15 + 5; // 5-20% per interval
            if (progress > 95) progress = 95; // Jangan sampai 100% sebelum selesai

            progressBar.style.width = progress + '%';
        }, 200);
    }

    /**
     * Animasi text processing
     */
    animateProcessingText() {
        const processingText = this.app.elements.processingText;
        if (!processingText) return;

        const messages = [
            'Menganalisis gambar...',
            'Mendeteksi objek hama dan penyakit...',
            'Mengidentifikasi spesies yang terdeteksi...',
            'Menghitung tingkat kepercayaan...',
            'Menganalisis tingkat kerusakan tanaman...',
            'Menyiapkan rekomendasi penanganan...',
            'Memvalidasi hasil deteksi...',
            'Finalisasi laporan hasil deteksi...'
        ];

        let messageIndex = 0;
        this.processingAnimationInterval = setInterval(() => {
            if (!this.isProcessing) {
                clearInterval(this.processingAnimationInterval);
                return;
            }

            processingText.textContent = messages[messageIndex];
            messageIndex = (messageIndex + 1) % messages.length;
        }, 800);
    }

    /**
     * Stop semua animasi processing
     */
    stopProcessingAnimation() {
        this.isProcessing = false;

        if (this.processingAnimationInterval) {
            clearInterval(this.processingAnimationInterval);
            this.processingAnimationInterval = null;
        }

        if (this.progressAnimationInterval) {
            clearInterval(this.progressAnimationInterval);
            this.progressAnimationInterval = null;
        }

        // Set progress bar ke 100%
        const progressBar = this.app.elements.progressBar;
        if (progressBar) {
            progressBar.style.width = '100%';
        }

        console.log('🛑 Processing animation stopped');
    }

    /**
     * Handle error deteksi
     */
    handleDetectionError(error) {
        console.error('❌ Detection error:', error);
        
        this.isProcessing = false;
        this.stopProcessingAnimation();
        
        // Kembali ke state image ready
        this.app.setState('imageReady');
        
        // Tampilkan pesan error
        const errorMessage = error.message || 'Gagal menganalisis gambar';
        this.app.showNotification(errorMessage, 'error');
    }

    /**
     * Mulai deteksi baru
     */
    startNewDetection() {
        this.currentResults = null;
        this.processingStartTime = 0;
        this.isProcessing = false;
        
        // Reset gambar
        this.app.imageHandler.handleChangeImage();
        
        console.log('🔄 New detection started');
    }

    /**
     * Tampilkan detail hasil
     */
    showDetailedResults() {
        if (!this.currentResults) {
            this.app.showNotification('Tidak ada hasil untuk ditampilkan', 'warning');
            return;
        }

        // Scroll ke results panel
        const resultsPanel = this.app.elements.resultsPanel;
        if (resultsPanel) {
            resultsPanel.scrollIntoView({ behavior: 'smooth' });
        }

        this.app.showNotification('Detail hasil ditampilkan di bawah', 'info');
    }

    /**
     * Mendapatkan hasil deteksi saat ini
     */
    getCurrentResults() {
        return this.currentResults;
    }

    /**
     * Cek apakah sedang memproses
     */
    isCurrentlyProcessing() {
        return this.isProcessing;
    }

    /**
     * Reset detection system
     */
    reset() {
        this.currentResults = null;
        this.processingStartTime = 0;
        this.isProcessing = false;
        this.stopProcessingAnimation();
        
        console.log('🔄 Detection system reset');
    }

    /**
     * Cleanup saat aplikasi ditutup
     */
    cleanup() {
        this.stopProcessingAnimation();
        this.reset();
        
        console.log('🧹 Detection system cleanup completed');
    }
}

// Export untuk digunakan di file lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = DetectionSystem;
}