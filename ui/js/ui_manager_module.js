/**
 * JAGAPADI v2.2 - UI Manager Module
 * Mengelola semua aspek User Interface:
 * - Sidebar control
 * - Modal management
 * - Notification system
 * - Theme switching
 * - Responsive behavior
 * - Touch feedback
 * - Keyboard shortcuts
 */

class UIManager {
    constructor(app) {
        this.app = app; // Reference ke aplikasi utama
        this.sidebarOpen = false;
        this.isDarkMode = false;
        this.activeModals = [];
        this.notificationQueue = [];
        this.keyboardShortcuts = {};
        this.touchFeedbackEnabled = true;
        
        console.log('🎨 UI Manager initialized');
        
        // Initialize UI systems
        this.initializeTheme();
        this.initializeTouchFeedback();
        this.initializeKeyboardShortcuts();
        this.initializeResponsiveBehavior();
        this.initializeStatusBar();
    }

    // =====================================
    // SIDEBAR MANAGEMENT
    // =====================================

    /**
     * Toggle sidebar open/close
     */
    toggleSidebar() {
        this.sidebarOpen = !this.sidebarOpen;
        const { sidebar, sidebarOverlay } = this.app.elements;
        
        if (this.sidebarOpen) {
            this.openSidebar();
        } else {
            this.closeSidebar();
        }
        
        console.log(`📋 Sidebar ${this.sidebarOpen ? 'opened' : 'closed'}`);
    }

    /**
     * Open sidebar
     */
    openSidebar() {
        const { sidebar, sidebarOverlay } = this.app.elements;
        
        if (sidebar) {
            sidebar.classList.add('open');
        }
        if (sidebarOverlay) {
            sidebarOverlay.classList.add('show');
        }
        
        this.sidebarOpen = true;
        
        // Add body class untuk mencegah scroll
        document.body.classList.add('sidebar-open');
        
        // Focus management untuk accessibility
        this.manageFocusForSidebar(true);
    }

    /**
     * Close sidebar
     */
    closeSidebar() {
        const { sidebar, sidebarOverlay } = this.app.elements;
        
        if (sidebar) {
            sidebar.classList.remove('open');
        }
        if (sidebarOverlay) {
            sidebarOverlay.classList.remove('show');
        }
        
        this.sidebarOpen = false;
        
        // Remove body class
        document.body.classList.remove('sidebar-open');
        
        // Focus management
        this.manageFocusForSidebar(false);
    }

    /**
     * Manage focus untuk sidebar accessibility
     */
    manageFocusForSidebar(isOpen) {
        if (isOpen) {
            // Focus ke sidebar saat buka
            const firstFocusable = this.app.elements.sidebar?.querySelector('button, a, input, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                setTimeout(() => firstFocusable.focus(), 100);
            }
        } else {
            // Return focus ke toggle button
            if (this.app.elements.toggleSidebar) {
                this.app.elements.toggleSidebar.focus();
            }
        }
    }

    /**
     * Check apakah sidebar sedang terbuka
     */
    isSidebarOpen() {
        return this.sidebarOpen;
    }

    // =====================================
    // MODAL MANAGEMENT
    // =====================================

    /**
     * Show modal dengan backdrop
     */
    showModal(modalElement) {
        if (!modalElement) {
            console.error('❌ Modal element not provided');
            return false;
        }
        
        console.log(`📱 Opening modal: ${modalElement.id || 'unnamed'}`);
        
        // Add to active modals stack
        this.activeModals.push(modalElement);
        
        // Show modal
        modalElement.classList.add('show');
        modalElement.style.display = 'flex';
        
        // Add body class untuk background scroll lock
        document.body.classList.add('modal-open');
        
        // Focus management
        this.manageFocusForModal(modalElement, true);
        
        // Add escape key listener
        this.addModalEscapeListener();
        
        return true;
    }

    /**
     * Hide modal
     */
    hideModal(modalElement) {
        if (!modalElement) {
            console.error('❌ Modal element not provided');
            return false;
        }
        
        console.log(`📱 Closing modal: ${modalElement.id || 'unnamed'}`);
        
        // Remove from active modals
        this.activeModals = this.activeModals.filter(modal => modal !== modalElement);
        
        // Hide modal dengan animasi
        modalElement.classList.remove('show');
        
        setTimeout(() => {
            modalElement.style.display = 'none';
        }, 300); // Match CSS transition duration
        
        // Remove body class jika tidak ada modal lain
        if (this.activeModals.length === 0) {
            document.body.classList.remove('modal-open');
        }
        
        // Focus management
        this.manageFocusForModal(modalElement, false);
        
        return true;
    }

