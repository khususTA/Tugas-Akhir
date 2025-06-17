/**
 * JAGAPADI v2.2 - Image Handler Module
 * Mengelola semua fungsi yang berhubungan dengan file gambar:
 * - Upload file gambar
 * - Preview gambar
 * - Validasi file
 * - Konversi format
 * - Drag & drop
 */

class ImageHandler {
    constructor(app) {
        this.app = app; // Reference ke aplikasi utama
        this.currentFile = null;
        this.selectedBase64 = null;
        this.maxFileSize = 10 * 1024 * 1024; // 10MB
        this.allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/gif', 'image/webp'];
        
        console.log('📷 Image Handler initialized');
        this.initializeFileInput();
    }

    /**
     * Inisialisasi event listener untuk file input
     */
    initializeFileInput() {
        const fileInput = this.app.elements.fileInput;
        if (fileInput) {
            fileInput.addEventListener('change', (e) => {
                if (e.target.files && e.target.files[0]) {
                    this.handleFileSelect(e.target.files[0]);
                }
            });
        }
    }



    /**
     * Menangani aksi file picker
     */
    handleFileAction() {
        if (!this.app.connectionManager.isConnected) {
            this.app.showNotification('Hubungkan ke server terlebih dahulu', 'warning');
            return;
        }

        // Trigger file input
        const fileInput = this.app.elements.fileInput;
        if (fileInput) {
            fileInput.click();
        }
    }

    /**
     * Menangani perubahan gambar - reset ke kondisi awal
     */
    handleChangeImage() {
        this.currentFile = null;
        this.selectedBase64 = null;
        
        // Reset preview image
        const previewImage = this.app.elements.previewImage;
        if (previewImage) {
            previewImage.src = '';
        }

        // Kembali ke state initial
        this.app.setState('initial');

        // Tutup sidebar di mobile
        if (window.innerWidth <= 768) {
            this.app.uiManager.closeSidebar();
        }

        this.app.showNotification('Gambar dihapus', 'info');
    }

    /**
     * Menangani pemilihan file dari file picker
     */
    handleFileSelect(file) {
        if (!file) {
            console.log('⚠️ No file selected');
            return;
        }

        console.log(`📁 File selected: ${file.name} (${this.formatFileSize(file.size)})`);

        // Validasi file
        const validation = this.validateFile(file);
        if (!validation.isValid) {
            this.app.showNotification(validation.message, 'error');
            return;
        }

        // Set current file dan load preview
        this.currentFile = file;
        this.loadImagePreview(file);

        // Tutup sidebar di mobile
        if (window.innerWidth <= 768) {
            this.app.uiManager.closeSidebar();
        }
    }

    /**
     * Validasi file yang dipilih
     */
    validateFile(file) {
        // Cek apakah file adalah gambar
        if (!file.type.startsWith('image/')) {
            return {
                isValid: false,
                message: 'File yang dipilih bukan gambar. Pilih file JPG, PNG, atau format gambar lainnya.'
            };
        }

        // Cek tipe file yang diizinkan
        if (!this.allowedTypes.includes(file.type)) {
            return {
                isValid: false,
                message: `Format file ${file.type} tidak didukung. Gunakan JPG, PNG, GIF, atau WebP.`
            };
        }

        // Cek ukuran file
        if (file.size > this.maxFileSize) {
            return {
                isValid: false,
                message: `Ukuran file terlalu besar (${this.formatFileSize(file.size)}). Maksimal ${this.formatFileSize(this.maxFileSize)}.`
            };
        }

        // Cek ukuran file minimum (1KB)
        if (file.size < 1024) {
            return {
                isValid: false,
                message: 'File terlalu kecil. Pilih gambar yang valid.'
            };
        }

        return {
            isValid: true,
            message: 'File valid'
        };
    }

    /**
     * Memuat preview gambar yang dipilih
     */
    loadImagePreview(file) {
        const reader = new FileReader();

        reader.onload = (e) => {
            this.selectedBase64 = e.target.result;
            
            // Update preview image
            const previewImage = this.app.elements.previewImage;
            if (previewImage) {
                previewImage.onload = () => {
                    // Pindah ke state imageReady setelah gambar berhasil dimuat
                    this.app.setState('imageReady');
                    console.log('✅ Image preview loaded successfully');
                };
                
                previewImage.onerror = () => {
                    console.error('❌ Failed to load image preview');
                    this.app.showNotification('Gagal memuat preview gambar', 'error');
                    this.app.setState('initial');
                };
                
                previewImage.src = e.target.result;
            }

            this.app.showNotification(`Gambar ${file.name} berhasil dimuat`, 'success');
        };

        reader.onerror = () => {
            console.error('❌ FileReader error');
            this.app.showNotification('Gagal membaca file gambar', 'error');
            this.app.setState('initial');
        };

        reader.readAsDataURL(file);
    }

