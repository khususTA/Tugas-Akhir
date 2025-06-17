/**
 * JAGAPADI v2.2 - History Manager Module (Local-First)
 * Mengelola riwayat deteksi dengan pendekatan local-first:
 * - Auto-load history lokal saat startup
 * - Sync dengan server saat connect
 * - Offline-capable history viewing
 * - Persistent local storage
 */

class HistoryManager {
    constructor(app) {
        this.app = app; // Reference ke aplikasi utama
        this.history = [];
        this.todayStats = { detections: 0, accuracy: 0 };
        this.isHistoryLoaded = false;
        this.pendingServerSync = false;
        
        // Local storage key untuk backup
        this.localStorageKey = 'jagapadi_history_cache';
        
        console.log('📋 History Manager initialized (Local-First)');
        
        // Auto-load history saat inisialisasi
        this.initializeHistory();
    }

    /**
     * Inisialisasi history - load data lokal terlebih dahulu
     */
    async initializeHistory() {
        console.log('🔄 Initializing history system...');
        
        try {
            // 1. Coba load dari Python client history file
            await this.loadLocalHistoryFromPython();
            
            // 2. Fallback ke localStorage jika Python tidak tersedia
            if (!this.isHistoryLoaded) {
                this.loadHistoryFromLocalStorage();
            }
            
            // 3. Update UI dengan data yang ada
            this.renderHistory();
            this.updateTodayStats();
            
            console.log(`✅ History initialized: ${this.history.length} items loaded`);
            
        } catch (error) {
            console.error('❌ Error initializing history:', error);
            // Fallback ke localStorage
            this.loadHistoryFromLocalStorage();
        }
    }

    /**
     * Load history dari Python client (detections.json)
     */
    async loadLocalHistoryFromPython() {
        try {
            // Cek apakah PyWebView API tersedia
            if (window.pywebview && window.pywebview.api) {
                console.log('📂 Loading local history from Python client...');
                
                // Panggil method Python untuk load history lokal
                if (typeof window.pywebview.api.load_local_history === 'function') {
                    const localHistory = await window.pywebview.api.load_local_history();
                    
                    if (localHistory && Array.isArray(localHistory)) {
                        this.history = this.convertPythonHistoryToUI(localHistory);
                        this.isHistoryLoaded = true;
                        this.saveToLocalStorage(); // Backup ke localStorage
                        
                        console.log(`✅ Loaded ${this.history.length} items from Python client`);
                        return true;
                    }
                }
            }
            
            return false;
            
        } catch (error) {
            console.error('❌ Error loading from Python client:', error);
            return false;
        }
    }

    /**
     * Load history dari localStorage sebagai fallback
     */
    loadHistoryFromLocalStorage() {
        try {
            console.log('💾 Loading history from localStorage...');
            
            const stored = localStorage.getItem(this.localStorageKey);
            if (stored) {
                const parsedHistory = JSON.parse(stored);
                if (Array.isArray(parsedHistory)) {
                    this.history = parsedHistory.map(item => ({
                        ...item,
                        timestamp: new Date(item.timestamp) // Convert string back to Date
                    }));
                    this.isHistoryLoaded = true;
                    
                    console.log(`✅ Loaded ${this.history.length} items from localStorage`);
                    return;
                }
            }
            
            // Jika tidak ada data, buat demo history untuk first-time user
            this.createInitialDemoHistory();
            
        } catch (error) {
            console.error('❌ Error loading from localStorage:', error);
            this.createInitialDemoHistory();
        }
    }

    /**
     * Simpan history ke localStorage untuk backup
     */
    saveToLocalStorage() {
        try {
            const historyToStore = this.history.map(item => ({
                ...item,
                timestamp: item.timestamp.toISOString() // Convert Date to string
            }));
            
            localStorage.setItem(this.localStorageKey, JSON.stringify(historyToStore));
            console.log('💾 History saved to localStorage');
            
        } catch (error) {
            console.error('❌ Error saving to localStorage:', error);
        }
    }

