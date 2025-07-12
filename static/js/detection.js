// Farm Vision - Detection JavaScript Functions
document.addEventListener('DOMContentLoaded', function() {
    
    // Fruit detection form handling
    const fruitForm = document.getElementById('fruitDetectionForm');
    if (fruitForm) {
        fruitForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('image');
            const file = fileInput.files[0];
            
            if (!file) {
                e.preventDefault();
                FarmVision.showNotification('Lütfen bir görüntü dosyası seçin.', 'warning');
                return;
            }
            
            // Validate file type
            const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png'];
            if (!allowedTypes.includes(file.type)) {
                e.preventDefault();
                FarmVision.showNotification('Desteklenmeyen dosya formatı. Lütfen JPG, JPEG veya PNG dosyası seçin.', 'error');
                return;
            }
            
            // Validate file size (100MB)
            const maxSize = 100 * 1024 * 1024;
            if (file.size > maxSize) {
                e.preventDefault();
                FarmVision.showNotification('Dosya boyutu çok büyük. Maksimum 100MB olabilir.', 'error');
                return;
            }
            
            // Show progress
            showDetectionProgress();
        });
    }
    
    // Leaf detection form handling
    const leafForm = document.getElementById('leafDetectionForm');
    if (leafForm) {
        leafForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('image');
            const file = fileInput.files[0];
            
            if (!file) {
                e.preventDefault();
                FarmVision.showNotification('Lütfen bir yaprak görüntüsü seçin.', 'warning');
                return;
            }
            
            // Show progress
            showDetectionProgress();
        });
    }
    
    // Tree detection form handling
    const treeForm = document.getElementById('treeDetectionForm');
    if (treeForm) {
        treeForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('image');
            const file = fileInput.files[0];
            
            if (!file) {
                e.preventDefault();
                FarmVision.showNotification('Lütfen bir görüntü dosyası seçin.', 'warning');
                return;
            }
            
            // Show progress
            showDetectionProgress();
        });
    }
    
    // Image preview functionality
    const imageInputs = document.querySelectorAll('input[type="file"][accept*="image"]');
    imageInputs.forEach(function(input) {
        input.addEventListener('change', function(e) {
            const file = e.target.files[0];
            if (file) {
                createImagePreview(file, input);
                showFileInfo(file, input);
            }
        });
    });
    
    // Detection result actions
    window.viewDetection = function(detectionId) {
        // Implementation for viewing detection details
        const modal = new bootstrap.Modal(document.getElementById('detectionModal') || createDetectionModal());
        loadDetectionDetails(detectionId, modal);
    };
    
    window.downloadResult = function(detectionId) {
        // Implementation for downloading detection result
        const link = document.createElement('a');
        link.href = `/detection/download/${detectionId}`;
        link.download = `detection_result_${detectionId}.jpg`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        FarmVision.showNotification('Dosya indiriliyor...', 'info');
    };
    
    window.deleteDetection = function(detectionId) {
        if (confirm('Bu tespit sonucunu silmek istediğinizden emin misiniz?')) {
            fetch(`/detection/delete/${detectionId}`, {
                method: 'DELETE',
                headers: {
                    'Content-Type': 'application/json',
                }
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    FarmVision.showNotification('Tespit sonucu silindi.', 'success');
                    // Remove row from table
                    const row = document.querySelector(`tr[data-detection-id="${detectionId}"]`);
                    if (row) row.remove();
                } else {
                    FarmVision.showNotification('Silme işlemi başarısız oldu.', 'error');
                }
            })
            .catch(error => {
                console.error('Error:', error);
                FarmVision.showNotification('Bir hata oluştu.', 'error');
            });
        }
    };
});

function showDetectionProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const submitBtn = document.querySelector('button[type="submit"]');
    
    if (progressContainer) {
        progressContainer.style.display = 'block';
    }
    
    if (submitBtn) {
        const restoreButton = FarmVision.showLoadingSpinner(submitBtn);
        
        // Store restore function for potential error handling
        window.restoreSubmitButton = restoreButton;
    }
}

function createImagePreview(file, input) {
    const reader = new FileReader();
    reader.onload = function(e) {
        let previewContainer = input.parentNode.querySelector('.image-preview');
        
        if (!previewContainer) {
            previewContainer = document.createElement('div');
            previewContainer.className = 'image-preview mt-3 text-center';
            input.parentNode.appendChild(previewContainer);
        }
        
        previewContainer.innerHTML = `
            <div class="card" style="max-width: 300px; margin: 0 auto;">
                <img src="${e.target.result}" class="card-img-top" alt="Önizleme" style="height: 200px; object-fit: cover;">
                <div class="card-body">
                    <small class="text-muted">Dosya: ${file.name}</small><br>
                    <small class="text-muted">Boyut: ${FarmVision.formatFileSize(file.size)}</small>
                </div>
            </div>
        `;
    };
    reader.readAsDataURL(file);
}

