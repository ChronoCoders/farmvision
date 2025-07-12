import numpy as np
import cv2
import logging
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

# Color maps from uploaded files
RdYlGn_lut = [
    [165,0,38], [167,2,38], [169,4,38], [171,6,38], [173,8,38], [175,9,38],
    [177,11,38], [179,13,38], [181,15,38], [182,17,39], [184,19,39], [186,21,39],
    [188,23,39], [190,25,39], [192,27,39], [194,29,40], [196,31,40], [197,33,40],
    [199,35,40], [201,37,41], [203,39,41], [204,41,41], [206,43,42], [208,45,42],
    [209,47,43], [211,49,43], [212,51,44], [214,53,44], [215,56,45], [217,58,46],
    [218,60,46], [220,62,47], [221,64,48], [222,67,49], [224,69,50], [225,71,51],
    [226,74,51], [227,76,52], [228,78,53], [229,81,54], [231,83,55], [232,85,56],
    [233,88,57], [234,90,58], [235,93,60], [236,95,61], [237,97,62], [237,100,63],
    [238,102,64], [239,105,65], [240,107,66], [240,110,68], [241,112,69], [242,115,70],
    [242,117,71], [243,120,73], [243,122,74], [244,125,75], [244,127,77], [245,130,78],
    [245,132,79], [246,135,81], [246,137,82], [247,140,84], [247,142,85], [248,145,87],
    [248,147,88], [248,150,90], [249,152,91], [249,155,93], [249,158,94], [250,160,96],
    [250,163,98], [250,165,99], [251,168,101], [251,170,103], [251,173,104], [251,175,106],
    [252,178,108], [252,180,109], [252,183,111], [252,186,113], [252,188,115], [253,191,116],
    [253,193,118], [253,196,120], [253,198,122], [253,201,124], [253,203,125], [254,206,127],
    [254,208,129], [254,211,131], [254,214,133], [254,216,135], [254,219,137], [254,221,139],
    [254,224,141], [254,226,143], [254,229,145], [254,231,147], [254,234,149], [254,236,151],
    [254,239,153], [254,241,155], [254,244,157], [254,246,160], [254,249,162], [254,251,164],
    [254,254,166], [253,254,168], [251,254,170], [250,254,172], [248,254,175], [247,254,177],
    [245,254,179], [244,254,181], [242,254,183], [241,254,185], [239,254,188], [238,254,190],
    [236,254,192], [235,254,194], [233,254,196], [232,254,199], [230,254,201], [229,254,203],
    [227,254,205], [226,254,207], [224,254,210], [223,254,212], [221,254,214], [220,254,216]
]

def apply_colormap(data, colormap='rdylgn', min_val=None, max_val=None):
    """
    Fixed colormap application with bounds checking
    """
    try:
        # Input validation
        if data is None or data.size == 0:
            raise ValueError("Invalid input data")
            
        # Handle NaN values
        valid_mask = ~np.isnan(data)
        if not np.any(valid_mask):
            raise ValueError("All data values are NaN")
        
        if min_val is None:
            min_val = np.nanmin(data)
        if max_val is None:
            max_val = np.nanmax(data)
        
        # Prevent division by zero
        if max_val == min_val:
            max_val = min_val + 1e-6
            
        # Safe normalization
        normalized = np.full_like(data, 0.0)
        normalized[valid_mask] = (data[valid_mask] - min_val) / (max_val - min_val)
        normalized = np.clip(normalized, 0, 1)
        
        if colormap == 'rdylgn':
            colormap_array = np.array(RdYlGn_lut) / 255.0
            colored = np.zeros((*data.shape, 3))
            
            # Vectorized colormap application
            indices = (normalized * (len(colormap_array) - 1)).astype(int)
            indices = np.clip(indices, 0, len(colormap_array) - 1)
            
            for i in range(3):  # RGB channels
                colored[:, :, i] = colormap_array[indices, i]
                    
            return colored
        else:
            import matplotlib.pyplot as plt
            cmap = plt.cm.get_cmap(colormap)
            return cmap(normalized)
            
    except Exception as e:
        logging.error(f"Colormap application error: {e}")
        # Return grayscale fallback
        gray = np.clip((data - np.nanmin(data)) / (np.nanmax(data) - np.nanmin(data)), 0, 1)
        return np.stack([gray, gray, gray], axis=-1)