    /**
     * Buat demo history untuk first-time user
     */
    createInitialDemoHistory() {
        console.log('🎭 Creating initial demo history...');
        
        const demoItems = [];
        const pestTypes = ['wereng', 'bercak coklat', 'penggerek batang', 'walang sangit'];
        
        // Buat 3 item demo dengan waktu yang berbeda
        for (let i = 0; i < 3; i++) {
            const timestamp = new Date();
            timestamp.setHours(timestamp.getHours() - (i + 1) * 2); // 2, 4, 6 jam lalu
            
            demoItems.push({
                id: `demo_${Date.now()}_${i}`,
                filename: `demo_image_${i + 1}.jpg`,
                timestamp: timestamp,
                resultImage: '/placeholder-image.jpg',
                results: {
                    totalDetections: Math.floor(Math.random() * 2) + 1,
                    avgConfidence: Math.floor(Math.random() * 15) + 85,
                    detections: [{
                        name: pestTypes[Math.floor(Math.random() * pestTypes.length)],
                        confidence: Math.floor(Math.random() * 15) + 85
                    }],
                    recommendations: [
                        'Aplikasikan treatment sesuai anjuran',
                        'Pantau perkembangan setiap 2-3 hari'
                    ]
                },
                processingTime: (Math.random() * 3 + 1).toFixed(1),
                timing: {
                    total_waktu_komunikasi: Math.random() * 3 + 1,
                    ukuran_hasil_kb: Math.random() * 100 + 50
                },
                source: 'demo'
            });
        }
        
        this.history = demoItems;
        this.isHistoryLoaded = true;
        this.saveToLocalStorage();
        
        console.log('✅ Demo history created');
    }

    /**
     * Convert data history dari Python ke format UI
     */
    convertPythonHistoryToUI(pythonHistory) {
        return pythonHistory.map(item => ({
            id: item.id || `python_${Date.now()}_${Math.random()}`,
            filename: item.filename || 'unknown.jpg',
            timestamp: new Date(item.timestamp || Date.now()),
            resultImage: item.result_base64 || item.resultImage || '/placeholder-image.jpg',
            results: item.results || {
                totalDetections: 1,
                avgConfidence: 85,
                detections: [{ name: 'Hama Terdeteksi', confidence: 85 }],
                recommendations: ['Pantau area terinfeksi']
            },
            processingTime: parseFloat(item.timing?.total_waktu_komunikasi || item.processingTime || 0),
            timing: item.timing || {},
            source: 'python_client'
        }));
    }

    /**
     * Load history dari backend server (saat connect)
     */
    loadHistoryFromBackend(serverHistory) {
        console.log('🔌 Loading history from backend server');
        
        if (!this.app.isAppReady) {
            console.log('⏳ App not ready, storing server history for later');
            window._pendingHistoryData = serverHistory;
            return;
        }

        try {
            console.log(`📊 Syncing with server: ${serverHistory.length} items`);
            
            // Convert server data ke format UI
            const serverItems = serverHistory.map(item => ({
                ...item,
                timestamp: new Date(item.timestamp),
                source: 'server'
            }));
            
            // Merge dengan history lokal
            this.mergeWithLocalHistory(serverItems);
            
            // Update UI
            this.renderHistory();
            this.updateTodayStats();
            
            // Backup ke localStorage
            this.saveToLocalStorage();
            
            this.app.showNotification(`Sinkronisasi selesai: ${this.history.length} riwayat`, 'info');
            
            console.log('✅ History synced with server successfully');
            
        } catch (error) {
            console.error('❌ Error loading history from backend:', error);
            this.app.showNotification('Gagal sinkronisasi riwayat', 'error');
        }
    }

    /**
     * Merge history server dengan history lokal
     */
    mergeWithLocalHistory(serverItems) {
        // Buat map dari item lokal berdasarkan ID
        const localMap = new Map();
        this.history.forEach(item => {
            if (item.source !== 'demo') { // Kecualikan demo items
                localMap.set(item.id, item);
            }
        });
        
        // Merge dengan server items
        const mergedItems = [];
        
        // Tambahkan semua item dari server
        serverItems.forEach(serverItem => {
            mergedItems.push(serverItem);
            localMap.delete(serverItem.id); // Remove dari local jika ada di server
        });
        
        // Tambahkan item lokal yang tidak ada di server (offline items)
        localMap.forEach(localItem => {
            mergedItems.push({
                ...localItem,
                source: 'local_only'
            });
        });
        
        // Urutkan berdasarkan timestamp (terbaru dulu)
        mergedItems.sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
        
        // Batasi jumlah item (max 100)
        this.history = mergedItems.slice(0, 100);
        
        console.log(`🔄 Merged history: ${this.history.length} total items`);
    }

