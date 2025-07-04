import os
import numpy as np
import cv2
from PIL import Image

class VegetationAnalyzer:
    """
    Vegetation analysis algorithms for multispectral imagery
    """
    
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = None
        self.load_image()
    
    def load_image(self):
        """Load and prepare image for analysis"""
        try:
            # For mock implementation, load as regular image
            # In real implementation, you would use rasterio for GeoTIFF
            self.image = cv2.imread(self.image_path)
            if self.image is None:
                raise ValueError("Görüntü yüklenemedi")
        except Exception as e:
            raise Exception(f"Görüntü yükleme hatası: {str(e)}")
    
    def analyze(self, algorithm, ranges=(-1, 1), colormap='rdylgn'):
        """
        Perform vegetation analysis using specified algorithm
        """
        try:
            # Get the analysis function
            analysis_func = getattr(self, f'calculate_{algorithm}', None)
            if not analysis_func:
                raise ValueError(f"Desteklenmeyen algoritma: {algorithm}")
            
            # Calculate vegetation index
            result_array = analysis_func()
            
            # Apply color mapping and save result
            result_path = self.apply_colormap_and_save(result_array, algorithm, colormap, ranges)
            
            return {
                'path': result_path,
                'algorithm': algorithm,
                'colormap': colormap,
                'ranges': ranges
            }
            
        except Exception as e:
            raise Exception(f"Vegetation analizi hatası: {str(e)}")
    
    def calculate_ndvi(self):
        """Calculate NDVI (Normalized Difference Vegetation Index)"""
        # Mock NDVI calculation using RGB channels
        # In real implementation, you would use NIR and Red bands
        b, g, r = cv2.split(self.image.astype(np.float32))
        
        # Mock NDVI using green and red channels
        ndvi = (g - r) / (g + r + 1e-8)
        return np.clip(ndvi, -1, 1)
    
    def calculate_gli(self):
        """Calculate GLI (Green Leaf Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        gli = ((g * 2) - r - b) / ((g * 2) + r + b + 1e-8)
        return np.clip(gli, -1, 1)
    
    def calculate_vari(self):
        """Calculate VARI (Visual Atmospheric Resistance Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        vari = (g - r) / (g + r - b + 1e-8)
        return np.clip(vari, -1, 1)
    
    def calculate_ndyi(self):
        """Calculate NDYI (Normalized Difference Yellowness Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        ndyi = (g - b) / (g + b + 1e-8)
        return np.clip(ndyi, -1, 1)
    
    def calculate_ndre(self):
        """Calculate NDRE (Normalized Difference Red Edge Index)"""
        # Mock implementation using available channels
        b, g, r = cv2.split(self.image.astype(np.float32))
        ndre = (g - r) / (g + r + 1e-8)
        return np.clip(ndre, -1, 1)
    
    def calculate_ndwi(self):
        """Calculate NDWI (Normalized Difference Water Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        ndwi = (g - r) / (g + r + 1e-8)
        return np.clip(ndwi, -1, 1)
    
    def calculate_ndvi_blue(self):
        """Calculate Blue-based NDVI"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        ndvi_blue = (g - b) / (g + b + 1e-8)
        return np.clip(ndvi_blue, -1, 1)
    
    def calculate_endvi(self):
        """Calculate ENDVI (Enhanced NDVI)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        endvi = ((g + r) - (2 * b)) / ((g + r) + (2 * b) + 1e-8)
        return np.clip(endvi, -1, 1)
    
    def calculate_vndvi(self):
        """Calculate visible NDVI"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        vndvi = 0.5268 * ((r ** -0.1294) * (g ** 0.3389) * (b ** -0.3118))
        return np.clip(vndvi, 0, 2)
    
    def calculate_mpri(self):
        """Calculate MPRI (Modified Photochemical Reflectance Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        mpri = (g - r) / (g + r + 1e-8)
        return np.clip(mpri, -1, 1)
    
    def calculate_exg(self):
        """Calculate EXG (Excess Green Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        exg = (2 * g) - (r + b)
        return np.clip(exg, -255, 255)
    
    def calculate_tgi(self):
        """Calculate TGI (Triangular Greenness Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        tgi = (g - 0.39 * r - 0.61 * b)
        return np.clip(tgi, -255, 255)
    
    def calculate_bai(self):
        """Calculate BAI (Burn Area Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        # Mock BAI calculation
        bai = 1.0 / ((0.1 - r)**2 + (0.06 - g)**2 + 1e-8)
        return np.clip(bai, 0, 100)
    
    def calculate_gndvi(self):
        """Calculate GNDVI (Green NDVI)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        gndvi = (g - r) / (g + r + 1e-8)
        return np.clip(gndvi, -1, 1)
    
    def calculate_savi(self):
        """Calculate SAVI (Soil Adjusted Vegetation Index)"""
        b, g, r = cv2.split(self.image.astype(np.float32))
        L = 0.5  # soil adjustment factor
        savi = ((g - r) / (g + r + L)) * (1 + L)
        return np.clip(savi, -1, 1)
    
    def apply_colormap_and_save(self, data, algorithm, colormap, ranges):
        """Apply colormap and save the result"""
        try:
            # Normalize data to 0-255 range
            min_val, max_val = ranges
            normalized = ((data - min_val) / (max_val - min_val) * 255).astype(np.uint8)
            
            # Apply colormap
            colormap_dict = {
                'rdylgn': cv2.COLORMAP_RdYlGn if hasattr(cv2, 'COLORMAP_RdYlGn') else cv2.COLORMAP_JET,
                'spectral': cv2.COLORMAP_JET,
                'viridis': cv2.COLORMAP_VIRIDIS,
                'plasma': cv2.COLORMAP_PLASMA,
                'inferno': cv2.COLORMAP_INFERNO,
                'magma': cv2.COLORMAP_MAGMA,
                'jet': cv2.COLORMAP_JET,
                'terrain': cv2.COLORMAP_JET
            }
            
            cv_colormap = colormap_dict.get(colormap, cv2.COLORMAP_JET)
            colored_image = cv2.applyColorMap(normalized, cv_colormap)
            
            # Save result
            result_filename = f"vegetation_{algorithm}_{colormap}_{int(np.random.rand() * 10000)}.png"
            result_path = f"static/results/{result_filename}"
            os.makedirs(os.path.dirname(result_path), exist_ok=True)
            
            cv2.imwrite(result_path, colored_image)
            
            return result_path
            
        except Exception as e:
            raise Exception(f"Renk haritası uygulama hatası: {str(e)}")