def calculate_ndvi_advanced(red_band, nir_band):
    """
    Advanced NDVI calculation with error handling
    """
    try:
        # Input validation
        if red_band is None or nir_band is None:
            raise ValueError("Invalid input bands")
        
        # Convert to float to prevent integer overflow
        red_float = red_band.astype(np.float64)
        nir_float = nir_band.astype(np.float64)
        
        # Use small epsilon to prevent division by zero
        epsilon = 1e-10
        denominator = nir_float + red_float + epsilon
        
        # Calculate NDVI
        ndvi = (nir_float - red_float) / denominator
        
        # Handle potential NaN/inf values
        ndvi = np.where(np.isfinite(ndvi), ndvi, 0)
        ndvi = np.clip(ndvi, -1, 1)
        
        return ndvi
        
    except Exception as e:
        logging.error(f"NDVI calculation error: {e}")
        # Return zero array as fallback
        return np.zeros_like(red_band, dtype=np.float64)
    
    return ndvi

def calculate_gli_advanced(red_band, green_band, blue_band):
    """
    Advanced Green Leaf Index calculation
    """
    denominator = 2 * green_band + red_band + blue_band
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    gli = (2 * green_band - red_band - blue_band) / denominator
    
    return gli

def calculate_vari_advanced(red_band, green_band, blue_band):
    """
    Advanced Visible Atmospherically Resistant Index
    """
    denominator = green_band + red_band - blue_band
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    vari = (green_band - red_band) / denominator
    
    return vari

def calculate_ndwi_advanced(green_band, nir_band):
    """
    Advanced Normalized Difference Water Index
    """
    denominator = green_band + nir_band
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    ndwi = (green_band - nir_band) / denominator
    
    return ndwi

def calculate_savi_advanced(red_band, nir_band, l_factor=0.5):
    """
    Advanced Soil Adjusted Vegetation Index
    """
    denominator = nir_band + red_band + l_factor
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    savi = ((nir_band - red_band) * (1 + l_factor)) / denominator
    
    return savi

def calculate_evi_advanced(red_band, nir_band, blue_band):
    """
    Advanced Enhanced Vegetation Index
    """
    denominator = nir_band + 6 * red_band - 7.5 * blue_band + 1
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    evi = 2.5 * (nir_band - red_band) / denominator
    
    return evi

def calculate_tgi_advanced(red_band, green_band, blue_band):
    """
    Advanced Triangular Greenness Index
    """
    tgi = green_band - 0.39 * red_band - 0.61 * blue_band
    
    return tgi

def calculate_msavi_advanced(red_band, nir_band):
    """
    Advanced Modified Soil Adjusted Vegetation Index
    """
    msavi = (2 * nir_band + 1 - np.sqrt((2 * nir_band + 1)**2 - 8 * (nir_band - red_band))) / 2
    
    return msavi

def calculate_osavi_advanced(red_band, nir_band, y_factor=0.16):
    """
    Advanced Optimized Soil Adjusted Vegetation Index
    """
    denominator = nir_band + red_band + y_factor
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    osavi = (nir_band - red_band) / denominator
    
    return osavi

def calculate_mcari_advanced(red_band, green_band, red_edge_band):
    """
    Advanced Modified Chlorophyll Absorption Ratio Index
    """
    mcari = ((red_edge_band - red_band) - 0.2 * (red_edge_band - green_band)) * (red_edge_band / red_band)
    
    return mcari

def calculate_rdvi_advanced(red_band, nir_band):
    """
    Advanced Renormalized Difference Vegetation Index
    """
    denominator = np.sqrt(nir_band + red_band)
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    rdvi = (nir_band - red_band) / denominator
    
    return rdvi

def calculate_gndvi_advanced(green_band, nir_band):
    """
    Advanced Green Normalized Difference Vegetation Index
    """
    denominator = nir_band + green_band
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    gndvi = (nir_band - green_band) / denominator
    
    return gndvi

def calculate_cvi_advanced(red_band, green_band, nir_band):
    """
    Advanced Chlorophyll Vegetation Index
    """
    cvi = (nir_band * red_band) / (green_band ** 2)
    
    return cvi

def calculate_arvi_advanced(red_band, nir_band, blue_band):
    """
    Advanced Atmospherically Resistant Vegetation Index
    """
    denominator = nir_band + red_band - blue_band
    denominator = np.where(denominator == 0, np.nan, denominator)
    
    arvi = (nir_band - red_band) / denominator
    
    return arvi