    /**
     * Tambah deteksi baru dari backend
     */
    addDetectionFromBackend(detectionData) {
        console.log('🔌 Adding new detection from backend');
        
        if (!this.app.isAppReady) {
            console.log('⏳ App not ready, queueing detection');
            this.app.queuePendingOperation('addDetectionFromBackend', this.addDetectionFromBackend, [detectionData]);
            return;
        }

        try {
            // Convert ke format UI
            const uiDetection = {
                id: detectionData.id,
                filename: detectionData.filename,
                timestamp: new Date(detectionData.timestamp),
                resultImage: detectionData.resultImage || detectionData.result_base64,
                results: detectionData.results || {
                    totalDetections: 1,
                    avgConfidence: 85,
                    detections: [{ name: 'Hama Terdeteksi', confidence: 85 }],
                    recommendations: ['Pantau area terinfeksi']
                },
                processingTime: parseFloat(detectionData.timing?.total_waktu_komunikasi || detectionData.processingTime || 0),
                timing: detectionData.timing || {},
                source: 'server'
            };
            
            // Tambah ke beginning of array
            this.history.unshift(uiDetection);
            
            // Batasi jumlah items
            if (this.history.length > 100) {
                this.history = this.history.slice(0, 100);
            }
            
            // Update UI
            this.renderHistory();
            this.updateTodayStats();
            
            // Backup ke localStorage
            this.saveToLocalStorage();
            
            console.log('✅ Detection added to history successfully');
            
        } catch (error) {
            console.error('❌ Error adding detection to history:', error);
        }
    }

    /**
     * Render history di sidebar
     */
    renderHistory() {
        const { elements } = this.app;
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

        // Group by date untuk better organization
        const groupedHistory = this.groupHistoryByDate();
        
        Object.keys(groupedHistory).forEach(dateKey => {
            // Add date separator jika lebih dari 1 hari
            if (Object.keys(groupedHistory).length > 1) {
                const dateSeparator = document.createElement('div');
                dateSeparator.className = 'history-date-separator';
                dateSeparator.innerHTML = `<span>${dateKey}</span>`;
                elements.historyList.appendChild(dateSeparator);
            }
            
            // Add items for this date
            groupedHistory[dateKey].forEach((item) => {
                const historyElement = this.createHistoryItemElement(item);
                elements.historyList.appendChild(historyElement);
            });
        });

        console.log(`📋 Rendered ${this.history.length} history items`);
    }

    /**
     * Group history berdasarkan tanggal
     */
    groupHistoryByDate() {
        const groups = {};
        const today = new Date().toDateString();
        const yesterday = new Date(Date.now() - 86400000).toDateString();
        
        this.history.forEach(item => {
            const itemDateString = item.timestamp.toDateString();
            let dateKey;
            
            if (itemDateString === today) {
                dateKey = 'Hari Ini';
            } else if (itemDateString === yesterday) {
                dateKey = 'Kemarin';
            } else {
                dateKey = item.timestamp.toLocaleDateString('id-ID', { 
                    day: 'numeric', 
                    month: 'long' 
                });
            }
            
            if (!groups[dateKey]) {
                groups[dateKey] = [];
            }
            groups[dateKey].push(item);
        });
        
        return groups;
    }

    /**
     * Buat elemen UI untuk history item
     */
    createHistoryItemElement(item) {
        const historyElement = document.createElement('div');
        historyElement.className = 'history-item';
        
        // Add source indicator
        const sourceClass = item.source === 'demo' ? 'demo' : 
                           item.source === 'local_only' ? 'offline' : 'synced';
        historyElement.classList.add(`source-${sourceClass}`);
        
        // Format timestamp
        const timeStr = item.timestamp.toLocaleTimeString('id-ID', { 
            hour: '2-digit', 
            minute: '2-digit' 
        });
        
        // Get primary pest name
        const primaryPest = item.results?.detections?.[0]?.name || 'Hama Terdeteksi';
        
        // Format processing time
        const procTime = typeof item.processingTime === 'number' 
            ? item.processingTime.toFixed(1) 
            : parseFloat(item.processingTime || 0).toFixed(1);
        
        // Add source indicator icon
        const sourceIcon = item.source === 'demo' ? '🎭' :
                          item.source === 'local_only' ? '📱' : '🌐';
        
        historyElement.innerHTML = `
            <div class="history-thumbnail">
                <span class="source-icon">${sourceIcon}</span>
            </div>
            <div class="history-info">
                <h5>${primaryPest}</h5>
                <p>${timeStr} • ${item.results?.totalDetections || 1} deteksi</p>
                <p class="processing-time">${procTime}s</p>
            </div>
        `;
        
        // Add click handler
        historyElement.addEventListener('click', () => {
            this.showHistoryDetail(item);
            // Auto-close sidebar di mobile
            if (window.innerWidth <= 768) {
                this.app.uiManager?.closeSidebar();
            }
        });
        
        return historyElement;
    }

