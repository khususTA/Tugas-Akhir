/**
 * JAGAPADI v2.2 - App Core Module (Complete & Concise)
 * Main Application Orchestrator
 * 
 * Orchestrator utama yang mengelola semua modul dan komponen aplikasi.
 * File ini berfungsi sebagai "konduktor orkestra" yang mengkoordinasikan
 * semua modul agar bekerja secara harmonis.
 */

class JagaPadiApp {
    constructor() {
        console.log('🌾 JAGAPADI v2.2 - AI Deteksi Hama Padi');
        console.log('🔧 Initializing App Core Orchestrator...');
        
        // =====================================
        // APPLICATION STATE MANAGEMENT
        // =====================================
        this.isAppReady = false;
        this.pendingOperations = [];
        this.initializationSteps = [];
        this.moduleLoadOrder = [];
        
        // =====================================
        // INITIALIZATION SEQUENCE
        // =====================================
        this.elements = this.initializeElements();
        this.initializeModules();
        this.initializeEventSystem();
        this.finalizeAppInitialization();
        
        console.log('✅ JAGAPADI v2.2 App Core initialization completed');
        this.logInitializationSummary();
    }

    // =====================================
    // DOM ELEMENTS INITIALIZATION
    // =====================================
    initializeElements() {
        console.log('📋 DOM Elements Orchestrator: Initializing...');
        
        const elements = {
            // Header & Navigation
            toggleSidebar: document.getElementById('toggleSidebar'),
            darkModeBtn: document.getElementById('darkModeBtn'),
            
            // Sidebar
            sidebar: document.getElementById('sidebar'),
            sidebarOverlay: document.getElementById('sidebarOverlay'),
            
            // Connection Status
            connectBtn: document.getElementById('btn-connect'),
            statusIndicator: document.getElementById('statusIndicator'),
            statusText: document.getElementById('statusText'),
            mainConnectionStatus: document.getElementById('mainConnectionStatus'),
            mainStatusDot: document.getElementById('mainStatusDot'),
            mainStatusText: document.getElementById('mainStatusText'),
            
            // Image Preview
            previewContainer: document.getElementById('previewContainer'),
            emptyState: document.getElementById('emptyState'),
            previewContent: document.getElementById('previewContent'),
            previewImage: document.getElementById('previewImage'),
            fileInput: document.getElementById('fileInput'),
            
            // Processing & Results Overlays
            processingOverlay: document.getElementById('processingOverlay'),
            processingText: document.getElementById('processingText'),
            progressBar: document.getElementById('progressBar'),
            resultsOverlay: document.getElementById('resultsOverlay'),
            resultsCount: document.getElementById('resultsCount'),
            
            // Action Buttons (State-based)
            actionSection: document.getElementById('actionSection'),
            initialActions: document.getElementById('initialActions'),
            imageReadyActions: document.getElementById('imageReadyActions'),
            processingActions: document.getElementById('processingActions'),
            resultsActions: document.getElementById('resultsActions'),
            
            // Individual Buttons
            cameraBtn: document.getElementById('cameraBtn'),
            fileBtn: document.getElementById('fileBtn'),
            changeImageBtn: document.getElementById('changeImageBtn'),
            detectBtn: document.getElementById('detectBtn'),
            newDetectionBtn: document.getElementById('newDetectionBtn'),
            viewDetailsBtn: document.getElementById('viewDetailsBtn'),
            
            // Results Panel
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
            
            // Authentication Modal
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
        
        // Validasi elemen yang wajib ada
        const requiredElements = [
            'previewContainer', 'toggleSidebar', 'connectBtn',
            'initialActions', 'imageReadyActions', 'processingActions', 'resultsActions'
        ];
        
        const missingElements = requiredElements.filter(id => !elements[id]);
        if (missingElements.length > 0) {
            console.error('❌ Missing required elements:', missingElements);
        }
        
        this.logInitStep('DOM Elements', 'Initialized');
        console.log('✅ DOM Elements Orchestrator: Ready');
        return elements;
    }

    // =====================================
    // MODULE SYSTEM ORCHESTRATOR
    // =====================================
    initializeModules() {
        console.log('🧩 Module System Orchestrator: Initializing modules...');
        
        try {
            // Core Utility Module (first)
            this.utilities = window.utils || new Utilities();
            this.moduleLoadOrder.push('Utilities');
            console.log('✅ Module loaded: Utilities');
            
            // UI Management Module
            this.uiManager = new UIManager(this);
            this.moduleLoadOrder.push('UI Manager');
            console.log('✅ Module loaded: UI Manager');
            
            // State Management Module
            this.stateManager = new StateManager(this);
            this.moduleLoadOrder.push('State Manager');
            console.log('✅ Module loaded: State Manager');
            
            // Connection Management Module
            this.connectionManager = new ConnectionManager(this);
            this.moduleLoadOrder.push('Connection Manager');
            console.log('✅ Module loaded: Connection Manager');
            
            // Image Handling Module
            this.imageHandler = new ImageHandler(this);
            this.moduleLoadOrder.push('Image Handler');
            console.log('✅ Module loaded: Image Handler');
            
            // Camera Handling Module
            this.cameraHandler = new CameraHandler(this);
            this.moduleLoadOrder.push('Camera Handler');
            console.log('✅ Module loaded: Camera Handler');
            
            // Detection System Module
            this.detectionSystem = new DetectionSystem(this);
            this.moduleLoadOrder.push('Detection System');
            console.log('✅ Module loaded: Detection System');
            
            // History Management Module
            this.historyManager = new HistoryManager(this);
            this.moduleLoadOrder.push('History Manager');
            console.log('✅ Module loaded: History Manager');
            
        } catch (error) {
            console.error('❌ Module initialization error:', error);
            throw new Error(`Module initialization failed: ${error.message}`);
        }
        
        this.logInitStep('Module System', 'Initialized');
        console.log('✅ Module System Orchestrator: All modules loaded');
    }

    // =====================================
    // EVENT SYSTEM ORCHESTRATOR
    // =====================================
    initializeEventSystem() {
        console.log('🎯 Event System Orchestrator: Initializing events...');
        
        try {
            this.setupNavigationEvents();
            this.setupConnectionEvents();
            this.setupImageCameraEvents();
            this.setupDetectionEvents();
            this.setupModalEvents();
            this.setupGlobalEvents();
        } catch (error) {
            console.error('❌ Event system initialization error:', error);
        }
        
        this.logInitStep('Event System', 'Initialized');
        console.log('✅ Event System Orchestrator: All events connected');
    }

    // Navigation Events
    setupNavigationEvents() {
        const { elements } = this;
        
        elements.toggleSidebar?.addEventListener('click', () => {
            this.uiManager.toggleSidebar();
        });
        
        elements.darkModeBtn?.addEventListener('click', () => {
            this.uiManager.toggleDarkMode();
        });
        
        elements.sidebarOverlay?.addEventListener('click', () => {
            this.uiManager.closeSidebar();
        });
        
        console.log('✅ Navigation events setup complete');
    }

    // Connection Events
    setupConnectionEvents() {
        const { elements } = this;
        
        elements.connectBtn?.addEventListener('click', () => {
            if (this.connectionManager.isConnected) {
                this.connectionManager.disconnect();
            } else {
                this.uiManager.showAuthModal();
            }
        });
        
        elements.confirmAuthBtn?.addEventListener('click', () => {
            this.connectionManager.connect();
        });
        
        elements.cancelAuthBtn?.addEventListener('click', () => {
            this.uiManager.hideAuthModal();
        });
        
        elements.passwordInput?.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.connectionManager.connect();
            }
        });
        
        console.log('✅ Connection events setup complete');
    }

    // Image & Camera Events
    setupImageCameraEvents() {
        const { elements } = this;
        
        elements.cameraBtn?.addEventListener('click', () => {
            this.cameraHandler.handleCameraAction();
        });
        
        elements.fileBtn?.addEventListener('click', () => {
            this.imageHandler.handleFileAction();
        });
        
        elements.changeImageBtn?.addEventListener('click', () => {
            this.imageHandler.handleChangeImage();
        });
        
        elements.fileInput?.addEventListener('change', (e) => {
            if (e.target.files && e.target.files[0]) {
                this.imageHandler.handleFileSelect(e.target.files[0]);
            }
        });
        
        console.log('✅ Image & Camera events setup complete');
    }

    // Detection Events
    setupDetectionEvents() {
        const { elements } = this;
        
        elements.detectBtn?.addEventListener('click', () => {
            this.detectionSystem.startDetection();
        });
        
        elements.newDetectionBtn?.addEventListener('click', () => {
            this.detectionSystem.startNewDetection();
        });
        
        elements.viewDetailsBtn?.addEventListener('click', () => {
            this.detectionSystem.showDetailedResults();
        });
        
        console.log('✅ Detection events setup complete');
    }

    // Modal Events
    setupModalEvents() {
        const { elements } = this;
        
        elements.closeHistoryModal?.addEventListener('click', () => {
            this.uiManager.hideHistoryModal();
        });
        
        // Close modals on background click
        elements.authModal?.addEventListener('click', (e) => {
            if (e.target === elements.authModal) {
                this.uiManager.hideAuthModal();
            }
        });
        
        elements.historyModal?.addEventListener('click', (e) => {
            if (e.target === elements.historyModal) {
                this.uiManager.hideHistoryModal();
            }
        });
        
        console.log('✅ Modal events setup complete');
    }

    // Global Events
    setupGlobalEvents() {
        window.addEventListener('resize', () => {
            this.handleResize();
        });
        
        window.addEventListener('beforeunload', () => {
            this.cleanup();
        });
        
        window.addEventListener('pywebviewready', () => {
            this.handlePyWebViewReady();
        });
        
        console.log('✅ Global events setup complete');
    }

    // =====================================
    // APP READINESS ORCHESTRATOR
    // =====================================
    finalizeAppInitialization() {
        console.log('🎯 App Readiness Orchestrator: Finalizing...');
        
        this.isAppReady = true;
        this.signalFrontendReady();
        this.processPendingOperations();
        this.stateManager.setState('initial');
        
        // Global exposure untuk backend communication
        window.app = this;
        
        this.logInitStep('App Readiness', 'Completed');
        console.log('✅ App Readiness Orchestrator: Application ready for use!');
    }

    // =====================================
    // BACKEND COMMUNICATION
    // =====================================
    signalFrontendReady() {
        try {
            console.log('🎯 Signaling frontend ready to Python backend...');
            
            if (window.pywebview && window.pywebview.api && window.pywebview.api.frontend_ready) {
                console.log('🔌 Signaling via PyWebView API...');
                window.pywebview.api.frontend_ready();
            } else {
                console.log('⚠️ PyWebView API not available, using fallback method');
                window._frontendReady = true;
            }
        } catch (error) {
            console.error('❌ Failed to signal frontend ready:', error);
            window._frontendReady = true;
        }
    }

    queuePendingOperation(type, callback, args) {
        console.log(`⏳ Queueing pending operation: ${type}`);
        this.pendingOperations.push({
            type: type,
            callback: callback,
            args: args,
            timestamp: Date.now()
        });
    }

    processPendingOperations() {
        if (this.pendingOperations.length > 0) {
            console.log(`📋 Processing ${this.pendingOperations.length} pending operations`);
            
            this.pendingOperations.forEach(operation => {
                try {
                    operation.callback.apply(this, operation.args);
                    console.log(`✅ Processed: ${operation.type}`);
                } catch (error) {
                    console.error(`❌ Failed to process ${operation.type}:`, error);
                }
            });
            
            this.pendingOperations = [];
        }
        
        // Process pending history data
        if (window._pendingHistoryData) {
            console.log('📊 Processing pending history data');
            this.historyManager.loadHistoryFromBackend(window._pendingHistoryData);
            delete window._pendingHistoryData;
        }
    }

    // =====================================
    // GLOBAL FUNCTIONS FOR BACKEND
    // =====================================
    tampilkanHasil(base64img) {
        console.log('🔌 Backend calling tampilkanHasil');
        
        if (!this.isAppReady) {
            this.queuePendingOperation('tampilkanHasil', this.tampilkanHasil, [base64img]);
            return;
        }

        try {
            this.detectionSystem.tampilkanHasil(base64img);
        } catch (error) {
            console.error('❌ Error in tampilkanHasil:', error);
        }
    }

    updateStatus(message) {
        console.log('🔌 Backend calling updateStatus');
        
        try {
            this.stateManager.updateGlobalStatus(message);
        } catch (error) {
            console.error('❌ Error in updateStatus:', error);
        }
    }

    // =====================================
    // STATE MANAGEMENT SHORTCUTS
    // =====================================
    setState(state) {
        return this.stateManager.setState(state);
    }

    getCurrentState() {
        return this.stateManager.getCurrentState();
    }

    // =====================================
    // UI SHORTCUTS
    // =====================================
    showNotification(message, type = 'info', duration = 3000) {
        return this.uiManager.showNotification(message, type, duration);
    }

    hideAuthModal() {
        return this.uiManager.hideAuthModal();
    }

    updateGlobalStatus(message) {
        return this.stateManager.updateGlobalStatus(message);
    }

    // =====================================
    // EVENT HANDLERS
    // =====================================
    handlePyWebViewReady() {
        console.log('🔌 PyWebView API ready');
        this.signalFrontendReady();
    }

    handleResize() {
        this.uiManager.handleResize();
    }

    cleanup() {
        console.log('🧹 App cleanup initiated...');
        
        try {
            this.historyManager?.cleanup();
            this.detectionSystem?.cleanup();
            this.cameraHandler?.cleanup();
            this.uiManager?.cleanup();
            this.stateManager?.cleanup();
            
            console.log('✅ App cleanup completed');
        } catch (error) {
            console.error('❌ Cleanup error:', error);
        }
    }

    // =====================================
    // LOGGING & DEBUGGING
    // =====================================
    logInitStep(component, status) {
        this.initializationSteps.push({
            component,
            status,
            timestamp: Date.now(),
            time: new Date().toLocaleTimeString()
        });
    }

    logInitializationSummary() {
        console.log('📋 Initialization Summary:');
        console.log(`   • Total modules: ${this.moduleLoadOrder.length}`);
        console.log(`   • Load order: ${this.moduleLoadOrder.join(' → ')}`);
        console.log(`   • Total steps: ${this.initializationSteps.length}`);
        console.log(`   • App ready: ${this.isAppReady}`);
        console.log('🎉 JAGAPADI v2.2 ready for pest detection!');
    }

    getDebugInfo() {
        return {
            appInfo: {
                version: '2.2',
                ready: this.isAppReady,
                moduleCount: this.moduleLoadOrder.length
            },
            modules: {
                loadOrder: this.moduleLoadOrder,
                loaded: {
                    utilities: !!this.utilities,
                    uiManager: !!this.uiManager,
                    stateManager: !!this.stateManager,
                    connectionManager: !!this.connectionManager,
                    imageHandler: !!this.imageHandler,
                    cameraHandler: !!this.cameraHandler,
                    detectionSystem: !!this.detectionSystem,
                    historyManager: !!this.historyManager
                }
            },
            initialization: {
                steps: this.initializationSteps,
                pendingOperations: this.pendingOperations.length
            },
            ui: this.uiManager?.getUIState(),
            state: this.stateManager?.getDebugInfo(),
            connection: this.connectionManager?.getConnectionStatus()
        };
    }
}

