/**
 * JAGAPADI v2.2 - State Manager Module
 * Mengelola state aplikasi dan transisi antar state:
 * - State management sistem
 * - UI state transitions
 * - Action button management
 * - State-based UI updates
 * - Animation transitions
 */

class StateManager {
    constructor(app) {
        this.app = app; // Reference ke aplikasi utama
        this.currentState = 'initial';
        this.previousState = null;
        this.stateHistory = [];
        this.maxStateHistory = 10;
        
        // State definitions
        this.availableStates = [
            'initial',      // Kondisi awal, belum ada gambar
            'imageReady',   // Gambar sudah dipilih, siap deteksi
            'processing',   // Sedang proses deteksi
            'results'       // Hasil deteksi sudah ditampilkan
        ];
        
        console.log('🔄 State Manager initialized');
    }

    /**
     * Set state baru dengan validasi dan logging
     */
    setState(newState, force = false) {
        // Validasi state
        if (!this.availableStates.includes(newState)) {
            console.error(`❌ Invalid state: ${newState}`);
            return false;
        }

        // Cek apakah state sudah sama (skip jika tidak force)
        if (this.currentState === newState && !force) {
            console.log(`⚠️ State already ${newState}, skipping transition`);
            return true;
        }

        console.log(`🔄 State transition: ${this.currentState} → ${newState}`);
        
        // Simpan state sebelumnya
        this.previousState = this.currentState;
        
        // Add to state history
        this.addToStateHistory(this.currentState, newState);
        
        // Update current state
        this.currentState = newState;
        
        // Execute state transition
        this.executeStateTransition(newState);
        
        // Update global status
        this.updateGlobalStatus();
        
        // Animate transition
        this.animateStateTransition(this.previousState, newState);
        
        return true;
    }

    /**
     * Execute state transition dan update UI
     */
    executeStateTransition(newState) {
        // Hide semua action groups dulu
        this.hideAllActionGroups();
        
        // Execute specific state logic
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
                console.warn(`Unknown state logic for: ${newState}`);
        }
        
        // Update button states berdasarkan koneksi
        this.updateButtonStates();
        