    /**
     * Tampilkan detail history dalam modal
     */
    showHistoryDetail(item) {
        const { elements } = this.app;
        if (!elements.historyModal || !elements.historyModalBody) return;
        
        // Format detail information
        const detailHTML = this.generateHistoryDetailHTML(item);
        elements.historyModalBody.innerHTML = detailHTML;
        
        // Show modal
        this.app.uiManager?.showModal(elements.historyModal);
        
        console.log(`📖 Showing detail for: ${item.filename}`);
    }

    /**
     * Generate HTML untuk detail history
     */
    generateHistoryDetailHTML(item) {
        const timeStr = item.timestamp.toLocaleString('id-ID');
        const sourceLabel = this.getSourceLabel(item.source);
        
        let detectionsHTML = '';
        if (item.results?.detections) {
            detectionsHTML = item.results.detections.map(detection => `
                <div class="detection-item">
                    <span class="detection-name">${detection.name}</span>
                    <span class="detection-confidence">${detection.confidence}%</span>
                </div>
            `).join('');
        }
        
        let recommendationsHTML = '';
        if (item.results?.recommendations) {
            recommendationsHTML = item.results.recommendations.map(rec => `
                <li>${rec}</li>
            `).join('');
        }
        
        return `
            <div class="history-detail">
                <div class="detail-header">
                    <img src="${item.resultImage}" alt="Hasil Deteksi" class="detail-image">
                    <div class="detail-info">
                        <h4>${item.filename}</h4>
                        <p class="detail-time">${timeStr}</p>
                        <p class="detail-source">${sourceLabel}</p>
                    </div>
                </div>
                
                <div class="detail-stats">
                    <div class="stat-item">
                        <div class="stat-number">${item.results?.totalDetections || 0}</div>
                        <div class="stat-label">Hama Terdeteksi</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${item.results?.avgConfidence || 0}%</div>
                        <div class="stat-label">Tingkat Keyakinan</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-number">${parseFloat(item.processingTime || 0).toFixed(1)}s</div>
                        <div class="stat-label">Waktu Proses</div>
                    </div>
                </div>
                
                ${detectionsHTML ? `
                    <div class="detail-detections">
                        <h5>🐛 Detail Deteksi</h5>
                        ${detectionsHTML}
                    </div>
                ` : ''}
                
                ${recommendationsHTML ? `
                    <div class="detail-recommendations">
                        <h5>💊 Rekomendasi</h5>
                        <ul>${recommendationsHTML}</ul>
                    </div>
                ` : ''}
                
                ${item.timing ? `
                    <div class="detail-timing">
                        <h5>⏱️ Detail Timing</h5>
                        <div class="timing-grid">
                            <div>Total Komunikasi: ${(item.timing.total_waktu_komunikasi || 0).toFixed(3)}s</div>
                            <div>Ukuran Hasil: ${(item.timing.ukuran_hasil_kb || 0).toFixed(1)} KB</div>
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }

    /**
     * Get label untuk source data
     */
    getSourceLabel(source) {
        switch (source) {
            case 'demo': return '🎭 Data Demo';
            case 'local_only': return '📱 Offline';
            case 'server': return '🌐 Server';
            case 'python_client': return '💻 Client';
            default: return '📊 Data';
        }
    }

    /**
     * Update statistik hari ini
     */
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
        
        // Update UI elements
        if (this.app.elements.todayDetections) {
            this.app.elements.todayDetections.textContent = totalDetections;
        }
        if (this.app.elements.todayAccuracy) {
            this.app.elements.todayAccuracy.textContent = avgAccuracy + '%';
        }
        
