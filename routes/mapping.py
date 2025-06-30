import os
import time
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from models import VegetationAnalysis, Project
from utils.vegetation_analysis import VegetationAnalyzer
from utils.histogram_geotiff import process_geotiff_histogram, analyze_vegetation_from_geotiff, extract_rgb_from_geotiff
from utils.advanced_vegetation import analyze_vegetation_comprehensive
from utils.helpers import allowed_file, save_uploaded_file
from app import db, app

mapping_bp = Blueprint('mapping', __name__)

VEGETATION_ALGORITHMS = {
    'ndvi': 'NDVI - Normalized Difference Vegetation Index',
    'gli': 'GLI - Green Leaf Index',
    'vari': 'VARI - Visual Atmospheric Resistance Index',
    'ndyi': 'NDYI - Normalized Difference Yellowness Index',
    'ndre': 'NDRE - Normalized Difference Red Edge Index',
    'ndwi': 'NDWI - Normalized Difference Water Index',
    'ndvi_blue': 'NDVI (Blue) - Blue-based NDVI',
    'endvi': 'ENDVI - Enhanced NDVI',
    'vndvi': 'vNDVI - Visible NDVI',
    'mpri': 'MPRI - Modified Photochemical Reflectance Index',
    'exg': 'EXG - Excess Green Index',
    'tgi': 'TGI - Triangular Greenness Index',
    'bai': 'BAI - Burn Area Index',
    'gndvi': 'GNDVI - Green NDVI',
    'savi': 'SAVI - Soil Adjusted Vegetation Index'
}

COLORMAPS = {
    'rdylgn': 'RdYlGn',
    'spectral': 'Spectral',
    'rdylgn_r': 'RdYlGn (Reverse)',
    'spectral_r': 'Spectral (Reverse)',
    'viridis': 'Viridis',
    'plasma': 'Plasma',
    'inferno': 'Inferno',
    'magma': 'Magma',
    'jet': 'Jet',
    'terrain': 'Terrain'
}

@mapping_bp.route('/')
@login_required
def index():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    recent_analyses = VegetationAnalysis.query.join(Project)\
                                             .filter(Project.user_id == current_user.id)\
                                             .order_by(VegetationAnalysis.created_at.desc())\
                                             .limit(10).all()
    return render_template('mapping.html', projects=projects, recent_analyses=recent_analyses)

@mapping_bp.route('/vegetation', methods=['GET', 'POST'])
@login_required
def vegetation_analysis():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('Lütfen bir GeoTIFF dosyası seçin.', 'error')
            return redirect(request.url)
        
        file = request.files['image']
        project_id = request.form.get('project_id')
        algorithm = request.form.get('algorithm', 'ndvi')
        colormap = request.form.get('colormap', 'rdylgn')
        min_range = float(request.form.get('min_range', -1.0))
        max_range = float(request.form.get('max_range', 1.0))
        
        if file.filename == '':
            flash('Dosya seçilmedi.', 'error')
            return redirect(request.url)
        
        if file and file.filename.lower().endswith(('.tif', '.tiff')):
            start_time = time.time()
            
            # Save uploaded file
            filename = secure_filename(file.filename)
            file_path = save_uploaded_file(file, filename)
            
            try:
                # Perform vegetation analysis
                analyzer = VegetationAnalyzer(file_path)
                analysis_result = analyzer.analyze(algorithm, (min_range, max_range), colormap)
                
                processing_time = time.time() - start_time
                
                # Save to database
                result = VegetationAnalysis(
                    image_path=file_path,
                    result_path=analysis_result.get('path'),
                    algorithm=algorithm,
                    colormap=colormap,
                    min_range=min_range,
                    max_range=max_range,
                    project_id=project_id if project_id else None
                )
                
                db.session.add(result)
                db.session.commit()
                
                flash(f'{VEGETATION_ALGORITHMS.get(algorithm, algorithm)} analizi tamamlandı!', 'success')
                
                return render_template('vegetation_result.html', 
                                     result=result,
                                     analysis_result=analysis_result,
                                     original_image=file_path,
                                     processing_time=processing_time)
                
            except Exception as e:
                flash(f'Analiz sırasında hata oluştu: {str(e)}', 'error')
                app.logger.error(f"Vegetation analysis error: {str(e)}")
        else:
            flash('Geçersiz dosya formatı. Lütfen GeoTIFF (.tif/.tiff) dosyası yükleyin.', 'error')
    
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('vegetation_analysis.html', 
                         projects=projects,
                         algorithms=VEGETATION_ALGORITHMS,
                         colormaps=COLORMAPS)

@mapping_bp.route('/interactive')
@login_required
def interactive_map():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Get recent analyses for map overlay
    analyses = VegetationAnalysis.query.join(Project)\
                                      .filter(Project.user_id == current_user.id)\
                                      .order_by(VegetationAnalysis.created_at.desc())\
                                      .all()
    
    return render_template('interactive_map.html', projects=projects, analyses=analyses)

@mapping_bp.route('/results')
@login_required
def results():
    page = request.args.get('page', 1, type=int)
    results = VegetationAnalysis.query.join(Project)\
                                     .filter(Project.user_id == current_user.id)\
                                     .order_by(VegetationAnalysis.created_at.desc())\
                                     .paginate(page=page, per_page=20, error_out=False)
    return render_template('vegetation_results.html', results=results)