// =====================================
// GLOBAL FUNCTIONS FOR BACKEND COMPATIBILITY
// =====================================
let app = null;

// Global functions for backend compatibility
window.loadHistoryFromBackend = function(historyData) {
    console.log('🔌 Backend calling loadHistoryFromBackend');
    try {
        if (window.app && window.app.historyManager) {
            window.app.historyManager.loadHistoryFromBackend(historyData);
        } else {
            console.log('⏳ App not ready, storing history for later');
            window._pendingHistoryData = historyData;
        }
    } catch (error) {
        console.error('❌ Error in loadHistoryFromBackend:', error);
    }
};

window.addDetectionFromBackend = function(detectionData) {
    console.log('🔌 Backend calling addDetectionFromBackend');
    try {
        if (window.app && window.app.historyManager) {
            window.app.historyManager.addDetectionFromBackend(detectionData);
        } else {
            console.log('⏳ App not ready for detection adding');
        }
    } catch (error) {
        console.error('❌ Error in addDetectionFromBackend:', error);
    }
};

// Legacy functions for backward compatibility
function tampilkanHasil(base64img) {
    if (window.app) {
        window.app.tampilkanHasil(base64img);
    } else {
        console.log('⏳ App not ready for tampilkanHasil');
    }
}

function updateStatus(message) {
    if (window.app) {
        window.app.updateStatus(message);
    } else {
        console.log('📊 Status update (app not ready):', message);
    }
}