    /**
     * Manage focus untuk modal accessibility
     */
    manageFocusForModal(modalElement, isOpening) {
        if (isOpening) {
            // Focus ke elemen pertama dalam modal
            const firstFocusable = modalElement.querySelector('button, a, input, textarea, select, [tabindex]:not([tabindex="-1"])');
            if (firstFocusable) {
                setTimeout(() => firstFocusable.focus(), 100);
            }
        } else {
            // Return focus ke trigger element jika ada
            const triggerElement = document.activeElement;
            if (triggerElement && triggerElement !== document.body) {
                triggerElement.focus();
            }
        }
    }

    /**
     * Add escape key listener untuk modal
     */
    addModalEscapeListener() {
        const handleEscape = (e) => {
            if (e.key === 'Escape' && this.activeModals.length > 0) {
                const topModal = this.activeModals[this.activeModals.length - 1];
                this.hideModal(topModal);
            }
        };
        
        document.addEventListener('keydown', handleEscape, { once: true });
    }

    /**
     * Close semua modal
     */
    closeAllModals() {
        const modalsToClose = [...this.activeModals];
        modalsToClose.forEach(modal => this.hideModal(modal));
    }

    /**
     * Show auth modal
     */
    showAuthModal() {
        const success = this.showModal(this.app.elements.authModal);
        if (success && this.app.elements.passwordInput) {
            // Focus ke password input
            setTimeout(() => {
                this.app.elements.passwordInput.focus();
            }, 100);
        }
        return success;
    }

    /**
     * Hide auth modal
     */
    hideAuthModal() {
        const success = this.hideModal(this.app.elements.authModal);
        if (success && this.app.elements.passwordInput) {
            // Clear password field
            this.app.elements.passwordInput.value = '';
        }
        return success;
    }

    /**
     * Show history modal
     */
    showHistoryModal() {
        return this.showModal(this.app.elements.historyModal);
    }

    /**
     * Hide history modal
     */
    hideHistoryModal() {
        return this.hideModal(this.app.elements.historyModal);
    }

    // =====================================
    // NOTIFICATION SYSTEM
    // =====================================

    /**
     * Show notification dengan auto-hide
     */
    showNotification(message, type = 'info', duration = 3000) {
        if (!message) {
            console.error('❌ Notification message is required');
            return false;
        }
        
        console.log(`🔔 Notification (${type}): ${message}`);
        
        const notification = this.app.elements.notification;
        if (!notification) {
            console.error('❌ Notification element not found');
            return false;
        }
        
        // Queue notification jika ada yang sedang aktif
        if (notification.classList.contains('show')) {
            this.queueNotification(message, type, duration);
            return true;
        }
        
        // Set content dan style
        notification.textContent = message;
        notification.className = `notification ${type}`;
        
        // Show notification
        notification.classList.add('show');
        
        // Add accessibility attributes
        notification.setAttribute('role', 'alert');
        notification.setAttribute('aria-live', 'polite');
        
        // Auto-hide setelah duration
        setTimeout(() => {
            this.hideNotification();
        }, duration);
        
        return true;
    }

    /**
     * Hide notification
     */
    hideNotification() {
        const notification = this.app.elements.notification;
        if (notification) {
            notification.classList.remove('show');
            
            // Process queued notifications
            setTimeout(() => {
                this.processNotificationQueue();
            }, 300);
        }
    }

    /**
     * Queue notification untuk sequential display
     */
    queueNotification(message, type, duration) {
        this.notificationQueue.push({ message, type, duration });
        console.log(`📝 Notification queued: ${this.notificationQueue.length} in queue`);
    }

    /**
     * Process notification queue
     */
    processNotificationQueue() {
        if (this.notificationQueue.length > 0) {
            const next = this.notificationQueue.shift();
            this.showNotification(next.message, next.type, next.duration);
        }
    }

