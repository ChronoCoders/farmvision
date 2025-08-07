// Farm Vision - Mapping and Vegetation Analysis JavaScript
document.addEventListener('DOMContentLoaded', function() {
    
    // Initialize map if container exists
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        initializeMap();
    }
    
    // Vegetation analysis form handling
    const vegetationForm = document.getElementById('vegetationForm');
    if (vegetationForm) {
        vegetationForm.addEventListener('submit', function(e) {
            const fileInput = document.getElementById('image');
            const file = fileInput.files[0];
            
            if (!file) {
                e.preventDefault();
                FarmVision.showNotification('Lütfen bir GeoTIFF dosyası seçin.', 'warning');
                return;
            }
            
            // Validate GeoTIFF file
            if (!file.name.toLowerCase().endsWith('.tif') && !file.name.toLowerCase().endsWith('.tiff')) {
                e.preventDefault();
                FarmVision.showNotification('Lütfen GeoTIFF (.tif/.tiff) formatında dosya seçin.', 'error');
                return;
            }
            
            // Show progress
            showAnalysisProgress();
        });
    }
    
    // Algorithm selection change handler
    const algorithmSelect = document.getElementById('algorithm');
    if (algorithmSelect) {
        algorithmSelect.addEventListener('change', function() {
            updateAlgorithmInfo(this.value);
            updateRangeDefaults(this.value);
        });
    }
    
    // Colormap preview
    const colormapSelect = document.getElementById('colormap');
    if (colormapSelect) {
        colormapSelect.addEventListener('change', function() {
            updateColormapPreview(this.value);
        });
    }
    
    // Analysis result actions
    window.viewAnalysis = function(analysisId) {
        const modal = new bootstrap.Modal(document.getElementById('analysisModal') || createAnalysisModal());
        loadAnalysisDetails(analysisId, modal);
    };
    
    window.downloadAnalysis = function(analysisId) {
        const link = document.createElement('a');
        link.href = `/mapping/download/${analysisId}`;
        link.download = `vegetation_analysis_${analysisId}.tif`;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        
        FarmVision.showNotification('Analiz sonucu indiriliyor...', 'info');
    };
    
    // Range validation
    const minRangeInput = document.getElementById('min_range');
    const maxRangeInput = document.getElementById('max_range');
    
    if (minRangeInput && maxRangeInput) {
        function validateRange() {
            const minVal = parseFloat(minRangeInput.value);
            const maxVal = parseFloat(maxRangeInput.value);
            
            if (minVal >= maxVal) {
                FarmVision.showNotification('Minimum değer maksimum değerden küçük olmalıdır.', 'warning');
                return false;
            }
            return true;
        }
        
        minRangeInput.addEventListener('blur', validateRange);
        maxRangeInput.addEventListener('blur', validateRange);
    }
});

function initializeMap() {
    // Initialize Leaflet map
    const map = L.map('map').setView([39.9334, 32.8597], 6); // Turkey center
    
    // Add tile layers with error handling
    const baseMaps = {};
    
    try {
        baseMaps["OpenStreetMap"] = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors',
            errorTileUrl: '/static/images/map-error-tile.png'
        });
        
        baseMaps["Satellite"] = L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles © Esri',
            errorTileUrl: '/static/images/map-error-tile.png'
        });
        
        baseMaps["Terrain"] = L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenTopoMap contributors',
            errorTileUrl: '/static/images/map-error-tile.png'
        });
    } catch (error) {
        // Production-ready error logging
        if (typeof window.logError === 'function') {
            window.logError('Map layer creation failed', error.message);
        }
        showMapLoadingError('Harita katmanları yüklenemedi.');
        return null;
    }
    
    // Add default layer with error handling
    try {
        baseMaps["OpenStreetMap"].addTo(map);
    } catch (error) {
        // Production-ready error logging
        if (typeof window.logError === 'function') {
            window.logError('Map layer failed to load', error.message);
        }
        showMapLoadingError('Ana harita yüklenemedi. İnternet bağlantınızı kontrol edin.');
        return null;
    }
    
    // Add layer control
    L.control.layers(baseMaps).addTo(map);
    
    // Add scale
    L.control.scale().addTo(map);
    
    // Add measurement tool
    if (typeof L.Control.Measure !== 'undefined') {
        L.control.measure({
            primaryLengthUnit: 'meters',
            primaryAreaUnit: 'sqmeters',
            activeColor: '#198754',
            completedColor: '#198754'
        }).addTo(map);
    }
    
    // Load analysis overlays
    loadAnalysisOverlays(map);
    
    // Store map reference globally
    window.farmVisionMap = map;
    
    return map;
}