        console.log(`📊 Today stats updated: ${totalDetections} detections, ${avgAccuracy}% accuracy`);
    }

    /**
     * Get statistik hari ini
     */
    getTodayStats() {
        return this.todayStats;
    }

    /**
     * Search history berdasarkan query
     */
    searchHistory(query) {
        if (!query || query.trim() === '') {
            this.renderHistory(); // Show all
            return;
        }
        
        const filteredHistory = this.history.filter(item => {
            const searchText = `
                ${item.filename} 
                ${item.results?.detections?.map(d => d.name).join(' ') || ''}
            `.toLowerCase();
            
            return searchText.includes(query.toLowerCase());
        });
        
        // Render filtered results
        this.renderFilteredHistory(filteredHistory, `Hasil pencarian: "${query}"`);
    }

    /**
     * Filter history berdasarkan tanggal
     */
    filterByDate(date) {
        const targetDate = new Date(date).toDateString();
        const filteredHistory = this.history.filter(item => 
            item.timestamp.toDateString() === targetDate
        );
        
        const dateLabel = new Date(date).toLocaleDateString('id-ID');
        this.renderFilteredHistory(filteredHistory, `Riwayat ${dateLabel}`);
    }

    /**
     * Render hasil filter
     */
    renderFilteredHistory(filteredItems, title) {
        const { elements } = this.app;
        if (!elements.historyList) return;

        elements.historyList.innerHTML = '';
        
        // Add title
        const titleElement = document.createElement('div');
        titleElement.className = 'filter-title';
        titleElement.innerHTML = `<strong>${title}</strong> (${filteredItems.length} item)`;
        elements.historyList.appendChild(titleElement);
        
        if (filteredItems.length === 0) {
            const emptyElement = document.createElement('div');
            emptyElement.className = 'history-empty';
            emptyElement.textContent = 'Tidak ada hasil yang ditemukan';
            elements.historyList.appendChild(emptyElement);
            return;
        }
        
        // Render items
        filteredItems.forEach(item => {
            const historyElement = this.createHistoryItemElement(item);
            elements.historyList.appendChild(historyElement);
        });
    }

    /**
     * Export history ke CSV
     */
    exportToCSV() {
        try {
            const csvContent = this.generateCSVContent();
            const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
            
            // Create download link
            const link = document.createElement('a');
            const url = URL.createObjectURL(blob);
            link.setAttribute('href', url);
            link.setAttribute('download', `jagapadi_history_${new Date().toISOString().split('T')[0]}.csv`);
            
            // Trigger download
            document.body.appendChild(link);
            link.click();
            document.body.removeChild(link);
            
            this.app.showNotification('History berhasil diekspor ke CSV', 'success');
            
        } catch (error) {
            console.error('❌ Error exporting CSV:', error);
            this.app.showNotification('Gagal mengekspor history', 'error');
        }
    }

    /**
     * Generate konten CSV
     */
    generateCSVContent() {
        const headers = [
            'Tanggal',
            'Waktu', 
            'Nama File',
            'Hama Terdeteksi',
            'Jumlah Deteksi',
            'Tingkat Keyakinan (%)',
            'Waktu Proses (s)',
            'Sumber Data'
        ];
        
        const rows = this.history.map(item => [
            item.timestamp.toLocaleDateString('id-ID'),
            item.timestamp.toLocaleTimeString('id-ID'),
            item.filename,
            item.results?.detections?.map(d => d.name).join('; ') || '',
            item.results?.totalDetections || 0,
            item.results?.avgConfidence || 0,
            item.processingTime || 0,
            this.getSourceLabel(item.source)
        ]);
        
        const csvContent = [headers, ...rows]
            .map(row => row.map(field => `"${field}"`).join(','))
            .join('\n');
        
        return csvContent;
    }

    /**
     * Cleanup dan reset history manager
     */
    cleanup() {
        // Save current state
        this.saveToLocalStorage();
        
        // Clear memory
        this.history = [];
        this.todayStats = { detections: 0, accuracy: 0 };
        this.isHistoryLoaded = false;
        
        console.log('🧹 History manager cleanup completed');
    }

    /**
     * Get jumlah total history
     */
    getHistoryCount() {
        return this.history.length;
    }

    /**
     * Check apakah history sudah di-load
     */
    isLoaded() {
        return this.isHistoryLoaded;
    }

    /**
     * Force refresh history dari sumber yang tersedia
     */
    async refreshHistory() {
        console.log('🔄 Refreshing history...');
        this.isHistoryLoaded = false;
        await this.initializeHistory();
        this.app.showNotification('History berhasil di-refresh', 'info');
    }
}

// Export untuk digunakan di file lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = HistoryManager;
}