    /**
     * Clear notification queue
     */
    clearNotificationQueue() {
        this.notificationQueue = [];
        console.log('🗑️ Notification queue cleared');
    }

    // =====================================
    // THEME MANAGEMENT
    // =====================================

    /**
     * Initialize theme system
     */
    initializeTheme() {
        this.isDarkMode = this.loadTheme();
        this.applyTheme();
        console.log(`🎨 Theme initialized: ${this.isDarkMode ? 'dark' : 'light'}`);
    }

    /**
     * Toggle dark/light mode
     */
    toggleDarkMode() {
        this.isDarkMode = !this.isDarkMode;
        this.applyTheme();
        this.saveTheme();
        
        const mode = this.isDarkMode ? 'gelap' : 'terang';
        this.showNotification(`Mode ${mode} diaktifkan`, 'info');
        
        console.log(`🎨 Theme switched to: ${this.isDarkMode ? 'dark' : 'light'}`);
    }

    /**
     * Apply theme ke document
     */
    applyTheme() {
        const { darkModeBtn } = this.app.elements;
        
        if (this.isDarkMode) {
            document.documentElement.setAttribute('data-theme', 'dark');
            if (darkModeBtn) darkModeBtn.textContent = '☀️';
        } else {
            document.documentElement.removeAttribute('data-theme');
            if (darkModeBtn) darkModeBtn.textContent = '🌓';
        }
        
        // Dispatch theme change event
        window.dispatchEvent(new CustomEvent('themeChanged', {
            detail: { isDarkMode: this.isDarkMode }
        }));
    }

    /**
     * Load theme dari localStorage
     */
    loadTheme() {
        try {
            const saved = localStorage.getItem('jagapadi-dark-mode');
            return saved === 'true';
        } catch (error) {
            console.log('⚠️ LocalStorage not available, using default theme');
            return window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        }
    }

    /**
     * Save theme ke localStorage
     */
    saveTheme() {
        try {
            localStorage.setItem('jagapadi-dark-mode', this.isDarkMode.toString());
        } catch (error) {
            console.log('⚠️ LocalStorage not available, theme not saved');
        }
    }

    /**
     * Get current theme
     */
    getCurrentTheme() {
        return this.isDarkMode ? 'dark' : 'light';
    }

    // =====================================
    // TOUCH FEEDBACK
    // =====================================

    /**
     * Initialize touch feedback untuk interactive elements
     */
    initializeTouchFeedback() {
        if (!this.touchFeedbackEnabled) return;
        
        // Add touch feedback ke semua interactive elements
        const interactiveSelectors = [
            'button',
            '.history-item',
            '.stat-item',
            '.action-btn',
            '.modal-btn',
            '.touch-feedback'
        ];
        
        interactiveSelectors.forEach(selector => {
            this.addTouchFeedbackToSelector(selector);
        });
        
        console.log('👆 Touch feedback initialized');
    }

    /**
     * Add touch feedback ke selector tertentu
     */
    addTouchFeedbackToSelector(selector) {
        document.addEventListener('DOMContentLoaded', () => {
            const elements = document.querySelectorAll(selector);
            elements.forEach(element => this.addTouchFeedbackToElement(element));
        });
        
        // Handle dynamic elements dengan event delegation
        document.addEventListener('touchstart', (e) => {
            if (e.target.matches(selector)) {
                this.handleTouchStart(e.target);
            }
        }, { passive: true });
        
        document.addEventListener('touchend', (e) => {
            if (e.target.matches(selector)) {
                this.handleTouchEnd(e.target);
            }
        }, { passive: true });
    }

    /**
     * Add touch feedback ke element individual
     */
    addTouchFeedbackToElement(element) {
        element.classList.add('touch-feedback');
        
        element.addEventListener('touchstart', () => {
            this.handleTouchStart(element);
        }, { passive: true });
        
        element.addEventListener('touchend', () => {
            this.handleTouchEnd(element);
        }, { passive: true });
    }

    /**
     * Handle touch start
     */
    handleTouchStart(element) {
        element.style.transform = 'scale(0.98)';
        element.style.transition = 'transform 0.1s ease';
    }

    /**
     * Handle touch end
     */
    handleTouchEnd(element) {
        setTimeout(() => {
            element.style.transform = '';
            element.style.transition = '';
        }, 150);
    }