@mapping_bp.route('/api/get_analysis/<int:analysis_id>')
@login_required
def get_analysis_data(analysis_id):
    analysis = VegetationAnalysis.query.join(Project)\
                                      .filter(VegetationAnalysis.id == analysis_id,
                                             Project.user_id == current_user.id)\
                                      .first_or_404()
    
    return jsonify({
        'id': analysis.id,
        'result_path': analysis.result_path,
        'algorithm': analysis.algorithm,
        'colormap': analysis.colormap,
        'min_range': analysis.min_range,
        'max_range': analysis.max_range,
        'created_at': analysis.created_at.isoformat()
    })

@mapping_bp.route('/geotiff_processing')
@login_required
def geotiff_processing():
    """GeoTIFF processing and histogram analysis page"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('geotiff_processing.html', projects=projects)

@mapping_bp.route('/geotiff_processing', methods=['POST'])
@login_required
def process_geotiff():
    """Process uploaded GeoTIFF files with advanced histogram analysis"""
    try:
        if 'geotiff_file' not in request.files:
            flash('Lütfen bir GeoTIFF dosyası seçin.', 'error')
            return redirect(url_for('mapping.geotiff_processing'))
        
        file = request.files['geotiff_file']
        if file.filename == '':
            flash('Dosya seçilmedi.', 'error')
            return redirect(url_for('mapping.geotiff_processing'))
        
        if file and file.filename.lower().endswith(('.tif', '.tiff')):
            # Save uploaded file
            filename = save_uploaded_file(file, app.config['UPLOAD_FOLDER'])
            if not filename:
                flash('Dosya yüklenirken hata oluştu.', 'error')
                return redirect(url_for('mapping.geotiff_processing'))
            
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            process_type = request.form.get('process_type', 'histogram')
            project_id = request.form.get('project_id')
            
            if process_type == 'histogram':
                # Advanced histogram analysis from uploaded files
                bins = int(request.form.get('bins', 256))
                result = process_geotiff_histogram(file_path, bins=bins)
                
                if result:
                    flash('GeoTIFF histogram analizi tamamlandı!', 'success')
                    return render_template('geotiff_histogram_result.html', 
                                         result=result, 
                                         original_file=file_path)
                else:
                    flash('Histogram analizi başarısız oldu.', 'error')
                    
            elif process_type == 'rgb_extract':
                # RGB extraction
                output_path = os.path.join(app.config['RESULTS_FOLDER'], 
                                         f'rgb_{os.path.splitext(filename)[0]}.png')
                rgb_result = extract_rgb_from_geotiff(file_path, output_path)
                
                if rgb_result:
                    flash('RGB çıkarma işlemi tamamlandı!', 'success')
                    return render_template('geotiff_rgb_result.html',
                                         rgb_path=rgb_result,
                                         original_file=file_path)
                else:
                    flash('RGB çıkarma başarısız oldu.', 'error')
                    
            elif process_type == 'vegetation':
                # Advanced vegetation analysis for GeoTIFF
                algorithm = request.form.get('algorithm', 'ndvi')
                output_dir = os.path.join(app.config['RESULTS_FOLDER'], 'vegetation_analysis')
                
                veg_result = analyze_vegetation_from_geotiff(file_path, algorithm, output_dir)
                
                if veg_result:
                    # Save to database
                    analysis = VegetationAnalysis(
                        image_path=file_path,
                        result_path=veg_result.get('colored_path'),
                        algorithm=algorithm,
                        colormap='rdylgn',
                        min_range=veg_result['statistics']['min'],
                        max_range=veg_result['statistics']['max'],
                        project_id=int(project_id) if project_id else None
                    )
                    
                    db.session.add(analysis)
                    db.session.commit()
                    
                    flash(f'{algorithm.upper()} vegetation analizi tamamlandı!', 'success')
                    return redirect(url_for('mapping.vegetation_result', result_id=analysis.id))
                else:
                    flash('Vegetation analizi başarısız oldu.', 'error')
            
            return redirect(url_for('mapping.geotiff_processing'))
        else:
            flash('Geçersiz dosya formatı. Sadece GeoTIFF (.tif/.tiff) dosyaları desteklenir.', 'error')
            return redirect(url_for('mapping.geotiff_processing'))
            
    except Exception as e:
        flash(f'İşlem sırasında hata oluştu: {str(e)}', 'error')
        app.logger.error(f"GeoTIFF processing error: {str(e)}")
        return redirect(url_for('mapping.geotiff_processing'))

@mapping_bp.route('/advanced_vegetation')
@login_required
def advanced_vegetation():
    """Advanced vegetation analysis with 15+ algorithms"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Get available algorithms from uploaded configurations
    algorithms = [
        ('ndvi', 'NDVI - Normalized Difference Vegetation Index'),
        ('gli', 'GLI - Green Leaf Index'),
        ('vari', 'VARI - Visible Atmospherically Resistant Index'),
        ('ndwi', 'NDWI - Normalized Difference Water Index'),
        ('savi', 'SAVI - Soil Adjusted Vegetation Index'),
        ('evi', 'EVI - Enhanced Vegetation Index'),
        ('tgi', 'TGI - Triangular Greenness Index'),
        ('msavi', 'MSAVI - Modified SAVI'),
        ('osavi', 'OSAVI - Optimized SAVI'),
        ('rdvi', 'RDVI - Renormalized Difference VI'),
        ('gndvi', 'GNDVI - Green NDVI'),
        ('cvi', 'CVI - Chlorophyll Vegetation Index'),
        ('arvi', 'ARVI - Atmospherically Resistant VI'),
        ('gci', 'GCI - Green Coverage Index')
    ]
    
    return render_template('advanced_vegetation.html', 
                         projects=projects, 
                         algorithms=algorithms)