// =====================================
// APPLICATION INITIALIZATION
// =====================================
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 DOM loaded, initializing JAGAPADI v2.2...');
    
    try {
        app = new JagaPadiApp();
        window.app = app;
        
        console.log('🎉 JAGAPADI v2.2 initialization successful!');
    } catch (error) {
        console.error('💥 JAGAPADI initialization failed:', error);
        
        // Show error notification if possible
        const notification = document.getElementById('notification');
        if (notification) {
            notification.textContent = 'Gagal menginisialisasi aplikasi';
            notification.className = 'notification error show';
        }
    }
});

// =====================================
// WINDOW LOAD EVENT
// =====================================
window.addEventListener('load', () => {
    console.log('🌾 JAGAPADI v2.2 fully loaded!');
    console.log('🔧 All modules orchestrated successfully');
    console.log('🎯 Frontend-backend synchronization ready');
    console.log('💾 Local-first history system active');
    console.log('🔄 State management system active');
    console.log('🎨 UI management system active');
    console.log('📷 Camera & image handling ready');
    console.log('🔬 Detection system ready');
    console.log('📋 History management ready');
    console.log('✨ Application ready for pest detection!');
});

// Export untuk digunakan di environment lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { JagaPadiApp, tampilkanHasil, updateStatus };
}