// Map error handling function
function showMapLoadingError(message) {
    const mapContainer = document.getElementById('map');
    if (mapContainer) {
        mapContainer.innerHTML = `
            <div class="d-flex align-items-center justify-content-center h-100 bg-light rounded">
                <div class="text-center p-4">
                    <i class="fas fa-exclamation-triangle fa-3x text-warning mb-3"></i>
                    <h5 class="text-muted">Harita Yüklenemedi</h5>
                    <p class="text-muted">${message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">
                        <i class="fas fa-refresh me-2"></i>Tekrar Dene
                    </button>
                </div>
            </div>
        `;
    }
}

function loadAnalysisOverlays(map) {
    // Add loading indicator
    const loadingIndicator = document.createElement('div');
    loadingIndicator.id = 'map-loading';
    loadingIndicator.className = 'map-loading-indicator';
    loadingIndicator.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Analizler yükleniyor...';
    map.getContainer().appendChild(loadingIndicator);
    
    // Load authentic analysis overlays from server with timeout
    const fetchWithTimeout = (url, options = {}, timeout = 10000) => {
        return Promise.race([
            fetch(url, options),
            new Promise((_, reject) => 
                setTimeout(() => reject(new Error('Request timeout')), timeout)
            )
        ]);
    };
    
    fetchWithTimeout('/api/vegetation_analyses')
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .then(data => {
            if (data.analyses && data.analyses.length > 0) {
                const analysisLayers = L.layerGroup();
                let validOverlays = 0;
                
                data.analyses.forEach(analysis => {
                    if (analysis.bounds && analysis.result_path) {
                        try {
                            const overlay = L.imageOverlay(analysis.result_path, analysis.bounds, {
                                opacity: 0.7,
                                title: analysis.algorithm,
                                errorOverlayUrl: '/static/images/overlay-error.png'
                            });
                            
                            overlay.on('load', function() {
                                validOverlays++;
                            });
                            
                            overlay.on('error', function() {
                                // Production-ready error logging
                                if (typeof window.logError === 'function') {
                                    window.logError('Overlay loading failed', analysis.result_path);
                                }
                            });
                            
                            analysisLayers.addLayer(overlay);
                        } catch (overlayError) {
                            // Production-ready error logging
                            if (typeof window.logError === 'function') {
                                window.logError('Overlay creation failed', overlayError.message);
                            }
                        }
                    }
                });
                
                // Add to map if there are valid overlays
                if (analysisLayers.getLayers().length > 0) {
                    const overlayMaps = {
                        "Bitki Örtüsü Analizleri": analysisLayers
                    };
                    L.control.layers(null, overlayMaps).addTo(map);
                    
                    // Show success message
                    setTimeout(() => {
                        if (validOverlays > 0) {
                            FarmVision.showNotification(`${validOverlays} analiz katmanı yüklendi.`, 'success');
                        }
                    }, 2000);
                }
            }
        })
        .catch(error => {
            // Production-ready error handling
            let errorMessage = 'Analiz verileri yüklenemedi.';
            
            if (error.message === 'Request timeout') {
                errorMessage = 'Bağlantı zaman aşımına uğradı. Lütfen tekrar deneyin.';
            } else if (error.name === 'NetworkError' || error.message.includes('fetch')) {
                errorMessage = 'İnternet bağlantınızı kontrol edin ve tekrar deneyin.';
            } else if (error.message.includes('HTTP error')) {
                errorMessage = 'Sunucu hatası. Lütfen daha sonra tekrar deneyin.';
            }
            
            FarmVision.showNotification(errorMessage, 'warning');
            
            // Production error logging
            if (typeof window.logError === 'function') {
                window.logError('Overlay loading failed', {
                    error: error.message,
                    url: '/api/vegetation_analyses',
                    timestamp: new Date().toISOString()
                });
            }
        })
        .finally(() => {
            // Remove loading indicator
            const loadingEl = document.getElementById('map-loading');
            if (loadingEl) {
                loadingEl.remove();
            }
        });
}

function showAnalysisProgress() {
    const progressContainer = document.getElementById('progressContainer');
    const submitBtn = document.querySelector('button[type="submit"]');
    
    if (progressContainer) {
        progressContainer.style.display = 'block';
    }
    
    if (submitBtn) {
        const restoreButton = FarmVision.showLoadingSpinner(submitBtn);
        window.restoreSubmitButton = restoreButton;
    }
}