    /**
     * Membuat file object dari base64 (untuk hasil kamera)
     */
    createFileFromBase64(base64Data, filename) {
        // Konversi base64 ke blob
        const byteCharacters = atob(base64Data.split(',')[1]);
        const byteNumbers = new Array(byteCharacters.length);
        
        for (let i = 0; i < byteCharacters.length; i++) {
            byteNumbers[i] = byteCharacters.charCodeAt(i);
        }
        
        const byteArray = new Uint8Array(byteNumbers);
        const blob = new Blob([byteArray], { type: 'image/jpeg' });
        
        // Buat file object
        const file = new File([blob], filename, { type: 'image/jpeg' });
        
        // Set sebagai current file dan load preview
        this.currentFile = file;
        this.selectedBase64 = base64Data;
        
        // Update preview
        const previewImage = this.app.elements.previewImage;
        if (previewImage) {
            previewImage.onload = () => {
                this.app.setState('imageReady');
            };
            previewImage.src = base64Data;
        }
    }

    /**
     * Mendapatkan informasi file saat ini
     */
    getCurrentFileInfo() {
        if (!this.currentFile) {
            return null;
        }

        return {
            name: this.currentFile.name,
            size: this.currentFile.size,
            type: this.currentFile.type,
            lastModified: this.currentFile.lastModified,
            formattedSize: this.formatFileSize(this.currentFile.size),
            base64: this.selectedBase64
        };
    }

    /**
     * Cek apakah ada gambar yang siap diproses
     */
    hasImageReady() {
        return !!(this.currentFile && this.selectedBase64);
    }

    /**
     * Mendapatkan data base64 gambar saat ini
     */
    getImageBase64() {
        return this.selectedBase64;
    }

    /**
     * Mendapatkan file saat ini
     */
    getCurrentFile() {
        return this.currentFile;
    }

    /**
     * Reset semua data gambar
     */
    resetImageData() {
        this.currentFile = null;
        this.selectedBase64 = null;
        
        // Reset file input
        const fileInput = this.app.elements.fileInput;
        if (fileInput) {
            fileInput.value = '';
        }

        // Reset preview
        const previewImage = this.app.elements.previewImage;
        if (previewImage) {
            previewImage.src = '';
        }
    }

    /**
     * Mengubah gambar hasil deteksi (dipanggil dari backend)
     */
    updateResultImage(base64Data) {
        const previewImage = this.app.elements.previewImage;
        if (previewImage && base64Data) {
            previewImage.src = base64Data;
            console.log('🖼️ Result image updated');
        }
    }

    /**
     * Validasi kualitas gambar untuk deteksi
     */
    validateImageQuality() {
        if (!this.currentFile) {
            return {
                isValid: false,
                message: 'Tidak ada gambar yang dipilih'
            };
        }

        // Cek resolusi minimum (akan diimplementasi jika diperlukan)
        // const img = new Image();
        // img.onload = () => {
        //     if (img.width < 224 || img.height < 224) {
        //         return { isValid: false, message: 'Resolusi gambar terlalu kecil (minimal 224x224)' };
        //     }
        // };

        return {
            isValid: true,
            message: 'Gambar siap untuk diproses'
        };
    }

    /**
     * Format ukuran file menjadi string yang mudah dibaca
     */
    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    /**
     * Kompresi gambar jika terlalu besar
     */
    compressImage(file, maxWidth = 1024, quality = 0.8) {
        return new Promise((resolve) => {
            const canvas = document.createElement('canvas');
            const ctx = canvas.getContext('2d');
            const img = new Image();

            img.onload = () => {
                // Hitung ukuran baru dengan mempertahankan aspect ratio
                let { width, height } = img;
                
                if (width > maxWidth) {
                    height = (height * maxWidth) / width;
                    width = maxWidth;
                }

                canvas.width = width;
                canvas.height = height;

                // Gambar ke canvas dengan ukuran baru
                ctx.drawImage(img, 0, 0, width, height);

                // Konversi ke base64 dengan kualitas tertentu
                const compressedBase64 = canvas.toDataURL('image/jpeg', quality);
                
                resolve(compressedBase64);
            };

            img.src = URL.createObjectURL(file);
        });
    }

    /**
     * Setup drag and drop untuk area preview
     */
    setupDragAndDrop() {
        const previewContainer = this.app.elements.previewContainer;
        if (!previewContainer) return;

        // Prevent default drag behaviors
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            previewContainer.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        // Highlight drop area
        ['dragenter', 'dragover'].forEach(eventName => {
            previewContainer.addEventListener(eventName, () => {
                previewContainer.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            previewContainer.addEventListener(eventName, () => {
                previewContainer.classList.remove('drag-over');
            });
        });

        // Handle drop
        previewContainer.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                this.handleFileSelect(files[0]);
            }
        });
    }
}

// Export untuk digunakan di file lain
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ImageHandler;
}