        console.log(`✅ State ${newState} activated`);
    }

    /**
     * Hide semua action groups
     */
    hideAllActionGroups() {
        const { elements } = this.app;
        const actionGroups = [
            elements.initialActions,
            elements.imageReadyActions,
            elements.processingActions,
            elements.resultsActions
        ];
        
        actionGroups.forEach(group => {
            if (group) {
                group.classList.add('hidden');
            }
        });
    }

    /**
     * Show initial state - kondisi awal aplikasi
     */
    showInitialState() {
        const { elements } = this.app;
        
        console.log('🎯 Showing initial state');
        
        // Show empty state, hide preview content
        if (elements.emptyState) {
            elements.emptyState.classList.remove('hidden');
        }
        if (elements.previewContent) {
            elements.previewContent.classList.remove('show');
            elements.previewContent.classList.add('hidden');
        }
        if (elements.resultsPanel) {
            elements.resultsPanel.classList.add('hidden');
        }
        
        // Hide overlays
        if (elements.processingOverlay) {
            elements.processingOverlay.classList.remove('show');
        }
        if (elements.resultsOverlay) {
            elements.resultsOverlay.classList.remove('show');
        }
        
        // Show initial action buttons
        if (elements.initialActions) {
            elements.initialActions.classList.remove('hidden');
        }
        
        // Reset any processing state
        if (this.app.detectionSystem) {
            this.app.detectionSystem.stopProcessingAnimation();
        }
        
        this.updateGlobalStatus('Siap untuk deteksi');
    }

    /**
     * Show image ready state - gambar sudah dipilih
     */
    showImageReadyState() {
        const { elements } = this.app;
        
        console.log('🖼️ Showing image ready state');
        
        // Hide empty state, show image preview
        if (elements.emptyState) {
            elements.emptyState.classList.add('hidden');
        }
        if (elements.previewContent) {
            elements.previewContent.classList.remove('hidden');
            elements.previewContent.classList.add('show');
        }
        if (elements.resultsPanel) {
            elements.resultsPanel.classList.add('hidden');
        }
        
        // Hide overlays
        if (elements.processingOverlay) {
            elements.processingOverlay.classList.remove('show');
        }
        if (elements.resultsOverlay) {
            elements.resultsOverlay.classList.remove('show');
        }
        
        // Show image ready actions
        if (elements.imageReadyActions) {
            elements.imageReadyActions.classList.remove('hidden');
        }
        
        this.updateGlobalStatus('Gambar siap untuk dianalisis');
    }

    /**
     * Show processing state - sedang proses deteksi
     */
    showProcessingState() {
        const { elements } = this.app;
        
        console.log('⚙️ Showing processing state');
        
        // Keep image visible, show processing overlay
        if (elements.processingOverlay) {
            elements.processingOverlay.classList.add('show');
        }
        if (elements.resultsOverlay) {
            elements.resultsOverlay.classList.remove('show');
        }
        
        // Show processing actions (disabled state)
        if (elements.processingActions) {
            elements.processingActions.classList.remove('hidden');
        }
        
        // Start processing animation
        if (this.app.detectionSystem) {
            this.app.detectionSystem.startProcessingAnimation();
        }
        
        this.updateGlobalStatus('Menganalisis gambar...');
    }

    /**
     * Show results state - hasil deteksi sudah ada
     */
    showResultsState() {
        const { elements } = this.app;
        
        console.log('📊 Showing results state');
        
        // Hide processing overlay, show results
        if (elements.processingOverlay) {
            elements.processingOverlay.classList.remove('show');
        }
        if (elements.resultsOverlay) {
            elements.resultsOverlay.classList.add('show');
        }
        if (elements.resultsPanel) {
            elements.resultsPanel.classList.remove('hidden');
        }
        
        // Show results actions
        if (elements.resultsActions) {
            elements.resultsActions.classList.remove('hidden');
        }
        
        // Stop processing animation
        if (this.app.detectionSystem) {
            this.app.detectionSystem.stopProcessingAnimation();
        }
        
        this.updateGlobalStatus('Deteksi selesai');
    }

    /**
     * Update status tombol berdasarkan state dan koneksi
     */
    updateButtonStates() {
        const { elements } = this.app;
        const isConnected = this.app.connectionManager?.isConnected || false;
        
        // Buttons yang perlu koneksi
        const connectionRequiredButtons = [
            elements.cameraBtn,
            elements.fileBtn,
            elements.detectBtn
        ];
        
        connectionRequiredButtons.forEach(button => {
            if (button) {
                button.disabled = !isConnected;
            }
        });
        
        // State-specific button logic
        switch (this.currentState) {
            case 'initial':
                // Enable camera/file buttons jika connected
                if (elements.cameraBtn) elements.cameraBtn.disabled = !isConnected;
                if (elements.fileBtn) elements.fileBtn.disabled = !isConnected;
                break;
                
            case 'imageReady':
                // Enable detect button jika connected
                if (elements.detectBtn) elements.detectBtn.disabled = !isConnected;
                if (elements.changeImageBtn) elements.changeImageBtn.disabled = false;
                break;
                
            case 'processing':
                // Disable semua buttons saat processing
                connectionRequiredButtons.forEach(button => {
                    if (button) button.disabled = true;
                });
                if (elements.changeImageBtn) elements.changeImageBtn.disabled = true;
                break;
                
            case 'results':
                // Enable action buttons
                if (elements.newDetectionBtn) elements.newDetectionBtn.disabled = false;
                if (elements.viewDetailsBtn) elements.viewDetailsBtn.disabled = false;
                break;
        }
        
        console.log(`🔘 Button states updated for ${this.currentState} (connected: ${isConnected})`);
    }

    /**
     * Update global status message
     */
    updateGlobalStatus(message) {
        if (this.app.elements.globalStatus) {
            this.app.elements.globalStatus.textContent = message || this.getDefaultStatusMessage();
        }
        console.log(`📊 Status: ${message}`);
    }

    /**
     * Get default status message untuk current state
     */
    getDefaultStatusMessage() {
        switch (this.currentState) {
            case 'initial':
                return 'Siap untuk deteksi';
            case 'imageReady':
                return 'Gambar siap untuk dianalisis';
            case 'processing':
                return 'Menganalisis gambar...';
            case 'results':
                return 'Deteksi selesai';
            default:
                return 'JAGAPADI - AI Deteksi Hama Padi';
        }
    }

    /**
     * Animate state transition
     */
    animateStateTransition(fromState, toState) {
        if (fromState === toState) return;
        
        console.log(`🎬 Animating transition: ${fromState} → ${toState}`);
        
        // Add subtle animation between states
        const container = this.app.elements.previewContainer;
        if (container) {
            container.style.transform = 'scale(0.98)';
            container.style.opacity = '0.9';
            container.style.transition = 'all 0.2s ease';
            
            setTimeout(() => {
                container.style.transform = '';
                container.style.opacity = '';
            }, 200);
        }
        
        // Add state-specific animations
        this.addStateSpecificAnimations(fromState, toState);
    }

    /**
     * Add animasi spesifik untuk transisi tertentu
     */
    addStateSpecificAnimations(fromState, toState) {
        const { elements } = this.app;
        
        // Animation: initial → imageReady
        if (fromState === 'initial' && toState === 'imageReady') {
            if (elements.previewContent) {
                elements.previewContent.style.transform = 'scale(0.95)';
                elements.previewContent.style.opacity = '0';
                
                setTimeout(() => {
                    elements.previewContent.style.transform = '';
                    elements.previewContent.style.opacity = '';
                }, 50);
            }
        }
        
        // Animation: imageReady → processing
        if (fromState === 'imageReady' && toState === 'processing') {
            if (elements.processingOverlay) {
                elements.processingOverlay.style.opacity = '0';
                setTimeout(() => {
                    elements.processingOverlay.style.opacity = '';
                }, 100);
            }
        }
        
        // Animation: processing → results
        if (fromState === 'processing' && toState === 'results') {
            if (elements.resultsOverlay) {
                elements.resultsOverlay.style.transform = 'translateY(-10px)';
                elements.resultsOverlay.style.opacity = '0';
                
                setTimeout(() => {
                    elements.resultsOverlay.style.transform = '';
                    elements.resultsOverlay.style.opacity = '';
                }, 50);
            }
        }
    }

    /**
     * Add state ke history untuk debugging
     */
    addToStateHistory(fromState, toState) {
        const historyEntry = {
            from: fromState,
            to: toState,
            timestamp: Date.now(),
            time: new Date().toLocaleTimeString()
        };
        
        this.stateHistory.unshift(historyEntry);
        
        // Keep only last N entries
        if (this.stateHistory.length > this.maxStateHistory) {
            this.stateHistory = this.stateHistory.slice(0, this.maxStateHistory);
        }
    }

    /**
     * Get current state
     */
    getCurrentState() {
        return this.currentState;
    }

    /**
     * Get previous state
     */
    getPreviousState() {
        return this.previousState;
    }

    /**
     * Check apakah dalam state tertentu
     */
    isInState(state) {
        return this.currentState === state;
    }

    /**
     * Check apakah bisa transisi ke state tertentu
     */
    canTransitionTo(targetState) {
        // Basic validation
        if (!this.availableStates.includes(targetState)) {
            return false;
        }
        
        // State-specific transition rules
        switch (this.currentState) {
            case 'initial':
                return ['imageReady'].includes(targetState);
                
            case 'imageReady':
                return ['initial', 'processing'].includes(targetState);
                
            case 'processing':
                return ['results', 'imageReady'].includes(targetState); // imageReady for errors
                
            case 'results':
                return ['initial', 'imageReady', 'processing'].includes(targetState);
                
            default:
                return true; // Allow any transition as fallback
        }
    }

    /**
     * Force state transition (bypass validation)
     */
    forceState(state) {
        return this.setState(state, true);
    }

    /**
     * Reset ke state awal
     */
    resetToInitial() {
        console.log('🔄 Resetting to initial state');
        return this.setState('initial', true);
    }

    /**
     * Get state history untuk debugging
     */
    getStateHistory() {
        return [...this.stateHistory];
    }

    /**
     * Get state statistics
     */
    getStateStats() {
        const stats = {};
        
        this.stateHistory.forEach(entry => {
            const key = `${entry.from}→${entry.to}`;
            stats[key] = (stats[key] || 0) + 1;
        });
        
        return {
            currentState: this.currentState,
            previousState: this.previousState,
            totalTransitions: this.stateHistory.length,
            transitionCounts: stats,
            lastTransition: this.stateHistory[0] || null
        };
    }

    /**
     * Validate current state dengan UI
     */
    validateCurrentState() {
        const { elements } = this.app;
        let isValid = true;
        const issues = [];
        
        switch (this.currentState) {
            case 'initial':
                if (!elements.emptyState?.classList.contains('hidden')) {
                    // OK
                } else {
                    issues.push('Empty state should be visible');
                    isValid = false;
                }
                break;
                
            case 'imageReady':
                if (elements.previewContent?.classList.contains('show')) {
                    // OK
                } else {
                    issues.push('Preview content should be visible');
                    isValid = false;
                }
                break;
                
            case 'processing':
                if (elements.processingOverlay?.classList.contains('show')) {
                    // OK
                } else {
                    issues.push('Processing overlay should be visible');
                    isValid = false;
                }
                break;
                
            case 'results':
                if (elements.resultsOverlay?.classList.contains('show')) {
                    // OK
                } else {
                    issues.push('Results overlay should be visible');
                    isValid = false;
                }
                break;
        }
        
        return {
            isValid,
            issues,
            state: this.currentState
        };
    }

    /**
     * Debug info untuk troubleshooting
     */
    getDebugInfo() {
        return {
            currentState: this.currentState,
            previousState: this.previousState,
            stateHistory: this.getStateHistory().slice(0, 5), // Last 5 transitions
            validation: this.validateCurrentState(),
            stats: this.getStateStats(),
            availableStates: this.availableStates,
            canTransitionTo: this.availableStates.map(state => ({
                state,
                allowed: this.canTransitionTo(state)
            }))
        };
    }

    /**
     * Cleanup state manager
     */
    cleanup() {
        // Reset to initial state
        this.resetToInitial();
        
        // Clear history
        this.stateHistory = [];
        this.previousState = null;
        
        console.log('🧹 State manager cleanup completed');
    }
}

// Export untuk digunakan di file lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = StateManager;
}