function updateAlgorithmInfo(algorithm) {
    const algorithmDescriptions = {
        'ndvi': {
            title: 'NDVI - Normalized Difference Vegetation Index',
            description: 'Yeşil bitki örtüsü miktarını ölçer. Sağlıklı bitkiler yüksek NDVI değerine sahiptir.',
            range: '(-1, 1)',
            interpretation: 'Yüksek değerler sağlıklı bitki örtüsünü, düşük değerler su, toprak veya yapılaşmış alanları gösterir.'
        },
        'gli': {
            title: 'GLI - Green Leaf Index',
            description: 'Yeşil yaprak ve gövdeleri vurgular.',
            range: '(-1, 1)',
            interpretation: 'Bitki yoğunluğunun belirlenmesinde kullanılır.'
        },
        'vari': {
            title: 'VARI - Visual Atmospheric Resistance Index',
            description: 'Bitki örtüsü alanlarını atmosferik etkilerden bağımsız olarak gösterir.',
            range: '(-1, 1)',
            interpretation: 'Atmosferik koşulların etkisini minimize eder.'
        },
        'endvi': {
            title: 'ENDVI - Enhanced NDVI',
            description: 'NDVI\'nin geliştirilmiş versiyonu.',
            range: '(-1, 1)',
            interpretation: 'Mavi ve yeşil bantları kullanarak bitki sağlığını analiz eder.'
        },
        'ndwi': {
            title: 'NDWI - Normalized Difference Water Index',
            description: 'Su kütlelerindeki su içeriği miktarını gösterir.',
            range: '(-1, 1)',
            interpretation: 'Su stresi tespitinde kullanılır.'
        }
    };
    
    const infoDiv = document.getElementById('algorithmInfo');
    if (infoDiv && algorithmDescriptions[algorithm]) {
        const info = algorithmDescriptions[algorithm];
        infoDiv.innerHTML = `
            <h6>${info.title}</h6>
            <p class="small text-muted mb-2">${info.description}</p>
            <div class="small">
                <strong>Değer Aralığı:</strong> ${info.range}<br>
                <strong>Yorumlama:</strong> ${info.interpretation}
            </div>
        `;
    }
}

function updateRangeDefaults(algorithm) {
    const minRangeInput = document.getElementById('min_range');
    const maxRangeInput = document.getElementById('max_range');
    
    const defaults = {
        'ndvi': { min: -1.0, max: 1.0 },
        'gli': { min: -1.0, max: 1.0 },
        'vari': { min: -1.0, max: 1.0 },
        'endvi': { min: -1.0, max: 1.0 },
        'ndwi': { min: -1.0, max: 1.0 },
        'exg': { min: -255, max: 255 },
        'tgi': { min: -255, max: 255 },
        'bai': { min: 0, max: 100 },
        'vndvi': { min: 0, max: 2 }
    };
    
    if (defaults[algorithm]) {
        minRangeInput.value = defaults[algorithm].min;
        maxRangeInput.value = defaults[algorithm].max;
    }
}

function updateColormapPreview(colormap) {
    const previewDiv = document.getElementById('colormapPreview');
    if (!previewDiv) {
        // Create preview div if it doesn't exist
        const colormapContainer = document.getElementById('colormap').parentNode;
        const newPreview = document.createElement('div');
        newPreview.id = 'colormapPreview';
        newPreview.className = 'mt-2';
        colormapContainer.appendChild(newPreview);
    }
    
    // Create colormap gradient preview
    const gradients = {
        'rdylgn': 'linear-gradient(to right, #d73027, #f46d43, #fdae61, #fee08b, #ffffbf, #d9ef8b, #a6d96a, #66bd63, #1a9850)',
        'spectral': 'linear-gradient(to right, #9e0142, #d53e4f, #f46d43, #fdae61, #fee08b, #e6f598, #abdda4, #66c2a5, #3288bd, #5e4fa2)',
        'viridis': 'linear-gradient(to right, #440154, #482777, #3f4a8a, #31678e, #26838f, #1f9d8a, #6cce5a, #b6de2b, #fee825)',
        'plasma': 'linear-gradient(to right, #0d0887, #6a00a8, #b12a90, #e16462, #fca636, #f0f921)',
        'inferno': 'linear-gradient(to right, #000004, #420a68, #932667, #dd513a, #fca50a, #fcffa4)',
        'jet': 'linear-gradient(to right, #000080, #0000ff, #00ffff, #ffff00, #ff0000, #800000)'
    };
    
    if (gradients[colormap]) {
        document.getElementById('colormapPreview').innerHTML = `
            <div style="height: 20px; background: ${gradients[colormap]}; border-radius: 5px; border: 1px solid #ddd;"></div>
            <small class="text-muted">Renk haritası önizleme</small>
        `;
    }
}

