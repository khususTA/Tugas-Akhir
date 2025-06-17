/**
 * JAGAPADI v2.2 - Utilities Module (Ringkas)
 * Helper functions, formatters, validators, dan constants
 */

class Utilities {
    constructor() {
        // Constants
        this.APP_VERSION = '2.2';
        this.APP_NAME = 'JAGAPADI';
        this.MAX_FILE_SIZE = 10 * 1024 * 1024; // 10MB
        this.SUPPORTED_FORMATS = ['jpg', 'jpeg', 'png', 'webp', 'gif'];
        this.LOCAL_STORAGE_PREFIX = 'jagapadi_';
        
        console.log('🛠️ Utilities initialized');
    }

    // =====================================
    // FILE UTILITIES
    // =====================================

    /**
     * Format ukuran file
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Validasi file gambar
     */
    validateImageFile(file) {
        if (!file) return { valid: false, message: 'File tidak ada' };
        
        // Check type
        if (!file.type.startsWith('image/')) {
            return { valid: false, message: 'Bukan file gambar' };
        }
        
        // Check size
        if (file.size > this.MAX_FILE_SIZE) {
            return { valid: false, message: `File terlalu besar (max ${this.formatFileSize(this.MAX_FILE_SIZE)})` };
        }
        
        if (file.size < 1024) {
            return { valid: false, message: 'File terlalu kecil' };
        }
        
        return { valid: true, message: 'File valid' };
    }

    /**
     * Get file extension
     */
    getFileExtension(filename) {
        return filename.split('.').pop().toLowerCase();
    }

    // =====================================
    // DATE & TIME UTILITIES
    // =====================================

    /**
     * Format tanggal Indonesia
     */
    formatDate(date, options = {}) {
        const defaultOptions = {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            ...options
        };
        
        return new Date(date).toLocaleDateString('id-ID', defaultOptions);
    }

    /**
     * Format waktu Indonesia
     */
    formatTime(date, options = {}) {
        const defaultOptions = {
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit',
            ...options
        };
        
        return new Date(date).toLocaleTimeString('id-ID', defaultOptions);
    }