function showFileInfo(file, input) {
    let infoContainer = input.parentNode.querySelector('.file-info');
    
    if (!infoContainer) {
        infoContainer = document.createElement('div');
        infoContainer.className = 'file-info mt-2';
        input.parentNode.appendChild(infoContainer);
    }
    
    const fileType = file.type.split('/')[1].toUpperCase();
    const fileSize = FarmVision.formatFileSize(file.size);
    
    infoContainer.innerHTML = `
        <div class="d-flex justify-content-between align-items-center p-2 bg-light rounded">
            <div>
                <i class="fas fa-image text-primary me-2"></i>
                <strong>${file.name}</strong>
            </div>
            <div class="text-end">
                <span class="badge bg-secondary">${fileType}</span>
                <small class="text-muted ms-2">${fileSize}</small>
            </div>
        </div>
    `;
}

function createDetectionModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'detectionModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-lg">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Tespit Detayları</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="detectionModalContent">
                        <div class="text-center">
                            <i class="fas fa-spinner fa-spin fa-2x"></i>
                            <p class="mt-2">Yükleniyor...</p>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Kapat</button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function loadDetectionDetails(detectionId, modal) {
    const contentDiv = document.getElementById('detectionModalContent');
    
    // Fetch real detection data from server
    fetch(`/api/detection/${detectionId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                contentDiv.innerHTML = `
                    <div class="row">
                        <div class="col-md-6">
                            <img src="${data.image_path}" class="img-fluid rounded" alt="Tespit Sonucu" 
                                 onerror="this.src='/static/images/no-image.jpg'">
                        </div>
                        <div class="col-md-6">
                            <table class="table table-borderless">
                                <tr>
                                    <td><strong>Tespit ID:</strong></td>
                                    <td>${data.id}</td>
                                </tr>
                                <tr>
                                    <td><strong>Tür:</strong></td>
                                    <td>${data.detection_type}</td>
                                </tr>
                                <tr>
                                    <td><strong>Sonuç:</strong></td>
                                    <td>${data.count} adet ${data.fruit_type || 'tespit'}</td>
                                </tr>
                                <tr>
                                    <td><strong>Güven:</strong></td>
                                    <td>${data.confidence}%</td>
                                </tr>
                                <tr>
                                    <td><strong>Tarih:</strong></td>
                                    <td>${new Date(data.created_at).toLocaleDateString('tr-TR')}</td>
                                </tr>
                            </table>
                        </div>
                    </div>
                `;
                modal.show();
            } else {
                contentDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Tespit detayları yüklenemedi: ${data.error || 'Bilinmeyen hata'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Detection details load error:', error);
            contentDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Tespit detayları yüklenirken hata oluştu.
                </div>
            `;
        });
}

// Batch processing functionality
function processBatchImages() {
    const fileInput = document.getElementById('batchImages');
    const files = fileInput.files;
    
    if (files.length === 0) {
        FarmVision.showNotification('Lütfen en az bir görüntü seçin.', 'warning');
        return;
    }
    
    const batchProgress = document.getElementById('batchProgress');
    const progressBar = batchProgress.querySelector('.progress-bar');
    
    batchProgress.style.display = 'block';
    
    let processed = 0;
    const total = files.length;
    
    // Process files through real API
    const formData = new FormData();
    Array.from(files).forEach(file => {
        formData.append('images', file);
    });
    
    fetch('/api/detection/batch', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            progressBar.style.width = '100%';
            progressBar.textContent = `${data.processed_count}/${total} işlendi`;
            FarmVision.showNotification(`${data.processed_count} görüntü başarıyla işlendi.`, 'success');
            
            setTimeout(() => {
                batchProgress.style.display = 'none';
                progressBar.style.width = '0%';
                // Refresh results if needed
                if (typeof loadDetectionResults === 'function') {
                    loadDetectionResults();
                }
            }, 2000);
        } else {
            throw new Error(data.error || 'Batch processing failed');
        }
    })
    .catch(error => {
        console.error('Batch processing error:', error);
        FarmVision.showNotification('Toplu işleme sırasında hata oluştu.', 'error');
        batchProgress.style.display = 'none';
    });
}

// Export functions
window.DetectionJS = {
    processBatchImages,
    createImagePreview,
    showFileInfo,
    showDetectionProgress
};
