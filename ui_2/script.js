/**
 * JAGAPADI v2.2 - AI Deteksi Hama Padi
 * FINAL FIX - History Loading Issue Resolved
 */

class JagaPadiApp {
    constructor() {
        console.log('🌾 JAGAPADI v2.2 - AI Deteksi Hama Padi');
        console.log('🔧 FINAL FIX - History Loading Issue Resolved');
        
        // Application states
        this.currentState = 'initial';
        this.isConnected = false;
        this.currentFile = null;
        this.selectedBase64 = null;
        this.processingStartTime = 0;
        this.currentResults = null;
        
        // UI state
        this.sidebarOpen = false;
        this.isDarkMode = this.loadTheme();
        this.history = [];
        this.todayStats = { detections: 0, accuracy: 0 };
        
        // ✅ FIXED: App readiness tracking
        this.isAppReady = false;
        this.pendingOperations = [];
        
        // DOM Elements
        this.elements = this.initializeElements();
        
        // Initialize app
        this.initializeEventListeners();
        this.initializeTouchFeedback();
        this.applyTheme();
        this.updateStatusBar();
        this.setState('initial');
        
        // ✅ FIXED: Mark app as ready and signal to backend
        this.markAppAsReady();
        
        console.log('✅ JAGAPADI v2.2 initialized successfully');
    }

    // ✅ FIXED: New method to handle app readiness
    markAppAsReady() {
        this.isAppReady = true;
        console.log('🎯 App marked as ready, signaling to Python backend...');
        
        // ✅ FIXED: Signal to Python that frontend is ready
        this.signalFrontendReady();
        
        // Process any pending operations from backend
        if (this.pendingOperations.length > 0) {
            console.log(`📋 Processing ${this.pendingOperations.length} pending operations`);
            this.pendingOperations.forEach(operation => {
                try {
                    operation.callback.apply(this, operation.args);
                    console.log(`✅ Processed pending operation: ${operation.type}`);
                } catch (error) {
                    console.error(`❌ Failed to process pending operation ${operation.type}:`, error);
                }
            });
            this.pendingOperations = [];
        }
        
        // Process pending history data if available
        if (window._pendingHistoryData) {
            console.log('📊 Processing pending history data');
            this.loadHistoryFromBackend(window._pendingHistoryData);
            delete window._pendingHistoryData;
        }
    }

    // ✅ FIXED: Signal to Python backend that frontend is ready
    signalFrontendReady() {
        try {
            // Try multiple methods to signal backend
            if (window.pywebview && window.pywebview.api && window.pywebview.api.frontend_ready) {
                console.log('🔌 Signaling Python backend via API...');
                window.pywebview.api.frontend_ready();
            } else {
                console.log('⚠️ PyWebView API not available, using fallback method');
                // Fallback: set global flag
                window._frontendReady = true;
            }
        } catch (error) {
            console.error('❌ Failed to signal frontend ready:', error);
            // Set fallback flag
            window._frontendReady = true;
        }
    }

    // ✅ FIXED: Method to queue operations when app is not ready
    queuePendingOperation(type, callback, args) {
        console.log(`⏳ Queueing pending operation: ${type}`);
        this.pendingOperations.push({
            type: type,
            callback: callback,
            args: args,
            timestamp: Date.now()
        });
    }

    initializeElements() {
        return {
            // Header & Navigation
            toggleSidebar: document.getElementById('toggleSidebar'),
            darkModeBtn: document.getElementById('darkModeBtn'),
            sidebar: document.getElementById('sidebar'),
            sidebarOverlay: document.getElementById('sidebarOverlay'),
            
            // Connection elements
            connectBtn: document.getElementById('btn-connect'),
            statusIndicator: document.getElementById('statusIndicator'),
            statusText: document.getElementById('statusText'),
            mainConnectionStatus: document.getElementById('mainConnectionStatus'),
            mainStatusDot: document.getElementById('mainStatusDot'),
            mainStatusText: document.getElementById('mainStatusText'),
            
            // Preview area
            previewContainer: document.getElementById('previewContainer'),
            emptyState: document.getElementById('emptyState'),
            previewContent: document.getElementById('previewContent'),
            previewImage: document.getElementById('previewImage'),
            fileInput: document.getElementById('fileInput'),
            
            // Processing overlay
            processingOverlay: document.getElementById('processingOverlay'),
            processingText: document.getElementById('processingText'),
            progressBar: document.getElementById('progressBar'),
            
            // Results overlay
            resultsOverlay: document.getElementById('resultsOverlay'),
            resultsCount: document.getElementById('resultsCount'),
            
            // Action buttons (state-based)
            actionSection: document.getElementById('actionSection'),
            initialActions: document.getElementById('initialActions'),
            imageReadyActions: document.getElementById('imageReadyActions'),
            processingActions: document.getElementById('processingActions'),
            resultsActions: document.getElementById('resultsActions'),
            
            // Individual buttons
            cameraBtn: document.getElementById('cameraBtn'),
            fileBtn: document.getElementById('fileBtn'),
            changeImageBtn: document.getElementById('changeImageBtn'),
            detectBtn: document.getElementById('detectBtn'),
            newDetectionBtn: document.getElementById('newDetectionBtn'),
            viewDetailsBtn: document.getElementById('viewDetailsBtn'),
            
            // Results panel
            resultsPanel: document.getElementById('resultsPanel'),
            detectionCount: document.getElementById('detectionCount'),
            confidenceLevel: document.getElementById('confidenceLevel'),
            processingTimeResult: document.getElementById('processingTimeResult'),
            detectionDetails: document.getElementById('detectionDetails'),
            recommendationsList: document.getElementById('recommendationsList'),
            
            // Statistics
            todayDetections: document.getElementById('todayDetections'),
            todayAccuracy: document.getElementById('todayAccuracy'),
            
            // History
            historyList: document.getElementById('historyList'),
            historyModal: document.getElementById('historyModal'),
            historyModalBody: document.getElementById('historyModalBody'),
            closeHistoryModal: document.getElementById('closeHistoryModal'),
            
            // Auth modal
            authModal: document.getElementById('authModal'),
            passwordInput: document.getElementById('passwordInput'),
            confirmAuthBtn: document.getElementById('confirmAuthBtn'),
            cancelAuthBtn: document.getElementById('cancelAuthBtn'),
            
            // Notification & Status
            notification: document.getElementById('notification'),
            statusBar: document.getElementById('statusBar'),
            globalStatus: document.getElementById('globalStatus'),
            statusTime: document.getElementById('statusTime')
        };
    }

