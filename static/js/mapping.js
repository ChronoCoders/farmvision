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
    
    // Add tile layers
    const baseMaps = {
        "OpenStreetMap": L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenStreetMap contributors'
        }),
        "Satellite": L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}', {
            attribution: 'Tiles © Esri'
        }),
        "Terrain": L.tileLayer('https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', {
            attribution: '© OpenTopoMap contributors'
        })
    };
    
    // Add default layer
    baseMaps["OpenStreetMap"].addTo(map);
    
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
}

function loadAnalysisOverlays(map) {
    // Mock analysis overlays - in real app, load from server
    const analysisLayers = L.layerGroup();
    
    // Add sample vegetation analysis overlay
    const sampleBounds = [[39.8, 32.7], [40.1, 33.0]];
    const sampleOverlay = L.imageOverlay('/static/images/sample_ndvi.png', sampleBounds, {
        opacity: 0.7
    });
    
    analysisLayers.addLayer(sampleOverlay);
    
    // Add to map
    map.addLayer(analysisLayers);
    
    // Add to layer control
    const overlayMaps = {
        "Vegetation Analysis": analysisLayers
    };
    
    L.control.layers(null, overlayMaps).addTo(map);
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
                            <div class="small">
                                <div class="d-flex justify-content-between">
                                    <span>Ortalama:</span>
                                    <span>${data.statistics?.mean?.toFixed(3) || 'N/A'}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Standart Sapma:</span>
                                    <span>${data.statistics?.std?.toFixed(3) || 'N/A'}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Minimum:</span>
                                    <span>${data.statistics?.min?.toFixed(3) || 'N/A'}</span>
                                </div>
                                <div class="d-flex justify-content-between">
                                    <span>Maksimum:</span>
                                    <span>${data.statistics?.max?.toFixed(3) || 'N/A'}</span>
                                </div>
                            </div>
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