    // =====================================
    // KEYBOARD SHORTCUTS
    // =====================================

    /**
     * Initialize keyboard shortcuts
     */
    initializeKeyboardShortcuts() {
        // Define shortcuts
        this.keyboardShortcuts = {
            'Escape': () => this.handleEscapeKey(),
            ' ': (e) => this.handleSpaceKey(e),
            'Enter': (e) => this.handleEnterKey(e),
            'f': (e) => this.handleFileShortcut(e),
            'c': (e) => this.handleCameraShortcut(e),
            'd': (e) => this.handleDetectShortcut(e),
            's': (e) => this.handleSidebarShortcut(e),
            't': (e) => this.handleThemeShortcut(e)
        };
        
        // Add global keyboard listener
        document.addEventListener('keydown', (e) => this.handleKeyboard(e));
        
        console.log('⌨️ Keyboard shortcuts initialized');
    }

    /**
     * Handle keyboard events
     */
    handleKeyboard(e) {
        const key = e.key;
        const handler = this.keyboardShortcuts[key];
        
        if (handler) {
            // Skip jika sedang mengetik di input
            if (this.isTypingInInput(e.target)) {
                return;
            }
            
            handler(e);
        }
    }

    /**
     * Check apakah sedang mengetik di input field
     */
    isTypingInInput(target) {
        const inputTypes = ['INPUT', 'TEXTAREA', 'SELECT'];
        return inputTypes.includes(target.tagName) || target.contentEditable === 'true';
    }

    /**
     * Handle Escape key
     */
    handleEscapeKey() {
        // Priority: Modal > Sidebar > Other
        if (this.activeModals.length > 0) {
            const topModal = this.activeModals[this.activeModals.length - 1];
            this.hideModal(topModal);
        } else if (this.sidebarOpen) {
            this.closeSidebar();
        }
    }

    /**
     * Handle Space key
     */
    handleSpaceKey(e) {
        if (e.target === document.body) {
            e.preventDefault();
            const state = this.app.stateManager?.getCurrentState();
            
            if (state === 'initial' && this.app.connectionManager?.isConnected) {
                this.app.cameraHandler?.handleCameraAction();
            } else if (state === 'imageReady') {
                this.app.detectionSystem?.startDetection();
            }
        }
    }

    /**
     * Handle Enter key
     */
    handleEnterKey(e) {
        const state = this.app.stateManager?.getCurrentState();
        
        if (state === 'imageReady' && e.target === document.body) {
            this.app.detectionSystem?.startDetection();
        }
    }

    /**
     * Handle file shortcut (F)
     */
    handleFileShortcut(e) {
        if (e.ctrlKey || e.metaKey) return; // Skip Ctrl+F
        
        e.preventDefault();
        if (this.app.connectionManager?.isConnected) {
            this.app.imageHandler?.handleFileAction();
        }
    }

    /**
     * Handle camera shortcut (C)
     */
    handleCameraShortcut(e) {
        if (e.ctrlKey || e.metaKey) return; // Skip Ctrl+C
        
        e.preventDefault();
        if (this.app.connectionManager?.isConnected) {
            this.app.cameraHandler?.handleCameraAction();
        }
    }

    /**
     * Handle detect shortcut (D)
     */
    handleDetectShortcut(e) {
        e.preventDefault();
        const state = this.app.stateManager?.getCurrentState();
        
        if (state === 'imageReady') {
            this.app.detectionSystem?.startDetection();
        }
    }

    /**
     * Handle sidebar shortcut (S)
     */
    handleSidebarShortcut(e) {
        if (e.ctrlKey || e.metaKey) return; // Skip Ctrl+S
        
        e.preventDefault();
        this.toggleSidebar();
    }

    /**
     * Handle theme shortcut (T)
     */
    handleThemeShortcut(e) {
        if (e.ctrlKey || e.metaKey) return; // Skip Ctrl+T
        
        e.preventDefault();
        this.toggleDarkMode();
    }

    // =====================================
    // RESPONSIVE BEHAVIOR
    // =====================================

    /**
     * Initialize responsive behavior
     */
    initializeResponsiveBehavior() {
        window.addEventListener('resize', () => this.handleResize());
        window.addEventListener('orientationchange', () => this.handleOrientationChange());
        
        // Initial responsive setup
        this.handleResize();
        
        console.log('📱 Responsive behavior initialized');
    }

