import rasterio
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import cv2
import os
import logging
from pathlib import Path

def read_geotiff(filename):
    """
    Fixed GeoTIFF reading with proper error handling
    """
    try:
        if not Path(filename).exists():
            raise FileNotFoundError(f"GeoTIFF file not found: {filename}")
            
        with rasterio.open(filename) as src:
            # Validate file format
            if src.count == 0:
                raise ValueError("Invalid GeoTIFF: No bands found")
                
            # Read data with memory management
            data = src.read()
            
            # Check for valid data
            if data is None or data.size == 0:
                raise ValueError("Invalid GeoTIFF: Empty data")
            
            metadata = {
                'crs': src.crs,
                'transform': src.transform,
                'bounds': src.bounds,
                'width': src.width,
                'height': src.height,
                'count': src.count,
                'dtype': src.dtypes[0] if src.count > 0 else None
            }
            
            return data, metadata
            
    except ImportError:
        raise ImportError("rasterio library not installed. Install with: pip install rasterio")
    except Exception as e:
        logging.error(f"GeoTIFF reading error: {e}")
        return None, None

def write_geotiff(filename, data, metadata, compress='lzw'):
    """
    Write GeoTIFF file with proper metadata
    """
    try:
        # Handle single band data
        if len(data.shape) == 2:
            data = np.expand_dims(data, axis=0)
        
        count, height, width = data.shape
        
        # Determine dtype
        if data.dtype == np.float32:
            dtype = rasterio.float32
        elif data.dtype == np.float64:
            dtype = rasterio.float64
        elif data.dtype == np.uint8:
            dtype = rasterio.uint8
        elif data.dtype == np.uint16:
            dtype = rasterio.uint16
        else:
            dtype = rasterio.float32
            data = data.astype(np.float32)
        
        with rasterio.open(
            filename,
            'w',
            driver='GTiff',
            height=height,
            width=width,
            count=count,
            dtype=dtype,
            crs=metadata.get('crs'),
            transform=metadata.get('transform'),
            compress=compress
        ) as dst:
            dst.write(data)
            
        return True
    except Exception as e:
        print(f"GeoTIFF yazma hatası: {e}")
        return False

def calculate_histogram(image_data, bins=256, range_values=None, mask=None):
    """
    Calculate histogram for image data
    Based on uploaded histogram algorithms
    """
    try:
        # Handle multi-band data
        if len(image_data.shape) == 3:
            # For multi-band, calculate histogram for each band
            histograms = []
            for band in range(image_data.shape[0]):
                band_data = image_data[band]
                
                # Apply mask if provided
                if mask is not None:
                    band_data = band_data[mask]
                else:
                    band_data = band_data.flatten()
                
                # Remove NaN values
                band_data = band_data[~np.isnan(band_data)]
                
                if range_values is None:
                    range_values = (np.min(band_data), np.max(band_data))
                
                hist, bin_edges = np.histogram(band_data, bins=bins, range=range_values)
                histograms.append((hist, bin_edges))
            
            return histograms
        else:
            # Single band
            if mask is not None:
                data = image_data[mask]
            else:
                data = image_data.flatten()
            
            # Remove NaN values
            data = data[~np.isnan(data)]
            
            if range_values is None:
                range_values = (np.min(data), np.max(data))
            
            hist, bin_edges = np.histogram(data, bins=bins, range=range_values)
            return [(hist, bin_edges)]
            
    except Exception as e:
        print(f"Histogram hesaplama hatası: {e}")
        return None

def create_histogram_plot(histogram_data, title="Histogram", save_path=None):
    """
    Create histogram plot visualization
    """
    try:
        fig, axes = plt.subplots(len(histogram_data), 1, figsize=(10, 6 * len(histogram_data)))
        
        if len(histogram_data) == 1:
            axes = [axes]
        
        colors = ['red', 'green', 'blue', 'alpha']
        
        for i, (hist, bin_edges) in enumerate(histogram_data):
            ax = axes[i]
            
            # Calculate bin centers
            bin_centers = (bin_edges[:-1] + bin_edges[1:]) / 2
            
            # Plot histogram
            ax.bar(bin_centers, hist, width=(bin_edges[1] - bin_edges[0]) * 0.8, 
                   color=colors[i % len(colors)], alpha=0.7, 
                   label=f'Band {i+1}' if len(histogram_data) > 1 else 'Data')
            
            ax.set_xlabel('Değer')
            ax.set_ylabel('Frekans')
            ax.set_title(f'{title} - Band {i+1}' if len(histogram_data) > 1 else title)
            ax.legend()
            ax.grid(True, alpha=0.3)
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            plt.close()
            return save_path
        else:
            return fig
            
    except Exception as e:
        print(f"Histogram plot oluşturma hatası: {e}")
        return None