function createAnalysisModal() {
    const modal = document.createElement('div');
    modal.className = 'modal fade';
    modal.id = 'analysisModal';
    modal.innerHTML = `
        <div class="modal-dialog modal-xl">
            <div class="modal-content">
                <div class="modal-header">
                    <h5 class="modal-title">Bitki Örtüsü Analiz Detayları</h5>
                    <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                </div>
                <div class="modal-body">
                    <div id="analysisModalContent">
                        <div class="text-center">
                            <i class="fas fa-spinner fa-spin fa-2x"></i>
                            <p class="mt-2">Yükleniyor...</p>
                        </div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Kapat</button>
                    <button type="button" class="btn btn-primary" onclick="downloadAnalysis()">
                        <i class="fas fa-download me-2"></i>İndir
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
    return modal;
}

function loadAnalysisDetails(analysisId, modal) {
    const contentDiv = document.getElementById('analysisModalContent');
    
    // Fetch real analysis data from server
    fetch(`/api/analysis/${analysisId}`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                contentDiv.innerHTML = `
                    <div class="row">
                        <div class="col-md-8">
                            <div class="text-center">
                                <img src="${data.result_path}" class="img-fluid rounded shadow" alt="Analiz Sonucu"
                                     onerror="this.src='/static/images/no-image.jpg'" style="max-height: 500px;">
                            </div>
                        </div>
                        <div class="col-md-4">
                            <h6>Analiz Bilgileri</h6>
                            <table class="table table-borderless table-sm">
                                <tr>
                                    <td><strong>ID:</strong></td>
                                    <td>${data.id}</td>
                                </tr>
                                <tr>
                                    <td><strong>Algoritma:</strong></td>
                                    <td><span class="badge bg-success">${data.algorithm.toUpperCase()}</span></td>
                                </tr>
                                <tr>
                                    <td><strong>Renk Haritası:</strong></td>
                                    <td>${data.colormap}</td>
                                </tr>
                                <tr>
                                    <td><strong>Değer Aralığı:</strong></td>
                                    <td>${data.min_range} - ${data.max_range}</td>
                                </tr>
                                <tr>
                                    <td><strong>Tarih:</strong></td>
                                    <td>${new Date(data.created_at).toLocaleDateString('tr-TR')}</td>
                                </tr>
                            </table>
                            
                            <hr>
                            
                            <h6>İstatistikler</h6>
                            ${data.has_valid_statistics ? `
                            <div class="small">
                                <div class="d-flex justify-content-between">
                                    <span>Ortalama:</span>
                                    <span class="text-success fw-bold">${data.statistics.mean.toFixed(3)}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Standart Sapma:</span>
                                    <span>${data.statistics.std.toFixed(3)}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Medyan:</span>
                                    <span>${data.statistics.median.toFixed(3)}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Minimum:</span>
                                    <span class="text-primary">${data.statistics.min.toFixed(3)}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Maksimum:</span>
                                    <span class="text-warning">${data.statistics.max.toFixed(3)}</span>
                                </div>
                                <hr class="my-2">
                                <div class="d-flex justify-content-between">
                                    <span>Geçerli Piksel:</span>
                                    <span>${data.statistics.pixel_count.toLocaleString('tr-TR')}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Toplam Piksel:</span>
                                    <span>${data.statistics.total_pixels.toLocaleString('tr-TR')}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Veri Oranı:</span>
                                    <span class="text-info">${((data.statistics.pixel_count / data.statistics.total_pixels) * 100).toFixed(1)}%</span>
                                </div>
                            </div>
                            ` : `
                            <div class="text-center text-muted">
                                <i class="fas fa-info-circle me-2"></i>
                                İstatistik hesaplaması için geçerli GeoTIFF verisi bulunamadı.
                                <br><small>Sadece gerçek spektral analiz sonuçları gösterilir.</small>
                            </div>
                            `}
                        </div>
                    </div>
                `;
                modal.show();
            } else {
                contentDiv.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-triangle me-2"></i>
                        Analiz detayları yüklenemedi: ${data.error || 'Bilinmeyen hata'}
                    </div>
                `;
            }
        })
        .catch(error => {
            console.error('Analysis details load error:', error);
            contentDiv.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    Analiz detayları yüklenirken hata oluştu.
                </div>
            `;
        });
}

// Export functions
window.MappingJS = {
    initializeMap,
    updateAlgorithmInfo,
    updateRangeDefaults,
    updateColormapPreview,
    showAnalysisProgress
};