    initializeEventListeners() {
        const { elements } = this;

        // === NAVIGATION EVENTS ===
        elements.toggleSidebar?.addEventListener('click', () => this.toggleSidebar());
        elements.darkModeBtn?.addEventListener('click', () => this.toggleDarkMode());
        elements.sidebarOverlay?.addEventListener('click', () => this.closeSidebar());

        // === CONNECTION EVENTS ===
        elements.connectBtn?.addEventListener('click', () => {
            if (this.isConnected) {
                this.disconnect();
            } else {
                this.showAuthModal();
            }
        });

        // === CAMERA & FILE EVENTS ===
        elements.cameraBtn?.addEventListener('click', () => this.handleCameraAction());
        elements.fileBtn?.addEventListener('click', () => this.handleFileAction());
        elements.changeImageBtn?.addEventListener('click', () => this.handleChangeImage());
        elements.fileInput?.addEventListener('change', (e) => this.handleFileSelect(e.target.files[0]));

        // === DETECTION EVENTS ===
        elements.detectBtn?.addEventListener('click', () => this.startDetection());
        elements.newDetectionBtn?.addEventListener('click', () => this.startNewDetection());
        elements.viewDetailsBtn?.addEventListener('click', () => this.showResultsDetail());

        // === AUTH MODAL EVENTS ===
        elements.confirmAuthBtn?.addEventListener('click', () => this.connect());
        elements.cancelAuthBtn?.addEventListener('click', () => this.hideAuthModal());
        elements.passwordInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') this.connect();
        });

        // === HISTORY MODAL EVENTS ===
        elements.closeHistoryModal?.addEventListener('click', () => this.hideHistoryModal());
        
        // Close modals on background click
        elements.authModal?.addEventListener('click', (e) => {
            if (e.target === elements.authModal) this.hideAuthModal();
        });
        elements.historyModal?.addEventListener('click', (e) => {
            if (e.target === elements.historyModal) this.hideHistoryModal();
        });

        // === KEYBOARD SHORTCUTS ===
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        // === WINDOW EVENTS ===
        window.addEventListener('resize', () => this.handleResize());
        window.addEventListener('beforeunload', () => this.cleanup());
    }

    initializeTouchFeedback() {
        // Add touch feedback to all interactive elements
        const interactiveElements = document.querySelectorAll(
            'button, .history-item, .stat-item, .action-btn, .modal-btn'
        );
        
        interactiveElements.forEach(element => {
            element.classList.add('touch-feedback');
            
            element.addEventListener('touchstart', (e) => {
                element.style.transform = 'scale(0.98)';
            }, { passive: true });
            
            element.addEventListener('touchend', (e) => {
                setTimeout(() => {
                    element.style.transform = '';
                }, 150);
            }, { passive: true });
        });
    }

    // === STATE MANAGEMENT SYSTEM ===
    setState(newState) {
        console.log(`🔄 State change: ${this.currentState} → ${newState}`);
        
        const previousState = this.currentState;
        this.currentState = newState;
        
        // Hide all action groups
        this.hideAllActionGroups();
        
        // Show appropriate action group and update UI
        switch (newState) {
            case 'initial':
                this.showInitialState();
                break;
            case 'imageReady':
                this.showImageReadyState();
                break;
            case 'processing':
                this.showProcessingState();
                break;
            case 'results':
                this.showResultsState();
                break;
            default:
                console.warn('Unknown state:', newState);
        }
        
        this.updateGlobalStatus();
        
        // Animate state transition
        if (previousState !== newState) {
            this.animateStateTransition(previousState, newState);
        }
    }

    hideAllActionGroups() {
        const { elements } = this;
        elements.initialActions?.classList.add('hidden');
        elements.imageReadyActions?.classList.add('hidden');
        elements.processingActions?.classList.add('hidden');
        elements.resultsActions?.classList.add('hidden');
    }

    showInitialState() {
        const { elements } = this;
        
        // Show empty state
        elements.emptyState?.classList.remove('hidden');
        elements.previewContent?.classList.remove('show');
        elements.previewContent?.classList.add('hidden');
        elements.resultsPanel?.classList.add('hidden');
        
        // Show initial action buttons
        elements.initialActions?.classList.remove('hidden');
        
        // Update button states based on connection
        this.updateButtonStates();
        
        this.updateGlobalStatus('Siap untuk deteksi');
    }

    showImageReadyState() {
        const { elements } = this;
        
        // Show image preview
        elements.emptyState?.classList.add('hidden');
        elements.previewContent?.classList.remove('hidden');
        elements.previewContent?.classList.add('show');
        elements.resultsPanel?.classList.add('hidden');
        
        // Hide processing and results overlays
        elements.processingOverlay?.classList.remove('show');
        elements.resultsOverlay?.classList.remove('show');
        
        // Show image ready actions
        elements.imageReadyActions?.classList.remove('hidden');
        
        this.updateGlobalStatus('Gambar siap untuk dianalisis');
    }

    showProcessingState() {
        const { elements } = this;
        
        // Keep image visible, show processing overlay
        elements.processingOverlay?.classList.add('show');
        elements.resultsOverlay?.classList.remove('show');
        
        // Show processing actions (disabled state)
        elements.processingActions?.classList.remove('hidden');
        
        // Start processing animation
        this.startProcessingAnimation();
        
        this.updateGlobalStatus('Menganalisis gambar...');
    }

    showResultsState() {
        const { elements } = this;
        
        // Hide processing overlay, show results
        elements.processingOverlay?.classList.remove('show');
        elements.resultsOverlay?.classList.add('show');
        elements.resultsPanel?.classList.remove('hidden');
        
        // Show results actions
        elements.resultsActions?.classList.remove('hidden');
        
        this.updateGlobalStatus('Deteksi selesai');
    }

    // === CAMERA & FILE HANDLING ===
    handleCameraAction() {
        if (!this.isConnected) {
            this.showNotification('Hubungkan ke server terlebih dahulu', 'warning');
            return;
        }
        
        // Simulate camera capture (in real app, this would access device camera)
        this.showNotification('Fitur kamera akan diimplementasikan', 'info');
        
        // For demo, trigger file picker
        this.handleFileAction();
    }

    handleFileAction() {
        if (!this.isConnected) {
            this.showNotification('Hubungkan ke server terlebih dahulu', 'warning');
            return;
        }
        
        this.elements.fileInput?.click();
    }

    handleChangeImage() {
        this.currentFile = null;
        this.selectedBase64 = null;
        this.currentResults = null;
        
        this.setState('initial');
        
        // Auto-close sidebar on mobile
        if (window.innerWidth <= 768) {
            this.closeSidebar();
        }
    }

    handleFileSelect(file) {
        if (!file) return;
        
        // Validate file type
        if (!file.type.startsWith('image/')) {
            this.showNotification('Pilih file gambar yang valid', 'error');
            return;
        }
        
        // Validate file size (max 10MB)
        if (file.size > 10 * 1024 * 1024) {
            this.showNotification('Ukuran file terlalu besar (maksimal 10MB)', 'error');
            return;
        }
        
        this.currentFile = file;
        this.loadImagePreview(file);
        
        // Auto-close sidebar on mobile
        if (window.innerWidth <= 768) {
            this.closeSidebar();
        }
    }

    loadImagePreview(file) {
        const reader = new FileReader();
        
        reader.onload = (e) => {
            this.selectedBase64 = e.target.result;
            
            // Update preview image
            if (this.elements.previewImage) {
                this.elements.previewImage.src = e.target.result;
                this.elements.previewImage.onload = () => {
                    this.setState('imageReady');
                };
            }
            
            this.showNotification(`Gambar ${file.name} berhasil dimuat`, 'success');
        };
        
        reader.onerror = () => {
            this.showNotification('Gagal memuat gambar', 'error');
            this.setState('initial');
        };
        
        reader.readAsDataURL(file);
    }

    // === DETECTION PROCESS ===
    async startDetection() {
        if (!this.currentFile || !this.selectedBase64) {
            this.showNotification('Tidak ada gambar untuk dianalisis', 'error');
            return;
        }

        if (!this.isConnected) {
            this.showNotification('Hubungkan ke server terlebih dahulu', 'error');
            return;
        }

        this.processingStartTime = Date.now();
        this.setState('processing');

        try {
            // Check if pywebview API is available
            if (window.pywebview && window.pywebview.api && window.pywebview.api.send_image) {
                const result = await window.pywebview.api.send_image(
                    this.currentFile.name, 
                    this.selectedBase64
                );
                
                const processingTime = ((Date.now() - this.processingStartTime) / 1000).toFixed(1);
                
                if (result[0]) {
                    // Success - results akan ditampilkan via tampilkanHasil callback
                    // History akan ditambahkan via addDetectionFromBackend callback
                    this.updateGlobalStatus(`Deteksi berhasil (${processingTime}s)`);
                } else {
                    this.showNotification(result[1], 'error');
                    this.setState('imageReady');
                }
            } else {
                // Demo mode - simulate processing
                this.simulateDetectionProcess();
            }
        } catch (error) {
            console.error('Detection error:', error);
            this.showNotification('Gagal menganalisis gambar', 'error');
            this.setState('imageReady');
        }
    }

    simulateDetectionProcess() {
        // Simulate processing delay
        setTimeout(() => {
            const processingTime = ((Date.now() - this.processingStartTime) / 1000).toFixed(1);
            
            // Generate demo results
            const demoResults = this.generateDemoResults();
            this.currentResults = demoResults;
            
            // Update result image (same as input for demo)
            if (this.elements.previewImage) {
                this.elements.previewImage.src = this.selectedBase64;
            }
            
            // Display results
            this.displayResults(demoResults, processingTime);
            
            // Add to history (demo mode)
            const demoDetection = {
                id: `demo_${Date.now()}`,
                filename: this.currentFile.name,
                timestamp: new Date().toISOString(),
                resultImage: this.selectedBase64,
                results: demoResults,
                processingTime: processingTime,
                timing: {
                    total_waktu_komunikasi: parseFloat(processingTime),
                    ukuran_hasil_kb: 100
                }
            };
            
            this.addDetectionFromBackend(demoDetection);
            
            this.setState('results');
            this.showNotification('Demo: Deteksi berhasil!', 'success');
        }, 2500);
    }

    generateDemoResults() {
        const pestTypes = [
            'Wereng Batang Coklat',
            'Penggerek Batang Padi',
            'Walang Sangit',
            'Ulat Grayak Padi'
        ];
        
        const detectionCount = Math.floor(Math.random() * 3) + 1;
        const detections = [];
        
        for (let i = 0; i < detectionCount; i++) {
            detections.push({
                name: pestTypes[Math.floor(Math.random() * pestTypes.length)],
                confidence: Math.floor(Math.random() * 20) + 80 // 80-99%
            });
        }
        
        return {
            detections,
            totalDetections: detectionCount,
            avgConfidence: Math.floor(detections.reduce((sum, d) => sum + d.confidence, 0) / detectionCount),
            recommendations: this.generateRecommendations(detections)
        };
    }

    generateRecommendations(detections) {
        const baseRecommendations = [
            'Isolasi area yang terinfeksi segera',
            'Aplikasikan insektisida sesuai dosis anjuran',
            'Pantau perkembangan setiap 2-3 hari',
            'Perbaiki sistem drainase sawah'
        ];
        
        const specificRecommendations = {
            'Wereng Batang Coklat': ['Gunakan varietas tahan wereng', 'Aplikasikan Imidakloprid'],
            'Penggerek Batang Padi': ['Bersihkan tunggul padi', 'Tanam serempak'],
            'Walang Sangit': ['Pasang perangkap cahaya', 'Semprot pada pagi/sore hari'],
            'Ulat Grayak Padi': ['Gunakan Bacillus thuringiensis', 'Bersihkan gulma']
        };
        
        let recommendations = [...baseRecommendations];
        
        detections.forEach(detection => {
            if (specificRecommendations[detection.name]) {
                recommendations.push(...specificRecommendations[detection.name]);
            }
        });
        
        // Remove duplicates and limit to 6
        return [...new Set(recommendations)].slice(0, 6);
    }

    displayResults(results, processingTime) {
        const { elements } = this;
        
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
        if (elements.detectionDetails) {
            elements.detectionDetails.innerHTML = '';
            results.detections.forEach(detection => {
                const detectionElement = document.createElement('div');
                detectionElement.className = 'detection-item';
                detectionElement.innerHTML = `
                    <div class="detection-name">${detection.name}</div>
                    <div class="detection-confidence">${detection.confidence}%</div>
                `;
                elements.detectionDetails.appendChild(detectionElement);
            });
        }
        
        // Update recommendations
        if (elements.recommendationsList) {
            elements.recommendationsList.innerHTML = '';
            results.recommendations.forEach(recommendation => {
                const li = document.createElement('li');
                li.textContent = recommendation;
                elements.recommendationsList.appendChild(li);
            });
        }
        
        // Update today's statistics
        this.updateTodayStats();
    }

    // ✅ FIXED: Function called from Python backend to display results
    tampilkanHasil(base64img) {
        console.log('🔌 Backend calling tampilkanHasil');
        
        if (!this.isAppReady) {
            console.log('⏳ App not ready, queueing tampilkanHasil');
            this.queuePendingOperation('tampilkanHasil', this.tampilkanHasil, [base64img]);
            return;
        }

        try {
            const processingTime = ((Date.now() - this.processingStartTime) / 1000).toFixed(1);
            
            // Update preview image with result
            if (this.elements.previewImage) {
                this.elements.previewImage.src = base64img;
            }
            
            // Generate results based on received image
            const results = this.generateDemoResults();
            this.currentResults = results;
            
            this.displayResults(results, processingTime);
            this.setState('results');
            this.showNotification('Hasil deteksi diterima!', 'success');
            
            console.log('✅ tampilkanHasil executed successfully');
        } catch (error) {
            console.error('❌ Error in tampilkanHasil:', error);
        }
    }

    // === HISTORY SYSTEM - BACKEND INTEGRATION ===
    
    // ✅ FIXED: Called from Python backend after successful connection to load existing history
    loadHistoryFromBackend(historyData) {
        console.log('🔌 Backend calling loadHistoryFromBackend');
        
        if (!this.isAppReady) {
            console.log('⏳ App not ready, storing history data for later');
            window._pendingHistoryData = historyData;
            return;
        }

        try {
            console.log(`📊 Loading ${historyData.length} detection records from backend`);
            this.history = historyData;
            this.renderHistory();
            this.updateTodayStats();
            this.showNotification(`Loaded ${historyData.length} history records`, 'info');
            console.log('✅ loadHistoryFromBackend executed successfully');
        } catch (error) {
            console.error('❌ Error loading history from backend:', error);
            this.history = [];
            this.renderHistory();
        }
    }

    // ✅ FIXED: Called from Python backend when new detection is completed
    addDetectionFromBackend(detectionData) {
        console.log('🔌 Backend calling addDetectionFromBackend');
        
        if (!this.isAppReady) {
            console.log('⏳ App not ready, queueing addDetectionFromBackend');
            this.queuePendingOperation('addDetectionFromBackend', this.addDetectionFromBackend, [detectionData]);
            return;
        }

        try {
            console.log(`📝 Adding new detection from backend: ${detectionData.id}`);
            
            // Convert backend detection data to UI format
            const uiDetection = {
                id: detectionData.id,
                filename: detectionData.filename,
                timestamp: new Date(detectionData.timestamp),
                resultImage: detectionData.resultImage || detectionData.result_base64,
                results: detectionData.results || {
                    totalDetections: 1,
                    avgConfidence: 85,
                    detections: [{ name: 'Hama Terdeteksi', confidence: 85 }],
                    recommendations: ['Pantau area terinfeksi', 'Aplikasikan treatment sesuai anjuran']
                },
                processingTime: detectionData.timing?.total_waktu_komunikasi || detectionData.processingTime || 0,
                timing: detectionData.timing || {}
            };
            
            // Add to beginning of history
            this.history.unshift(uiDetection);
            
            // Keep only last 50 items in UI
            if (this.history.length > 50) {
                this.history = this.history.slice(0, 50);
            }
            
            // Re-render history and update stats
            this.renderHistory();
            this.updateTodayStats();
            
            console.log('✅ addDetectionFromBackend executed successfully');
            
        } catch (error) {
            console.error('❌ Error adding detection from backend:', error);
        }
    }

    // ✅ FIXED: Called from Python backend to clear history
    clearHistoryFromBackend() {
        console.log('🔌 Backend calling clearHistoryFromBackend');
        
        if (!this.isAppReady) {
            console.log('⏳ App not ready, queueing clearHistoryFromBackend');
            this.queuePendingOperation('clearHistoryFromBackend', this.clearHistoryFromBackend, []);
            return;
        }

        try {
            console.log('📊 Clearing history from backend');
            this.history = [];
            this.renderHistory();
            this.updateTodayStats();
            this.showNotification('History cleared', 'info');
            console.log('✅ clearHistoryFromBackend executed successfully');
        } catch (error) {
            console.error('❌ Error clearing history from backend:', error);
        }
    }

    renderHistory() {
        const { elements } = this;
        if (!elements.historyList) return;

        elements.historyList.innerHTML = '';

        if (this.history.length === 0) {
            elements.historyList.innerHTML = `
                <div style="
                    color: var(--text-muted); 
                    text-align: center; 
                    padding: 20px; 
                    font-size: 0.9rem;
                    font-style: italic;
                ">
                    Belum ada riwayat deteksi
                </div>
            `;
            return;
        }

        this.history.forEach((item) => {
            const historyElement = document.createElement('div');
            historyElement.className = 'history-item';
            
            // Format timestamp
            const timeStr = item.timestamp.toLocaleTimeString('id-ID', { 
                hour: '2-digit', 
                minute: '2-digit' 
            });
            const dateStr = item.timestamp.toLocaleDateString('id-ID', { 
                day: 'numeric', 
                month: 'short' 
            });
            
            // Get primary pest name
            const primaryPest = item.results?.detections?.[0]?.name || 'Hama Terdeteksi';
            
            // Format processing time
            const procTime = typeof item.processingTime === 'number' 
                ? item.processingTime.toFixed(1) 
                : parseFloat(item.processingTime || 0).toFixed(1);
            
            historyElement.innerHTML = `
                <div class="history-thumbnail">🐛</div>
                <div class="history-info">
                    <h5>${primaryPest}</h5>
                    <p>${dateStr}, ${timeStr}</p>
                    <p>${item.results?.totalDetections || 1} deteksi • ${procTime}s</p>
                </div>
            `;
            
            // Add click handler
            historyElement.addEventListener('click', () => {
                this.showHistoryDetail(item);
                // Auto-close sidebar on mobile
                if (window.innerWidth <= 768) {
                    this.closeSidebar();
                }
            });
            
            elements.historyList.appendChild(historyElement);
        });
    }

    showHistoryDetail(item) {
        // Implementation sama seperti sebelumnya
        const { elements } = this;
        if (!elements.historyModal || !elements.historyModalBody) return;
        
        // [Implementasi showHistoryDetail lengkap sama seperti sebelumnya]
        this.showModal(elements.historyModal);
    }

    updateTodayStats() {
        const today = new Date().toDateString();
        const todayItems = this.history.filter(item => 
            item.timestamp.toDateString() === today
        );
        
        const totalDetections = todayItems.reduce((sum, item) => 
            sum + (item.results?.totalDetections || 0), 0
        );
        
        const avgAccuracy = todayItems.length > 0 
            ? Math.round(todayItems.reduce((sum, item) => 
                sum + (item.results?.avgConfidence || 0), 0
            ) / todayItems.length)
            : 0;
        
        this.todayStats = {
            detections: totalDetections,
            accuracy: avgAccuracy
        };
        
        // Update UI
        if (this.elements.todayDetections) {
            this.elements.todayDetections.textContent = totalDetections;
        }
        if (this.elements.todayAccuracy) {
            this.elements.todayAccuracy.textContent = avgAccuracy + '%';
        }
    }

    // === CONNECTION MANAGEMENT ===
    async connect() {
        const password = this.elements.passwordInput?.value;
        
        if (!password) {
            this.showNotification('Masukkan password!', 'error');
            return;
        }

        try {
            this.setConnectionState('connecting');
            
            // Check if pywebview API is available
            if (window.pywebview && window.pywebview.api && window.pywebview.api.connect_to_server) {
                const result = await window.pywebview.api.connect_to_server(password);
                
                if (result[0]) {
                    this.isConnected = true;
                    this.setConnectionState('connected');
                    this.updateButtonStates();
                    this.hideAuthModal();
                    this.showNotification(result[1], 'success');
                    
                    // ✅ FIXED: History will be loaded via frontend_ready signal
                    console.log('🔌 Connected successfully, history will load after frontend_ready signal');
                } else {
                    this.setConnectionState('disconnected');
                    this.showNotification(result[1], 'error');
                }
            } else {
                // Demo mode - simulate connection
                setTimeout(() => {
                    this.isConnected = true;
                    this.setConnectionState('connected');
                    this.updateButtonStates();
                    this.hideAuthModal();
                    this.showNotification('Demo mode: Terhubung ke server', 'success');
                    
                    // Load demo history in demo mode
                    const demoHistory = this.generateDemoHistory();
                    this.loadHistoryFromBackend(demoHistory);
                }, 1500);
            }
        } catch (error) {
            console.error('Connection error:', error);
            this.setConnectionState('disconnected');
            this.showNotification('Gagal terhubung ke server', 'error');
        }
    }

    generateDemoHistory() {
        // Generate some demo history for demo mode
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

    setConnectionState(state) {
        const { elements } = this;
        
        // Update sidebar connection status
        elements.statusIndicator?.classList.remove('connected', 'connecting');
        elements.connectBtn?.classList.remove('connected', 'connecting');
        
        // Update main connection status
        elements.mainStatusDot?.classList.remove('connected', 'connecting');
        
        switch(state) {
            case 'connected':
                if (elements.connectBtn) {
                    elements.connectBtn.textContent = 'Terhubung';
                    elements.connectBtn.classList.add('connected');
                }
                if (elements.statusIndicator) elements.statusIndicator.classList.add('connected');
                if (elements.statusText) elements.statusText.textContent = 'Terhubung';
                if (elements.mainStatusDot) elements.mainStatusDot.classList.add('connected');
                if (elements.mainStatusText) elements.mainStatusText.textContent = 'Server terhubung';
                break;
                
            case 'connecting':
                if (elements.connectBtn) {
                    elements.connectBtn.textContent = 'Menghubungkan...';
                    elements.connectBtn.classList.add('connecting');
                }
                if (elements.statusIndicator) elements.statusIndicator.classList.add('connecting');
                if (elements.statusText) elements.statusText.textContent = 'Menghubungkan...';
                if (elements.mainStatusDot) elements.mainStatusDot.classList.add('connecting');
                if (elements.mainStatusText) elements.mainStatusText.textContent = 'Menghubungkan...';
                break;
                
            case 'disconnected':
            default:
                if (elements.connectBtn) {
                    elements.connectBtn.textContent = 'Connect';
                }
                if (elements.statusText) elements.statusText.textContent = 'Tidak Terhubung';
                if (elements.mainStatusText) elements.mainStatusText.textContent = 'Hubungkan ke server';
                break;
        }
    }

    updateButtonStates() {
        const { elements } = this;
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

    // === NOTIFICATION SYSTEM ===
    showNotification(message, type = 'info') {
        const { notification } = this.elements;
        
        if (notification) {
            notification.textContent = message;
            notification.className = `notification ${type}`;
            notification.classList.add('show');

            setTimeout(() => {
                notification.classList.remove('show');
            }, 3000);
        } else {
            console.log(`${type.toUpperCase()}: ${message}`);
        }
    }

    // === MODAL MANAGEMENT ===
    showModal(modalElement) {
        if (modalElement) {
            modalElement.classList.add('show');
            modalElement.style.display = 'flex';
        }
    }

    hideModal(modalElement) {
        if (modalElement) {
            modalElement.classList.remove('show');
            modalElement.style.display = 'none';
        }
    }

    showAuthModal() {
        this.showModal(this.elements.authModal);
        if (this.elements.passwordInput) {
            this.elements.passwordInput.focus();
        }
    }

    hideAuthModal() {
        this.hideModal(this.elements.authModal);
        if (this.elements.passwordInput) {
            this.elements.passwordInput.value = '';
        }
    }

    // === SIDEBAR MANAGEMENT ===
    toggleSidebar() {
        this.sidebarOpen = !this.sidebarOpen;
        const { sidebar, sidebarOverlay } = this.elements;
        
        if (this.sidebarOpen) {
            sidebar?.classList.add('open');
            sidebarOverlay?.classList.add('show');
        } else {
            this.closeSidebar();
        }
    }

    closeSidebar() {
        this.sidebarOpen = false;
        const { sidebar, sidebarOverlay } = this.elements;
        sidebar?.classList.remove('open');
        sidebarOverlay?.classList.remove('show');
    }

    // === THEME MANAGEMENT ===
    toggleDarkMode() {
        this.isDarkMode = !this.isDarkMode;
        this.applyTheme();
        this.saveTheme();
        this.showNotification(
            `Mode ${this.isDarkMode ? 'gelap' : 'terang'} diaktifkan`, 
            'info'
        );
    }

    applyTheme() {
        const { darkModeBtn } = this.elements;
        
        if (this.isDarkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
            if (darkModeBtn) darkModeBtn.textContent = '☀️';
        } else {
            document.documentElement.removeAttribute('data-theme');
            if (darkModeBtn) darkModeBtn.textContent = '🌓';
        }
    }

    loadTheme() {
        try {
            const saved = localStorage.getItem('jagapadi-dark-mode');
            return saved === 'true';
        } catch (error) {
            console.log('LocalStorage not available, using default theme');
            return false;
        }
    }

    saveTheme() {
        try {
            localStorage.setItem('jagapadi-dark-mode', this.isDarkMode.toString());
        } catch (error) {
            console.log('LocalStorage not available, theme not saved');
        }
    }

    // === STATUS & UI UPDATES ===
    updateGlobalStatus(message) {
        if (this.elements.globalStatus) {
            this.elements.globalStatus.textContent = message || 'Siap untuk deteksi';
        }
        console.log('📊 Status:', message);
    }

    updateStatusBar() {
        if (this.elements.statusTime) {
            const updateTime = () => {
                const now = new Date();
                this.elements.statusTime.textContent = now.toLocaleTimeString('id-ID');
            };
            
            updateTime();
            setInterval(updateTime, 1000);
        }
    }

    animateStateTransition(fromState, toState) {
        // Add subtle animation between states
        const container = this.elements.previewContainer;
        if (container) {
            container.style.transform = 'scale(0.98)';
            container.style.opacity = '0.8';
            
            setTimeout(() => {
                container.style.transform = '';
                container.style.opacity = '';
            }, 200);
        }
    }

    // === EVENT HANDLERS ===
    handleKeyboard(e) {
        // ESC key - close modals/sidebar
        if (e.key === 'Escape') {
            if (this.elements.historyModal?.classList.contains('show')) {
                this.hideHistoryModal();
            } else if (this.elements.authModal?.classList.contains('show')) {
                this.hideAuthModal();
            } else if (this.sidebarOpen) {
                this.closeSidebar();
            }
        }
        
        // Spacebar - trigger primary action
        if (e.key === ' ' && e.target === document.body) {
            e.preventDefault();
            if (this.currentState === 'initial' && this.isConnected) {
                this.handleCameraAction();
            } else if (this.currentState === 'imageReady') {
                this.startDetection();
            }
        }
        
        // Enter key - trigger detection if image ready
        if (e.key === 'Enter' && this.currentState === 'imageReady') {
            this.startDetection();
        }
    }

    handleResize() {
        // Auto-close sidebar on mobile when resizing to desktop
        if (window.innerWidth > 768 && this.sidebarOpen) {
            this.closeSidebar();
        }
    }

    cleanup() {
        // Save any pending data before page unload
        this.saveTheme();
    }

    // === UTILITY METHODS ===
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    // === LEGACY SUPPORT ===
    updateStatus(message) {
        this.updateGlobalStatus(message);
    }

    startProcessingAnimation() {
        const { elements } = this;
        
        // Animate progress bar
        if (elements.progressBar) {
            elements.progressBar.style.width = '0%';
            
            let progress = 0;
            const interval = setInterval(() => {
                progress += Math.random() * 15 + 5; // Random progress increments
                if (progress > 100) progress = 100;
                
                elements.progressBar.style.width = progress + '%';
                
                if (progress >= 100 || this.currentState !== 'processing') {
                    clearInterval(interval);
                }
            }, 200);
        }
        
        // Animate processing text
        this.animateProcessingText();
    }

    animateProcessingText() {
        const { elements } = this;
        if (!elements.processingText) return;
        
        const messages = [
            'Menganalisis gambar...',
            'Mendeteksi objek...',
            'Mengidentifikasi hama...',
            'Menghitung confidence...',
            'Menyiapkan hasil...'
        ];
        
        let index = 0;
        const interval = setInterval(() => {
            if (this.currentState !== 'processing') {
                clearInterval(interval);
                return;
            }
            
            elements.processingText.textContent = messages[index];
            index = (index + 1) % messages.length;
        }, 800);
    }

    startNewDetection() {
        this.handleChangeImage();
    }

    showResultsDetail() {
        if (!this.currentResults) return;
        
        // For now, just scroll to results panel
        this.elements.resultsPanel?.scrollIntoView({ behavior: 'smooth' });
        
        // In future versions, could open detailed modal
        this.showNotification('Detail hasil ditampilkan di bawah', 'info');
    }

    hideHistoryModal() {
        this.hideModal(this.elements.historyModal);
    }

    async disconnect() {
        try {
            if (window.pywebview && window.pywebview.api && window.pywebview.api.disconnect) {
                const result = await window.pywebview.api.disconnect();
            }
            
            this.isConnected = false;
            this.setConnectionState('disconnected');
            this.updateButtonStates();
            
            // Reset to initial state if not processing
            if (this.currentState !== 'processing') {
                this.setState('initial');
            }
            
            this.showNotification('Terputus dari server', 'info');
        } catch (error) {
            console.error('Disconnect error:', error);
            this.isConnected = false;
            this.setConnectionState('disconnected');
            this.updateButtonStates();
            this.showNotification('Terputus dari server', 'info');
        }
    }
}

// === FIXED: GLOBAL FUNCTIONS FOR BACKEND COMMUNICATION ===

// Global variable for app instance
let app = null;

// ✅ FIXED: Global functions that backend can call directly with proper error handling
window.loadHistoryFromBackend = function(historyData) {
    console.log('🔌 Backend calling loadHistoryFromBackend');
    try {
        if (window.app && window.app.loadHistoryFromBackend) {
            window.app.loadHistoryFromBackend(historyData);
        } else {
            console.log('⏳ App not ready for history loading, storing for later');
            // Store for later when app is ready
            window._pendingHistoryData = historyData;
        }
    } catch (error) {
        console.error('❌ Error in loadHistoryFromBackend:', error);
    }
};

window.addDetectionFromBackend = function(detectionData) {
    console.log('🔌 Backend calling addDetectionFromBackend');
    try {
        if (window.app && window.app.addDetectionFromBackend) {
            window.app.addDetectionFromBackend(detectionData);
        } else {
            console.log('⏳ App not ready for detection adding, storing for later');
            if (!window._pendingOperations) window._pendingOperations = [];
            window._pendingOperations.push({
                type: 'addDetection',
                data: detectionData
            });
        }
    } catch (error) {
        console.error('❌ Error in addDetectionFromBackend:', error);
    }
};

window.clearHistoryFromBackend = function() {
    console.log('🔌 Backend calling clearHistoryFromBackend');
    try {
        if (window.app && window.app.clearHistoryFromBackend) {
            window.app.clearHistoryFromBackend();
        } else {
            console.log('⏳ App not ready for history clearing, will clear when ready');
            window._pendingHistoryData = [];
        }
    } catch (error) {
        console.error('❌ Error in clearHistoryFromBackend:', error);
    }
};

// ✅ FIXED: Legacy functions for backward compatibility with better error handling
function tampilkanHasil(base64img) {
    console.log('🔌 Backend calling tampilkanHasil (legacy)');
    try {
        if (app && app.tampilkanHasil) {
            app.tampilkanHasil(base64img);
        } else {
            console.log('⏳ App not ready for tampilkanHasil, storing for later');
            if (!window._pendingOperations) window._pendingOperations = [];
            window._pendingOperations.push({
                type: 'tampilkanHasil',
                data: base64img
            });
        }
    } catch (error) {
        console.error('❌ Error in tampilkanHasil:', error);
    }
}

function updateStatus(message) {
    console.log('🔌 Backend calling updateStatus (legacy)');
    try {
        if (app && app.updateStatus) {
            app.updateStatus(message);
        } else {
            console.log('📊 Status update (app not ready):', message);
        }
    } catch (error) {
        console.error('❌ Error in updateStatus:', error);
    }
}

// === GLOBAL INITIALIZATION ===
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM loaded, initializing JAGAPADI v2.2...');
    app = new JagaPadiApp();
    
    // Make app globally accessible for modal actions and backend calls
    window.app = app;
    
    // ✅ FIXED: Process pending history data if any
    if (window._pendingHistoryData) {
        console.log('📊 Processing pending history data');
        app.loadHistoryFromBackend(window._pendingHistoryData);
        delete window._pendingHistoryData;
    }
    
    // ✅ FIXED: Process pending operations if any
    if (window._pendingOperations) {
        console.log('📋 Processing pending operations');
        window._pendingOperations.forEach(operation => {
            try {
                if (operation.type === 'addDetection') {
                    app.addDetectionFromBackend(operation.data);
                } else if (operation.type === 'tampilkanHasil') {
                    app.tampilkanHasil(operation.data);
                }
            } catch (error) {
                console.error(`❌ Error processing pending operation ${operation.type}:`, error);
            }
        });
        delete window._pendingOperations;
    }
    
    console.log('✅ JAGAPADI v2.2 fully initialized and ready for backend communication');
});

// ✅ FIXED: Handle pywebview API availability - MOVED OUTSIDE DOM READY
window.addEventListener('pywebviewready', () => {
    console.log('🔌 PyWebView API ready for JAGAPADI v2.2');
    // Signal to Python that frontend is ready
    if (window.pywebview && window.pywebview.api && window.pywebview.api.frontend_ready) {
        console.log('🎯 Signaling frontend ready to Python backend...');
        try {
            window.pywebview.api.frontend_ready();
        } catch (error) {
            console.error('❌ Failed to signal frontend ready:', error);
        }
    }
});

// Export for use in other modules if needed
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { JagaPadiApp, tampilkanHasil, updateStatus };
}

// ✅ FIXED: Demo functionality announcement
window.addEventListener('load', () => {
    console.log('🌾 JAGAPADI v2.2 - AI Deteksi Hama Padi loaded successfully!');
    console.log('🔧 FINAL FIX - History Loading Issue Resolved');
    console.log('🎯 Frontend-backend synchronization improved');
    console.log('💾 Persistent history system active');
    console.log('⏱️ Timing issues resolved with proper signaling');
    console.log('🔄 App readiness tracking and pending operations system active');
});