def process_geotiff_histogram(file_path, output_dir=None, bins=256):
    """
    Process GeoTIFF file and generate histogram analysis
    """
    try:
        # Read GeoTIFF
        data, metadata = read_geotiff(file_path)
        if data is None:
            return None
        
        # Calculate histogram
        histogram_data = calculate_histogram(data, bins=bins)
        if histogram_data is None:
            return None
        
        # Create output directory if not provided
        if output_dir is None:
            output_dir = Path(file_path).parent / 'histogram_analysis'
        
        os.makedirs(output_dir, exist_ok=True)
        
        # Generate filename
        base_name = Path(file_path).stem
        plot_path = os.path.join(output_dir, f'{base_name}_histogram.png')
        
        # Create histogram plot
        plot_file = create_histogram_plot(histogram_data, 
                                        title=f"GeoTIFF Histogram - {base_name}",
                                        save_path=plot_path)
        
        # Calculate statistics
        statistics = []
        for i, (hist, bin_edges) in enumerate(histogram_data):
            # Get original band data for statistics
            if len(data.shape) == 3:
                band_data = data[i].flatten()
            else:
                band_data = data.flatten()
            
            # Remove NaN values
            band_data = band_data[~np.isnan(band_data)]
            
            stats = {
                'band': i + 1,
                'min': float(np.min(band_data)),
                'max': float(np.max(band_data)),
                'mean': float(np.mean(band_data)),
                'std': float(np.std(band_data)),
                'median': float(np.median(band_data)),
                'count': len(band_data)
            }
            statistics.append(stats)
        
        result = {
            'histogram_data': histogram_data,
            'statistics': statistics,
            'plot_path': plot_file,
            'metadata': metadata,
            'bins': bins
        }
        
        return result
        
    except Exception as e:
        print(f"GeoTIFF histogram işleme hatası: {e}")
        return None

def extract_rgb_from_geotiff(file_path, output_path=None):
    """
    Extract RGB image from GeoTIFF for visualization
    """
    try:
        data, metadata = read_geotiff(file_path)
        if data is None:
            return None
        
        # Handle different band configurations
        if data.shape[0] >= 3:
            # Take first 3 bands as RGB
            rgb_data = data[:3]
        elif data.shape[0] == 1:
            # Single band - create grayscale
            rgb_data = np.repeat(data, 3, axis=0)
        else:
            print("Desteklenmeyen band sayısı")
            return None
        
        # Normalize to 0-255 range
        rgb_normalized = []
        for band in rgb_data:
            band_min, band_max = np.nanmin(band), np.nanmax(band)
            if band_max > band_min:
                normalized = ((band - band_min) / (band_max - band_min) * 255).astype(np.uint8)
            else:
                normalized = np.zeros_like(band, dtype=np.uint8)
            rgb_normalized.append(normalized)
        
        # Convert to HWC format
        rgb_image = np.stack(rgb_normalized, axis=-1)
        
        # Save as PNG if output path provided
        if output_path:
            image = Image.fromarray(rgb_image)
            image.save(output_path)
            return output_path
        else:
            return rgb_image
            
    except Exception as e:
        print(f"RGB çıkarma hatası: {e}")
        return None

def analyze_vegetation_from_geotiff(file_path, algorithm='ndvi', output_dir=None):
    """
    Analyze vegetation indices from GeoTIFF file
    Integrates with advanced_vegetation.py algorithms
    """
    try:
        from utils.advanced_vegetation import analyze_vegetation_comprehensive
        
        # Read GeoTIFF
        data, metadata = read_geotiff(file_path)
        if data is None:
            return None
        
        # Prepare bands for vegetation analysis
        image_bands = {}
        
        if data.shape[0] >= 4:
            # Assume first 4 bands are R, G, B, NIR
            image_bands['red'] = data[0]
            image_bands['green'] = data[1] 
            image_bands['blue'] = data[2]
            image_bands['nir'] = data[3]
        elif data.shape[0] == 3:
            # RGB only
            image_bands['red'] = data[0]
            image_bands['green'] = data[1]
            image_bands['blue'] = data[2]
            # Mock NIR band
            image_bands['nir'] = data[1] * 1.2  # Rough approximation
        else:
            print("Yetersiz band sayısı vegetation analizi için")
            return None
        
        # Perform vegetation analysis
        analysis_result = analyze_vegetation_comprehensive(image_bands, algorithm)
        
        if analysis_result and output_dir:
            # Save results
            os.makedirs(output_dir, exist_ok=True)
            
            base_name = Path(file_path).stem
            result_path = os.path.join(output_dir, f'{base_name}_{algorithm}_analysis.tif')
            
            # Save analysis result as GeoTIFF
            analysis_data = analysis_result['analysis_data']
            write_geotiff(result_path, analysis_data, metadata)
            
            # Save colored visualization
            colored_path = os.path.join(output_dir, f'{base_name}_{algorithm}_colored.png')
            colored_image = (analysis_result['colored_image'] * 255).astype(np.uint8)
            if len(colored_image.shape) == 3 and colored_image.shape[-1] >= 3:
                Image.fromarray(colored_image[:,:,:3]).save(colored_path)
            
            analysis_result['geotiff_path'] = result_path
            analysis_result['colored_path'] = colored_path
        
        return analysis_result
        
    except Exception as e:
        print(f"GeoTIFF vegetation analizi hatası: {e}")
        return None