def calculate_gci_advanced(red_band, green_band, nir_band):
    """
    Advanced Green Coverage Index
    """
    gci = (nir_band / green_band) - 1
    
    return gci

# Comprehensive vegetation analysis function
VEGETATION_ALGORITHMS = {
    'ndvi': calculate_ndvi_advanced,
    'gli': calculate_gli_advanced,
    'vari': calculate_vari_advanced,
    'ndwi': calculate_ndwi_advanced,
    'savi': calculate_savi_advanced,
    'evi': calculate_evi_advanced,
    'tgi': calculate_tgi_advanced,
    'msavi': calculate_msavi_advanced,
    'osavi': calculate_osavi_advanced,
    'rdvi': calculate_rdvi_advanced,
    'gndvi': calculate_gndvi_advanced,
    'cvi': calculate_cvi_advanced,
    'arvi': calculate_arvi_advanced,
    'gci': calculate_gci_advanced
}

def analyze_vegetation_comprehensive(image_bands, algorithm='ndvi', colormap='rdylgn'):
    """
    Comprehensive vegetation analysis using uploaded algorithms
    """
    try:
        if algorithm not in VEGETATION_ALGORITHMS:
            raise ValueError(f"Desteklenmeyen algoritma: {algorithm}")
        
        # Extract bands based on algorithm requirements - ONLY AUTHENTIC DATA
        if algorithm in ['ndvi', 'savi', 'msavi', 'osavi', 'rdvi', 'gndvi']:
            # Requires RED and NIR bands
            red_band = image_bands.get('red')
            nir_band = image_bands.get('nir')
            
            if red_band is None or nir_band is None:
                raise ValueError(f"Algoritma {algorithm} için RED ve NIR bandları gereklidir")
            
            result = VEGETATION_ALGORITHMS[algorithm](red_band, nir_band)
            
        elif algorithm in ['gli', 'vari', 'tgi', 'evi', 'arvi']:
            # Requires RGB bands
            red_band = image_bands.get('red')
            green_band = image_bands.get('green')
            blue_band = image_bands.get('blue')
            
            if red_band is None or green_band is None or blue_band is None:
                raise ValueError(f"Algoritma {algorithm} için RGB bandları gereklidir")
            
            if algorithm == 'evi' or algorithm == 'arvi':
                nir_band = image_bands.get('nir')
                if nir_band is None:
                    raise ValueError(f"Algoritma {algorithm} için NIR bandı gereklidir")
                    
                if algorithm == 'evi':
                    result = VEGETATION_ALGORITHMS[algorithm](red_band, nir_band, blue_band)
                else:  # arvi
                    result = VEGETATION_ALGORITHMS[algorithm](red_band, nir_band, blue_band)
            else:
                result = VEGETATION_ALGORITHMS[algorithm](red_band, green_band, blue_band)
                
        elif algorithm == 'ndwi':
            green_band = image_bands.get('green')
            nir_band = image_bands.get('nir')
            
            if green_band is None or nir_band is None:
                raise ValueError(f"Algoritma {algorithm} için GREEN ve NIR bandları gereklidir")
            
            result = VEGETATION_ALGORITHMS[algorithm](green_band, nir_band)
            
        elif algorithm in ['cvi', 'gci']:
            red_band = image_bands.get('red')
            green_band = image_bands.get('green')
            nir_band = image_bands.get('nir')
            
            if red_band is None or green_band is None or nir_band is None:
                raise ValueError(f"Algoritma {algorithm} için RED, GREEN ve NIR bandları gereklidir")
            
            result = VEGETATION_ALGORITHMS[algorithm](red_band, green_band, nir_band)
            
        else:
            raise ValueError(f"Desteklenmeyen algoritma: {algorithm}")
        
        # Apply colormap
        colored_result = apply_colormap(result, colormap)
        
        # Calculate statistics
        stats = {
            'min': np.nanmin(result),
            'max': np.nanmax(result),
            'mean': np.nanmean(result),
            'std': np.nanstd(result),
            'median': np.nanmedian(result)
        }
        
        return {
            'analysis_data': result,
            'colored_image': colored_result,
            'statistics': stats,
            'algorithm': algorithm,
            'colormap': colormap
        }
        
    except Exception as e:
        print(f"Bitki örtüsü analizinde hata: {e}")
        return None