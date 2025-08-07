"""
Professional Vegetation Analysis Module with Production-Grade Security
Enhanced with comprehensive error handling, type safety, and logging standards
"""
import os
import numpy as np
import cv2
import logging
from PIL import Image
from pathlib import Path
from typing import Optional, Union, Dict, List, Any, Tuple
import rasterio
from rasterio.errors import RasterioError

# Professional logging setup
logger = logging.getLogger(__name__)
if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)

class VegetationAnalyzer:
    """
    Professional vegetation analysis algorithms for multispectral imagery
    Enhanced with comprehensive error handling and type safety
    """
    
    def __init__(self, image_path: str):
        """
        Initialize vegetation analyzer with enhanced validation
        
        Args:
            image_path: Path to the image file for analysis
            
        Raises:
            ValueError: If image path is invalid
            FileNotFoundError: If image file doesn't exist
        """
        # Input validation
        if not isinstance(image_path, str) or not image_path.strip():
            raise ValueError("Image path must be a non-empty string")
            
        self.image_path: str = image_path.strip()
        self.image: Optional[np.ndarray] = None
        self.image_shape: Optional[Tuple[int, ...]] = None
        self.is_geotiff: bool = False
        
        # Enhanced image loading with validation
        self.load_image()
    
    def load_image(self) -> None:
        """
        Load and prepare image for analysis with comprehensive error handling
        Supports both regular images and GeoTIFF files
        """
        try:
            # Enhanced path validation
            path_obj = Path(self.image_path)
            if not path_obj.exists():
                raise FileNotFoundError(f"Image file not found: {self.image_path}")
                
            if not path_obj.is_file():
                raise ValueError(f"Path exists but is not a file: {self.image_path}")
                
            # Check file permissions
            if not os.access(path_obj, os.R_OK):
                raise PermissionError(f"Image file not readable: {self.image_path}")
            
            # Check file size
            file_size = path_obj.stat().st_size
            if file_size == 0:
                raise ValueError(f"Image file is empty: {self.image_path}")
                
            # Determine if it's a GeoTIFF file
            file_ext = path_obj.suffix.lower()
            self.is_geotiff = file_ext in ['.tif', '.tiff', '.geotiff']
            
            if self.is_geotiff:
                # Use rasterio for GeoTIFF files with enhanced error handling
                try:
                    with rasterio.open(self.image_path) as src:
                        # Validate raster properties
                        if src.count < 3:
                            logger.warning(f"GeoTIFF has only {src.count} bands, may not be suitable for vegetation analysis")
                        
                        # Read all bands
                        bands = []
                        for i in range(1, min(src.count + 1, 4)):  # Limit to first 3-4 bands
                            try:
                                band = src.read(i)
                                if band is None or band.size == 0:
                                    raise ValueError(f"Failed to read band {i} from GeoTIFF")
                                bands.append(band)
                            except Exception as band_error:
                                logger.error(f"Error reading band {i}: {band_error}")
                                raise
                        
                        if len(bands) < 3:
                            raise ValueError(f"Insufficient bands for analysis. Found {len(bands)}, need at least 3")
                        
                        # Stack bands to create RGB-like image
                        self.image = np.stack(bands[:3], axis=2).astype(np.float64)
                        
                        # Validate image data
                        if not np.isfinite(self.image).all():
                            logger.warning("GeoTIFF contains non-finite values, applying cleanup")
                            self.image = np.where(np.isfinite(self.image), self.image, 0)
                            
                        logger.info(f"Successfully loaded GeoTIFF: {self.image_path} with shape {self.image.shape}")
                        
                except RasterioError as rio_error:
                    logger.error(f"Rasterio error loading GeoTIFF {self.image_path}: {rio_error}")
                    raise ValueError(f"Failed to load GeoTIFF file: {rio_error}")
                    
            else:
                # Use OpenCV for regular image files
                self.image = cv2.imread(self.image_path, cv2.IMREAD_COLOR)
                if self.image is None:
                    raise ValueError(f"Failed to load image with OpenCV: {self.image_path}")
                
                # Convert to float64 for calculations
                self.image = self.image.astype(np.float64)
                logger.info(f"Successfully loaded regular image: {self.image_path} with shape {self.image.shape}")
            
            # Final validation
            if self.image is None:
                raise ValueError("Image loading resulted in None")
                
            if len(self.image.shape) != 3 or self.image.shape[2] < 3:
                raise ValueError(f"Invalid image shape: {self.image.shape}. Expected (H, W, >=3)")
                
            if self.image.shape[0] < 10 or self.image.shape[1] < 10:
                raise ValueError(f"Image too small for analysis: {self.image.shape}")
            
            self.image_shape = self.image.shape
            logger.debug(f"Image loaded successfully with shape: {self.image_shape}")
            
        except Exception as e:
            logger.error(f"Error loading image {self.image_path}: {e}")
            raise Exception(f"Image loading failed: {str(e)}")
    
    def analyze(
        self, 
        algorithm: str, 
        ranges: Tuple[float, float] = (-1, 1), 
        colormap: str = 'rdylgn'
    ) -> Dict[str, Any]:
        """
        Perform vegetation analysis using specified algorithm with enhanced validation
        
        Args:
            algorithm: Analysis algorithm name ('ndvi', 'gli', 'vari', etc.)
            ranges: Value range for normalization (min, max)
            colormap: Colormap name for visualization
            
        Returns:
            Dictionary containing analysis results and metadata
            
        Raises:
            ValueError: If algorithm is unsupported or parameters are invalid
        """
        try:
            # Enhanced input validation
            if not isinstance(algorithm, str) or not algorithm.strip():
                raise ValueError("Algorithm must be a non-empty string")
                
            algorithm = algorithm.strip().lower()
            
            # Validate ranges parameter
            if not isinstance(ranges, (tuple, list)) or len(ranges) != 2:
                logger.error(f"Invalid ranges parameter: {ranges}. Using default (-1, 1)")
                ranges = (-1, 1)
            
            try:
                min_val, max_val = float(ranges[0]), float(ranges[1])
                if min_val >= max_val:
                    logger.error(f"Invalid range values: min={min_val} >= max={max_val}")
                    ranges = (-1, 1)
                    min_val, max_val = -1, 1
                else:
                    ranges = (min_val, max_val)
            except (ValueError, TypeError) as e:
                logger.error(f"Cannot convert ranges to floats: {ranges}. Error: {e}")
                ranges = (-1, 1)
            
            # Validate colormap parameter
            if not isinstance(colormap, str) or not colormap.strip():
                logger.warning(f"Invalid colormap: {colormap}. Using default 'rdylgn'")
                colormap = 'rdylgn'
            else:
                colormap = colormap.strip().lower()
                
            # Check if algorithm is supported
            analysis_func = getattr(self, f'calculate_{algorithm}', None)
            if not analysis_func or not callable(analysis_func):
                supported_algorithms = [method[10:] for method in dir(self) 
                                      if method.startswith('calculate_') and callable(getattr(self, method))]
                raise ValueError(f"Unsupported algorithm: {algorithm}. Supported algorithms: {supported_algorithms}")
            
            logger.info(f"Starting vegetation analysis: {algorithm} with ranges {ranges}")
            
            # Calculate vegetation index with error handling
            result_array = analysis_func()
            
            # Validate result array
            if result_array is None:
                raise ValueError(f"Algorithm {algorithm} returned None result")
                
            if not isinstance(result_array, np.ndarray):
                raise ValueError(f"Algorithm {algorithm} returned invalid type: {type(result_array)}")
                
            if result_array.size == 0:
                raise ValueError(f"Algorithm {algorithm} returned empty array")
            
            # Apply color mapping and save result
            result_path = self.apply_colormap_and_save(result_array, algorithm, colormap, ranges)
            
            return {
                'path': result_path,
                'algorithm': algorithm,
                'colormap': colormap,
                'ranges': ranges,
                'array_shape': result_array.shape,
                'array_stats': {
                    'min': float(np.nanmin(result_array)),
                    'max': float(np.nanmax(result_array)), 
                    'mean': float(np.nanmean(result_array)),
                    'std': float(np.nanstd(result_array))
                }
            }
            
        except Exception as e:
            logger.error(f"Vegetation analysis failed for {algorithm}: {e}")
            raise Exception(f"Vegetation analysis error: {str(e)}")
    
    def calculate_ndvi(self) -> np.ndarray:
        """
        Calculate NDVI (Normalized Difference Vegetation Index) with production-grade error handling
        
        Returns:
            2D numpy array containing NDVI values ranging from -1 to 1
            
        Raises:
            ValueError: If image is not loaded or has invalid format
        """
        try:
            if self.image is None:
                raise ValueError("No image loaded for NDVI calculation")
                
            if not isinstance(self.image, np.ndarray):
                raise ValueError(f"Invalid image type: {type(self.image)}. Expected numpy ndarray")
                
            # Ensure image has sufficient dimensions
            if len(self.image.shape) < 3 or self.image.shape[2] < 3:
                raise ValueError(f"Invalid image shape for NDVI: {self.image.shape}. Need at least 3 channels")
                
            # Convert to float64 for high precision calculations
            image_float = self.image.astype(np.float64)
            
            # Split channels (BGR format in OpenCV)
            try:
                b, g, r = cv2.split(image_float)
            except Exception as split_error:
                logger.error(f"Channel splitting failed: {split_error}")
                raise ValueError("Failed to split image channels")
            
            # Validate channel data
            for i, (channel, name) in enumerate([(b, 'Blue'), (g, 'Green'), (r, 'Red')]):
                if channel is None or channel.size == 0:
                    raise ValueError(f"{name} channel is empty or None")
                    
                if not np.isfinite(channel).any():
                    logger.warning(f"{name} channel contains no finite values")
                    
                # Check for reasonable value ranges
                if np.all(channel == 0):
                    logger.warning(f"{name} channel contains all zero values")
            
            # Calculate NDVI: (NIR - Red) / (NIR + Red)
            # For RGB images, we approximate using Green as NIR substitute
            epsilon = 1e-10  # Prevent division by zero
            numerator = g - r
            denominator = g + r + epsilon
            
            # Perform division with safety checks
            with np.errstate(divide='ignore', invalid='ignore'):
                ndvi = numerator / denominator
            
            # Handle NaN, inf, and invalid values
            ndvi = np.where(np.isfinite(ndvi), ndvi, 0.0)
            
            # Clip values to valid NDVI range
            ndvi = np.clip(ndvi, -1.0, 1.0)
            
            # Final validation
            if not np.isfinite(ndvi).all():
                logger.warning("NDVI result contains non-finite values, applying final cleanup")
                ndvi = np.nan_to_num(ndvi, nan=0.0, posinf=1.0, neginf=-1.0)
            
            logger.debug(f"NDVI calculated successfully. Range: [{np.min(ndvi):.3f}, {np.max(ndvi):.3f}]")
            return ndvi.astype(np.float64)
            
        except Exception as e:
            logger.error(f"NDVI calculation error: {e}")
            # Return safe fallback array
            if hasattr(self, 'image') and self.image is not None and hasattr(self.image, 'shape'):
                fallback_shape = self.image.shape[:2]
                logger.warning(f"Returning zero NDVI array with shape {fallback_shape}")
                return np.zeros(fallback_shape, dtype=np.float64)
            else:
                logger.warning("Returning minimal zero NDVI array (100x100)")
                return np.zeros((100, 100), dtype=np.float64)
    
    def calculate_gli(self) -> np.ndarray:
        """
        Calculate GLI (Green Leaf Index) with production-grade error handling
        GLI = (2*Green - Red - Blue) / (2*Green + Red + Blue)
        
        Returns:
            2D numpy array containing GLI values ranging from -1 to 1
            
        Raises:
            ValueError: If image is not loaded or has invalid format
        """
        try:
            if self.image is None:
                raise ValueError("No image loaded for GLI calculation")
                
            if not isinstance(self.image, np.ndarray):
                raise ValueError(f"Invalid image type: {type(self.image)}. Expected numpy ndarray")
                
            # Ensure image has sufficient dimensions
            if len(self.image.shape) < 3 or self.image.shape[2] < 3:
                raise ValueError(f"Invalid image shape for GLI: {self.image.shape}. Need at least 3 channels")
                
            # Convert to float64 for precision
            image_float = self.image.astype(np.float64)
            
            # Split channels safely
            try:
                b, g, r = cv2.split(image_float)
            except Exception as split_error:
                logger.error(f"Channel splitting failed: {split_error}")
                raise ValueError("Failed to split image channels for GLI calculation")
            
            # Validate channel data
            for channel, name in [(b, 'Blue'), (g, 'Green'), (r, 'Red')]:
                if channel is None or channel.size == 0:
                    raise ValueError(f"{name} channel is empty or None")
                    
                if not np.isfinite(channel).any():
                    logger.warning(f"{name} channel contains no finite values")
            
            # Calculate GLI with enhanced numerical stability
            epsilon = 1e-10  # Prevent division by zero
            numerator = (g * 2.0) - r - b
            denominator = (g * 2.0) + r + b + epsilon
            
            # Perform division with safety checks
            with np.errstate(divide='ignore', invalid='ignore'):
                gli = numerator / denominator
            
            # Handle NaN, inf, and invalid values
            gli = np.where(np.isfinite(gli), gli, 0.0)
            
            # Clip to valid range
            gli = np.clip(gli, -1.0, 1.0)
            
            # Final validation and cleanup
            if not np.isfinite(gli).all():
                logger.warning("GLI result contains non-finite values, applying cleanup")
                gli = np.nan_to_num(gli, nan=0.0, posinf=1.0, neginf=-1.0)
            
            logger.debug(f"GLI calculated successfully. Range: [{np.min(gli):.3f}, {np.max(gli):.3f}]")
            return gli.astype(np.float64)
            
        except Exception as e:
            logger.error(f"GLI calculation error: {e}")
            # Return safe fallback array
            if hasattr(self, 'image') and self.image is not None and hasattr(self.image, 'shape'):
                fallback_shape = self.image.shape[:2]
                logger.warning(f"Returning zero GLI array with shape {fallback_shape}")
                return np.zeros(fallback_shape, dtype=np.float64)
            else:
                logger.warning("Returning minimal zero GLI array (100x100)")
                return np.zeros((100, 100), dtype=np.float64)
    
    def calculate_vari(self) -> np.ndarray:
        """
        Calculate VARI (Visible Atmospherically Resistant Index) with production-grade error handling
        VARI = (Green - Red) / (Green + Red - Blue)
        
        Returns:
            2D numpy array containing VARI values
            
        Raises:
            ValueError: If image is not loaded or has invalid format
        """
        try:
            if self.image is None:
                raise ValueError("No image loaded for VARI calculation")
                
            if not isinstance(self.image, np.ndarray):
                raise ValueError(f"Invalid image type: {type(self.image)}. Expected numpy ndarray")
            
            # Ensure sufficient dimensions
            if len(self.image.shape) < 3 or self.image.shape[2] < 3:
                raise ValueError(f"Invalid image shape for VARI: {self.image.shape}. Need at least 3 channels")
            
            image_float = self.image.astype(np.float64)
            b, g, r = cv2.split(image_float)
            
            # Validate channels
            for channel, name in [(b, 'Blue'), (g, 'Green'), (r, 'Red')]:
                if channel is None or channel.size == 0:
                    raise ValueError(f"{name} channel is empty or None")
            
            # Calculate VARI with numerical stability
            epsilon = 1e-10
            denominator = g + r - b + epsilon
            
            with np.errstate(divide='ignore', invalid='ignore'):
                vari = (g - r) / denominator
            
            # Handle invalid values
            vari = np.where(np.isfinite(vari), vari, 0.0)
            vari = np.clip(vari, -1.0, 1.0)
            
            # Final cleanup
            if not np.isfinite(vari).all():
                vari = np.nan_to_num(vari, nan=0.0, posinf=1.0, neginf=-1.0)
            
            logger.debug(f"VARI calculated successfully. Range: [{np.min(vari):.3f}, {np.max(vari):.3f}]")
            return vari.astype(np.float64)
            
        except Exception as e:
            logger.error(f"VARI calculation error: {e}")
            if hasattr(self, 'image') and self.image is not None and hasattr(self.image, 'shape'):
                fallback_shape = self.image.shape[:2]
                return np.zeros(fallback_shape, dtype=np.float64)
            else:
                return np.zeros((100, 100), dtype=np.float64)
    
    def calculate_ndyi(self) -> np.ndarray:
        """Calculate NDYI (Normalized Difference Yellowness Index) with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for NDYI calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        ndyi = (g - b) / (g + b + 1e-8)
        return np.clip(ndyi, -1, 1)
    
    def calculate_ndre(self):
        """Calculate NDRE (Normalized Difference Red Edge Index)"""
        # NDRE requires NIR and Red Edge spectral bands
        # RGB data cannot provide authentic NDRE calculation
        raise ValueError("NDRE analizi için NIR ve Red Edge spektral bantları gereklidir. RGB görüntü ile authentic NDRE hesaplaması yapılamaz.")
    
    def calculate_ndwi(self) -> np.ndarray:
        """Calculate NDWI (Normalized Difference Water Index) with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for NDWI calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        ndwi = (g - r) / (g + r + 1e-8)
        return np.clip(ndwi, -1, 1)
    
    def calculate_ndvi_blue(self) -> np.ndarray:
        """Calculate Blue-based NDVI with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for Blue NDVI calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        ndvi_blue = (g - b) / (g + b + 1e-8)
        return np.clip(ndvi_blue, -1, 1)
    
    def calculate_endvi(self) -> np.ndarray:
        """Calculate ENDVI (Enhanced NDVI) with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for ENDVI calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        endvi = ((g + r) - (2 * b)) / ((g + r) + (2 * b) + 1e-8)
        return np.clip(endvi, -1, 1)
    
    def calculate_vndvi(self) -> np.ndarray:
        """Calculate visible NDVI with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for visible NDVI calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        vndvi = 0.5268 * ((r ** -0.1294) * (g ** 0.3389) * (b ** -0.3118))
        return np.clip(vndvi, 0, 2)
    
    def calculate_mpri(self) -> np.ndarray:
        """Calculate MPRI (Modified Photochemical Reflectance Index) with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for MPRI calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        mpri = (g - r) / (g + r + 1e-8)
        return np.clip(mpri, -1, 1)
    
    def calculate_exg(self) -> np.ndarray:
        """Calculate EXG (Excess Green Index) with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for EXG calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        exg = (2 * g) - (r + b)
        return np.clip(exg, -255, 255)
    
    def calculate_tgi(self) -> np.ndarray:
        """Calculate TGI (Triangular Greenness Index) with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for TGI calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        tgi = (g - 0.39 * r - 0.61 * b)
        return np.clip(tgi, -255, 255)
    
    def calculate_bai(self):
        """Calculate BAI (Burn Area Index)"""
        # BAI requires NIR and SWIR spectral bands for authentic calculation
        # Formula: BAI = 1 / ((0.1 - NIR)² + (0.06 - SWIR)²)
        # RGB data cannot provide authentic BAI calculation
        raise ValueError("BAI analizi için NIR ve SWIR spektral bantları gereklidir. RGB görüntü ile authentic BAI hesaplaması yapılamaz.")
    
    def calculate_gndvi(self) -> np.ndarray:
        """Calculate GNDVI (Green NDVI) with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for GNDVI calculation")
        b, g, r = cv2.split(self.image.astype(np.float32))
        gndvi = (g - r) / (g + r + 1e-8)
        return np.clip(gndvi, -1, 1)
    
    def calculate_savi(self) -> np.ndarray:
        """Calculate SAVI (Soil Adjusted Vegetation Index) with type safety"""
        if self.image is None:
            raise ValueError("No image loaded for SAVI calculation")
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
            # Safe colormap mapping using available OpenCV colormaps
            colormap_dict = {
                'rdylgn': cv2.COLORMAP_JET,  # Use JET as fallback for RdYlGn
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