    /**
     * Handle window resize
     */
    handleResize() {
        const width = window.innerWidth;
        
        // Auto-close sidebar di desktop
        if (width > 768 && this.sidebarOpen) {
            this.closeSidebar();
        }
        
        // Update responsive classes
        document.body.classList.toggle('mobile', width <= 768);
        document.body.classList.toggle('tablet', width > 768 && width <= 1024);
        document.body.classList.toggle('desktop', width > 1024);
        
        // Dispatch resize event
        window.dispatchEvent(new CustomEvent('responsiveResize', {
            detail: { width, height: window.innerHeight }
        }));
    }

    /**
     * Handle orientation change
     */
    handleOrientationChange() {
        setTimeout(() => {
            this.handleResize();
            console.log('📱 Orientation changed');
        }, 100);
    }

    /**
     * Get current screen size category
     */
    getScreenSize() {
        const width = window.innerWidth;
        
        if (width <= 768) return 'mobile';
        if (width <= 1024) return 'tablet';
        return 'desktop';
    }

    /**
     * Check if mobile device
     */
    isMobile() {
        return this.getScreenSize() === 'mobile';
    }

    // =====================================
    // STATUS BAR
    // =====================================

    /**
     * Initialize status bar
     */
    initializeStatusBar() {
        this.updateStatusBar();
        
        // Update time setiap detik
        if (this.app.elements.statusTime) {
            setInterval(() => {
                this.updateTime();
            }, 1000);
        }
        
        console.log('📊 Status bar initialized');
    }

    /**
     * Update status bar
     */
    updateStatusBar() {
        this.updateTime();
        this.updateConnectionStatus();
    }

    /**
     * Update time display
     */
    updateTime() {
        if (this.app.elements.statusTime) {
            const now = new Date();
            this.app.elements.statusTime.textContent = now.toLocaleTimeString('id-ID');
        }
    }

    /**
     * Update connection status di status bar
     */
    updateConnectionStatus() {
        const isConnected = this.app.connectionManager?.isConnected || false;
        const statusElement = this.app.elements.globalStatus;
        
        if (statusElement && !statusElement.textContent) {
            statusElement.textContent = isConnected ? 'Terhubung ke server' : 'Siap untuk deteksi';
        }
    }

    // =====================================
    // UTILITY METHODS
    // =====================================

    /**
     * Add CSS class dengan animation
     */
    addClassWithAnimation(element, className, duration = 300) {
        if (!element) return;
        
        element.classList.add(className);
        
        return new Promise(resolve => {
            setTimeout(resolve, duration);
        });
    }

    /**
     * Remove CSS class dengan animation
     */
    removeClassWithAnimation(element, className, duration = 300) {
        if (!element) return;
        
        element.classList.remove(className);
        
        return new Promise(resolve => {
            setTimeout(resolve, duration);
        });
    }

    /**
     * Smooth scroll ke element
     */
    scrollToElement(element, behavior = 'smooth') {
        if (element) {
            element.scrollIntoView({ behavior, block: 'center' });
        }
    }

    /**
     * Get UI state untuk debugging
     */
    getUIState() {
        return {
            sidebar: {
                isOpen: this.sidebarOpen
            },
            modals: {
                active: this.activeModals.length,
                list: this.activeModals.map(modal => modal.id || 'unnamed')
            },
            theme: {
                isDark: this.isDarkMode,
                current: this.getCurrentTheme()
            },
            notifications: {
                queued: this.notificationQueue.length
            },
            responsive: {
                screenSize: this.getScreenSize(),
                isMobile: this.isMobile()
            }
        };
    }

    /**
     * Cleanup UI manager
     */
    cleanup() {
        // Close sidebar dan modals
        this.closeSidebar();
        this.closeAllModals();
        
        // Clear notifications
        this.clearNotificationQueue();
        
        // Save theme
        this.saveTheme();
        
        // Remove body classes
        document.body.classList.remove('sidebar-open', 'modal-open', 'mobile', 'tablet', 'desktop');
        
        console.log('🧹 UI Manager cleanup completed');
    }
}

// Export untuk digunakan di file lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = UIManager;
}