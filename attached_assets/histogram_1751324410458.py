import rasterio
from rio_tiler.utils import linear_rescale
from rio_tiler.colormap import cmap
import numpy as np
np.seterr(divide='ignore', invalid='ignore')
from rio_tiler.io import Reader
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
from rasterio.enums import ColorInterp

def get_zoom(raster_path):
    with Reader(raster_path) as src:
        info = src.info()
        band_count = src.dataset.meta['count']
        minzoom, maxzoom = info["minzoom"], info["maxzoom"]
        if maxzoom < minzoom:
            maxzoom = minzoom

    return {"minzoom":minzoom, "maxzoom":maxzoom, "band_count":band_count}


class algos:
    def __init__(self,path,out): 
        
        self.input_path = path
        self.output_path = out
        self.raster = rasterio.open(self.input_path,driver="GTiff",dtype=np.float32)
        self.red = self.raster.read(1)
        self.green = self.raster.read(2)
        self.blue = self.raster.read(3)
        self.nir = self.raster.read(4)
        
    
    def Ndvi(self,ranges= (-1,1),colormap=None): 
        if ranges == (-0.0, 0.0):
            ranges = (-0.5,1)
        
        cm = cmap.get(colormap,)
        
        data = self.raster.read((3,2,4)).astype(np.float32) #BGRN #RGN
        # (N - R) / (N + R) BGRN
        ndvi = (data[2] - data[0]) / (data[2] + data[0])
        ndvi = ndvi.astype(np.float32)
        #ndvi[np.isnan(ndvi)] = -99
   
        rgb = linear_rescale(ndvi, in_range=ranges)
        
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'driver' :'GTiff',
                     'nodata': 0,
                     'bins': 255,
                     #'pmin':-1,
                     #'pmax':1,
                     'dtype':np.uint16,
                     #'compress':'tiff',
                     #'crs':32636 ,
                     #'photometric':'RGA',
                     'quality':90
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.alpha  ] #ColorInterp.blue,, ColorInterp.green, ColorInterp.alpha
            dst.write(rgb,1)
            dst.write_colormap(1, cm)
            
            
        dst.close()   
            
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
    
    
    def Vari(self,ranges,colormap):
        # (G - R) / (G + R - B) BGRN
        cm = cmap.get(colormap,)
        # Apply NDVI band math BGRN
        red = self.red.astype('f4')
        green = self.green.astype('f4')
        blue = self.blue.astype('f4')
        Vari = (green - red) / (green + red-blue)
        Vari = Vari.astype(np.float32)
        rgb = linear_rescale(Vari, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
          
            
    def Gli(self,ranges,colormap):
        # ((G * 2) - R - B) / ((G * 2) + R + B) BGRN
        cm = cmap.get(colormap,)
        # Apply NDVI band math BGRN
        red = self.red.astype('f4')
        green = self.green.astype('f4')
        blue = self.blue.astype('f4')
        Gli = ((green*2) - red - blue) /((green*2) + red+blue)
        Gli = Gli.astype(np.float32)
        rgb = linear_rescale(Gli, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

    
    def NDYI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (G - B) / (G + B) BGRN
        green = self.green.astype('f4')
        blue = self.blue.astype('f4')
        NDYI = (green - blue) / (green + blue)
        NDYI = NDYI.astype(np.float32)
        rgb = linear_rescale(NDYI, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
            

    
    def NDRE(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (N - Re) / (N + Re) BGRN
        red = self.red.astype('f4')
        nir = self.nir.astype('f4')
        NDRE = (nir - red) / (nir + red)
        NDRE = NDRE.astype(np.float32)
        rgb = linear_rescale(NDRE, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
    
    def NDWI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (G - N) / (G + N) BGRN
        green = self.green.astype('f4')
        nir = self.nir.astype('f4')
        NDWI = (green - nir) / (nir + green)
        NDWI = NDWI.astype(np.float32)
        rgb = linear_rescale(NDWI, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

    
    
    def NDVI_Blue(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (N - B) / (N + B) BGRN
        blue = self.blue.astype('f4')
        nir = self.nir.astype('f4')
        NDVI_Blue = (nir - blue) / (nir + blue)
        NDVI_Blue = NDVI_Blue.astype(np.float32)
        rgb = linear_rescale(NDVI_Blue, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

    
    
    def ENDVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # ((N + G) - (2 * B)) / ((N + G) + (2 * B)) BGRN
        green = self.green.astype('f4')
        blue = self.blue.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = ((nir + green)- (2*blue)) / ((nir + green)+(2*blue))
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

    
    
    def VNDVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # 0.5268*((R ** -0.1294) * (G ** 0.3389) * (B ** -0.3118)) band math BGRN
        red = self.red.astype('f4')
        blue = self.blue.astype('f4')
        green = self.green.astype('f4')
        ndvi = 0.5268*((red ** -0.1294) * (green ** 0.3389) * (blue ** -0.3118))
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

      
    
    def MPRI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (G - R) / (G + R) BGRN
        red = self.red.astype('f4')
        green = self.green.astype('f4')
        ndvi = (green - red) / (green + red)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
          
    def EXG(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (2 * G) - (R + B) BGRN
        red = self.red.astype('f4')
        green = self.green.astype('f4')
        blue = self.blue.astype('f4')
        ndvi = (2 * green) - (red + blue)
        ndvi = ndvi.astype(np.float32)
        rgb = ndvi#linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
            
    
    
    def TGI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (G - 0.39) * (R - 0.61) * B band math BGRN
        red = self.red.astype('f4')
        green = self.green.astype('f4')
        blue = self.blue.astype('f4')
        ndvi = (green - 0.39) * (red - 0.61) * blue
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=0)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

    
    
    def BAI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # 1.0 / (((0.1 - R) ** 2) + ((0.06 - N) ** 2)) band math BGRN
        red = self.red.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = 1.0 / (((0.1 - red) ** 2) + ((0.06 - nir) ** 2))
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

    
  
    
    def GNDVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (N - G) / (N + G) band math BGRN
        green = self.green.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = (nir - green) / (nir + green)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
           
    
    
    
    def GRVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # N / G band math BGRN
        green = self.green.astype('f4')
        nir = self.nir.astype('f4')
        ndvi =nir / green
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

    
    def SAVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (1.5 * (N - R)) / (N + R + 0.5) band math BGRN
        red = self.red.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = (1.5 * (nir - red)) / (nir + red + 0.5)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
  
    
    def MNLI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # ((N ** 2 - R) * 1.5) / (N ** 2 + R + 0.5) band math BGRN
        red = self.red.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = ((nir ** 2 - red) * 1.5) / (nir ** 2 + red + 0.5)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
    
    
    
    def MSR(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # ((N / R) - 1) / (sqrt(N / R) + 1) band math BGRN
        red = self.red.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = ((nir / red) - 1) / (np.sqrt(np / red) + 1)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
    
    
    def RDVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (N - R) / sqrt(N + R) band math BGRN
        red = self.red.astype('f4')
        nir = self.nir.astype('f4')
        ndvi =  (nir - red) / np.sqrt(nir + red)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
    
    def TDVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # 1.5 * ((N - R) / sqrt(N ** 2 + R + 0.5)) BGRN
        red = self.red.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = 1.5 * ((nir - red) / np.sqrt(nir ** 2 + red + 0.5))
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
             
    
    
    def OSAVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (N - R) / (N + R + 0.16) BGRN
        red = self.red.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = (nir - red) / (nir + red + 0.16)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
           
                
    
    
    def LAI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # 3.618 * (2.5 * (N - R) / (N + 6*R - 7.5*B + 1)) * 0.118 band math BGRN
        red = self.red.astype('f4')
        blue = self.blue.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = 3.618 * (2.5 * (nir - red) / (nir + 6*red - 7.5*blue + 1)) * 0.118
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

            
    
    
    def EVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # 2.5 * (N - R) / (N + 6*R - 7.5*B + 1) band math BGRN
        red = self.red.astype('f4')
        blue = self.blue.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = 2.5 * (nir - red) / (nir + 6*red - 7.5*blue + 1)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}
    
    def ARVI(self,ranges,colormap):
        cm = cmap.get(colormap,)
        # (N - (2 * R) + B) / (N + (2 * R) + B) band math BGRN
        red = self.red.astype('f4')
        blue = self.blue.astype('f4')
        nir = self.nir.astype('f4')
        ndvi = (nir - (2 * red) + blue) / (nir + (2 * red) + blue)
        ndvi = ndvi.astype(np.float32)
        rgb = linear_rescale(ndvi, in_range=ranges)
        rgb=rgb.astype(np.float32)
        meta = self.raster.meta
        meta.update({'count': 1,
                     'nodata': 0,
                     #'crs':4326 
                    })
        with rasterio.open(f"{BASE_DIR}/static/results/{self.output_path}/odm_orthophoto/output.tif", 'w',**meta) as dst:
            #dst.colorinterp = [ColorInterp.red, ColorInterp.green, ColorInterp.blue, ColorInterp.alpha]
            dst.write_band(1,rgb)
            dst.write_colormap(1, cm)
        
        return { 'path': f"results/{self.output_path}/odm_orthophoto/output.tif",'colormap':colormap,'ranges':ranges,}

    






def gli(path):
    range =  (-1, 1)
    img = Image.open(path)     
    arr = np.asarray(img).astype(float) 
    gli_array = (2*arr[:,:,1]-arr[:,:,0]-arr[:,:,2])/(2*arr[:,:,1]+arr[:,:,0]+arr[:,:,2])            
    gli_array[np.isnan(gli_array)] = 0  
    return gli_array  

def vari(path): 
    range =  (-1, 1)
    img = Image.open(path) 
    arr = np.asarray(img).astype(float) 
    vari_array = (arr[:,:,1]-arr[:,:,0])/(arr[:,:,1]+arr[:,:,0]-arr[:,:,2])           
    vari_array[np.isnan(vari_array)] = 0 
    return vari_array  

def vigreen(path):
    img = Image.open(path) 
    arr = np.asarray(img).astype(float)     
    vi_array = (arr[:,:,1]-arr[:,:,0])/(arr[:,:,1]+arr[:,:,0])             
    vi_array[np.isnan(vi_array)] = 0  
    return vi_array

def ndvi(path):
    range =  (-1, 1)
    img = Image.open(path)     
    arr = np.asarray(img).astype(float)    
    ndvi_array = (arr[:,:,2]-arr[:,:,0])/(arr[:,:,2]+arr[:,:,0])
    ndvi_array[np.isnan(ndvi_array)] = 0 
    return ndvi_array



def hist(path):
    import cv2
    img = cv2.imread(path)
    hist,bins = np.histogram(img.ravel(),256,[0,256])
    return hist,bins