    /**
     * Format durasi
     */
    formatDuration(seconds) {
        if (seconds < 60) return `${seconds.toFixed(1)}s`;
        if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${(seconds % 60).toFixed(0)}s`;
        return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
    }

    /**
     * Relative time (berapa lama yang lalu)
     */
    getRelativeTime(date) {
        const now = new Date();
        const diff = now - new Date(date);
        const seconds = Math.floor(diff / 1000);
        const minutes = Math.floor(seconds / 60);
        const hours = Math.floor(minutes / 60);
        const days = Math.floor(hours / 24);
        
        if (seconds < 60) return 'Baru saja';
        if (minutes < 60) return `${minutes} menit lalu`;
        if (hours < 24) return `${hours} jam lalu`;
        if (days < 7) return `${days} hari lalu`;
        return this.formatDate(date, { day: 'numeric', month: 'short' });
    }

    // =====================================
    // VALIDATION UTILITIES
    // =====================================

    /**
     * Validasi password
     */
    validatePassword(password) {
        if (!password) return { valid: false, message: 'Password kosong' };
        if (password.length < 3) return { valid: false, message: 'Password terlalu pendek' };
        return { valid: true, message: 'Password valid' };
    }

    /**
     * Validasi email (basic)
     */
    validateEmail(email) {
        const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return regex.test(email);
    }

    /**
     * Sanitize input
     */
    sanitizeInput(input) {
        return input.replace(/[<>]/g, '').trim();
    }

    // =====================================
    // LOCAL STORAGE UTILITIES
    // =====================================

    /**
     * Save ke localStorage dengan prefix
     */
    saveToStorage(key, value) {
        try {
            localStorage.setItem(this.LOCAL_STORAGE_PREFIX + key, JSON.stringify(value));
            return true;
        } catch (error) {
            console.error('Storage save error:', error);
            return false;
        }
    }

    /**
     * Load dari localStorage
     */
    loadFromStorage(key, defaultValue = null) {
        try {
            const stored = localStorage.getItem(this.LOCAL_STORAGE_PREFIX + key);
            return stored ? JSON.parse(stored) : defaultValue;
        } catch (error) {
            console.error('Storage load error:', error);
            return defaultValue;
        }
    }

    /**
     * Remove dari localStorage
     */
    removeFromStorage(key) {
        try {
            localStorage.removeItem(this.LOCAL_STORAGE_PREFIX + key);
            return true;
        } catch (error) {
            console.error('Storage remove error:', error);
            return false;
        }
    }

    // =====================================
    // STRING UTILITIES
    // =====================================

    /**
     * Generate random ID
     */
    generateId(prefix = 'id') {
        return `${prefix}_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    /**
     * Truncate text
     */
    truncateText(text, maxLength = 50) {
        if (text.length <= maxLength) return text;
        return text.substr(0, maxLength - 3) + '...';
    }

    /**
     * Capitalize first letter
     */
    capitalize(text) {
        return text.charAt(0).toUpperCase() + text.slice(1);
    }

    /**
     * Clean filename
     */
    cleanFilename(filename) {
        return filename.replace(/[^a-zA-Z0-9._-]/g, '_');
    }

    // =====================================
    // NUMBER UTILITIES
    // =====================================

    /**
     * Format number dengan pemisah ribuan
     */
    formatNumber(num) {
        return new Intl.NumberFormat('id-ID').format(num);
    }

    /**
     * Format percentage
     */
    formatPercentage(value, decimals = 1) {
        return `${value.toFixed(decimals)}%`;
    }

    /**
     * Clamp number between min and max
     */
    clamp(value, min, max) {
        return Math.min(Math.max(value, min), max);
    }

    // =====================================
    // DETECTION UTILITIES
    // =====================================

    /**
     * Get confidence level class
     */
    getConfidenceClass(confidence) {
        if (confidence >= 95) return 'confidence-excellent';
        if (confidence >= 85) return 'confidence-good';
        if (confidence >= 75) return 'confidence-fair';
        return 'confidence-low';
    }

    /**
     * Get confidence description
     */
    getConfidenceDescription(confidence) {
        if (confidence >= 95) return 'Sangat Yakin';
        if (confidence >= 85) return 'Yakin';
        if (confidence >= 75) return 'Cukup Yakin';
        return 'Kurang Yakin';
    }

    /**
     * Format detection summary
     */
    formatDetectionSummary(results) {
        if (!results || !results.detections) return 'Tidak ada deteksi';
        
        const count = results.totalDetections || results.detections.length;
        const confidence = results.avgConfidence || 0;
        
        return `${count} hama terdeteksi (${confidence}% yakin)`;
    }

    // =====================================
    // ARRAY UTILITIES
    // =====================================

    /**
     * Remove duplicates from array
     */
    removeDuplicates(array, key = null) {
        if (key) {
            return array.filter((item, index, self) => 
                index === self.findIndex(t => t[key] === item[key])
            );
        }
        return [...new Set(array)];
    }

    /**
     * Sort array by date
     */
    sortByDate(array, dateKey = 'timestamp', ascending = false) {
        return array.sort((a, b) => {
            const dateA = new Date(a[dateKey]);
            const dateB = new Date(b[dateKey]);
            return ascending ? dateA - dateB : dateB - dateA;
        });
    }

    /**
     * Group array by key
     */
    groupBy(array, key) {
        return array.reduce((groups, item) => {
            const group = item[key];
            groups[group] = groups[group] || [];
            groups[group].push(item);
            return groups;
        }, {});
    }

    // =====================================
    // ERROR UTILITIES
    // =====================================

    /**
     * Safe execute function
     */
    safeExecute(fn, fallback = null) {
        try {
            return fn();
        } catch (error) {
            console.error('Safe execute error:', error);
            return fallback;
        }
    }

    /**
     * Retry function dengan delay
     */
    async retry(fn, maxRetries = 3, delay = 1000) {
        for (let i = 0; i < maxRetries; i++) {
            try {
                return await fn();
            } catch (error) {
                if (i === maxRetries - 1) throw error;
                await this.sleep(delay);
            }
        }
    }

    /**
     * Sleep function
     */
    sleep(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    // =====================================
    // BROWSER UTILITIES
    // =====================================

    /**
     * Check browser support
     */
    getBrowserInfo() {
        const userAgent = navigator.userAgent;
        const isChrome = /Chrome/.test(userAgent);
        const isFirefox = /Firefox/.test(userAgent);
        const isSafari = /Safari/.test(userAgent) && !isChrome;
        const isEdge = /Edge/.test(userAgent);
        const isMobile = /Mobi|Android/i.test(userAgent);
        
        return { isChrome, isFirefox, isSafari, isEdge, isMobile };
    }

    /**
     * Check feature support
     */
    checkFeatureSupport() {
        return {
            localStorage: typeof Storage !== 'undefined',
            camera: !!(navigator.mediaDevices && navigator.mediaDevices.getUserMedia),
            fileAPI: window.File && window.FileReader,
            webWorkers: typeof Worker !== 'undefined'
        };
    }

    /**
     * Copy text to clipboard
     */
    async copyToClipboard(text) {
        try {
            await navigator.clipboard.writeText(text);
            return true;
        } catch (error) {
            console.error('Clipboard error:', error);
            return false;
        }
    }

    // =====================================
    // DEBUG UTILITIES
    // =====================================

    /**
     * Log dengan timestamp
     */
    log(message, type = 'info') {
        const timestamp = new Date().toLocaleTimeString();
        console.log(`[${timestamp}] ${type.toUpperCase()}: ${message}`);
    }

    /**
     * Performance timer
     */
    startTimer(label = 'timer') {
        const start = performance.now();
        return () => {
            const end = performance.now();
            const duration = end - start;
            console.log(`⏱️ ${label}: ${duration.toFixed(2)}ms`);
            return duration;
        };
    }

    /**
     * Get app info
     */
    getAppInfo() {
        return {
            name: this.APP_NAME,
            version: this.APP_VERSION,
            userAgent: navigator.userAgent,
            timestamp: new Date().toISOString(),
            features: this.checkFeatureSupport(),
            browser: this.getBrowserInfo()
        };
    }
}

// Create global instance
const utils = new Utilities();

// Export untuk digunakan di file lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { Utilities, utils };
}

// Export individual functions untuk backward compatibility
const {
    formatFileSize,
    formatDate,
    formatTime,
    validateImageFile,
    generateId,
    saveToStorage,
    loadFromStorage,
    getConfidenceClass,
    formatDetectionSummary,
    safeExecute
} = utils;

// Expose ke window untuk debugging
window.utils = utils;