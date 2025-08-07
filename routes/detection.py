import os
import time
from typing import Optional, Dict, Any
from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app, jsonify
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
from models import DetectionResult, Project
from utils.ai_detection import detect_fruits, detect_leaf_disease, detect_trees
from utils.yolo_detection import detect_fruits_yolo, detect_leaf_disease_corn, detect_trees_from_drone
from utils.advanced_vegetation import analyze_vegetation_comprehensive
from utils.helpers import allowed_file, save_uploaded_file, validate_file_security
from utils.error_handlers import safe_db_commit, handle_errors
from app import db

detection_bp = Blueprint('detection', __name__)

# Fruit weights (kg)
FRUIT_WEIGHTS = {
    'mandalina': 0.125,
    'elma': 0.105,
    'armut': 0.220,
    'seftali': 0.185,
    'portakal': 0.150,
    'nar': 0.300,
    'hurma': 0.200
}

@detection_bp.route('/')
@login_required
def index():
    projects = Project.query.filter_by(user_id=current_user.id).all()
    recent_detections = DetectionResult.query.filter_by(user_id=current_user.id)\
                                           .order_by(DetectionResult.created_at.desc())\
                                           .limit(10).all()
    return render_template('detection.html', projects=projects, recent_detections=recent_detections)

@detection_bp.route('/fruit', methods=['GET', 'POST'])
@login_required
@handle_errors
def fruit_detection():
    if request.method == 'POST':
        # Type-safe file validation
        if 'image' not in request.files:
            flash('Lütfen bir görüntü seçin.', 'error')
            return redirect(request.url)
        
        file: FileStorage = request.files['image']
        project_id_str: Optional[str] = request.form.get('project_id')
        fruit_type: str = request.form.get('fruit_type', 'elma')
        
        # Comprehensive filename validation
        if not file or not file.filename or file.filename.strip() == '':
            flash('Dosya seçilmedi.', 'error')
            return redirect(request.url)
        
        # Enhanced security validation: MIME type + Magic number + Extension
        is_valid, security_error = validate_file_security(file, file.filename)
        if not is_valid:
            flash(f'Güvenlik hatası: {security_error}', 'error')
            return redirect(request.url)
        
        # Validate project_id if provided
        project_id: Optional[int] = None
        if project_id_str and project_id_str.strip():
            try:
                project_id = int(project_id_str.strip())
                # Verify user owns this project
                project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
                if not project:
                    flash('Geçersiz proje seçimi.', 'error')
                    return redirect(request.url)
            except (ValueError, TypeError):
                flash('Geçersiz proje ID\'si.', 'error')
                return redirect(request.url)
        
        # Validate fruit type
        if fruit_type not in FRUIT_WEIGHTS:
            fruit_type = 'elma'  # Default fallback
        
        # Secure filename handling with proper None check
        original_filename = file.filename.strip()
        if allowed_file(original_filename):
            start_time = time.time()
            
            # Save uploaded file with secure filename
            secure_name = secure_filename(original_filename)
            if not secure_name or secure_name == '':
                secure_name = f'upload_{int(time.time())}.jpg'
            file_path = save_uploaded_file(file, secure_name)
            
            try:
                # Perform fruit detection with enhanced error handling
                detection_result = detect_fruits(file_path, fruit_type)
                
                processing_time = time.time() - start_time
                
                # Calculate total weight with enhanced validation
                count = detection_result.get('count', 0)
                unit_weight = FRUIT_WEIGHTS.get(fruit_type, 0.15)
                total_weight = count * unit_weight
                
                # Enhanced feedback for detection results
                if count == 0:
                    flash(f'Görüntüde {fruit_type} tespit edilemedi. Görüntü kalitesini artırmayı veya farklı açıdan çekmeyi deneyin.', 'warning')
                else:
                    flash(f'Tespit tamamlandı! {count} adet {fruit_type} tespit edildi. Toplam ağırlık: {total_weight:.2f} kg', 'success')
                
                # Save to database with validated inputs
                result = DetectionResult(
                    image_path=file_path,
                    result_path=detection_result.get('result_path'),
                    detection_type='fruit',
                    fruit_type=fruit_type,
                    count=max(0, count),  # Ensure non-negative count
                    total_weight=max(0.0, total_weight),  # Ensure non-negative weight
                    confidence=max(0.0, min(1.0, detection_result.get('confidence', 0.0))),  # Clamp to [0,1]
                    processing_time=max(0.0, processing_time),
                    user_id=current_user.id,
                    project_id=project_id
                )
                
                db.session.add(result)
                db.session.commit()
                
                return render_template('detection_result.html', 
                                     result=result,
                                     detection_result=detection_result,
                                     original_image=file_path)
                
            except FileNotFoundError as file_error:
                current_app.logger.error(f"File not found during fruit detection: {str(file_error)}")
                flash('Dosya bulunamadı. Lütfen dosyayı tekrar yükleyin.', 'error')
                return redirect(url_for('detection.fruit_detection'))
                
            except ValueError as value_error:
                current_app.logger.error(f"Value error in fruit detection: {str(value_error)}")
                flash(f'Girdi doğrulama hatası: {str(value_error)}', 'error')
                return redirect(url_for('detection.fruit_detection'))
                
            except Exception as e:
                current_app.logger.error(f"Unexpected error in fruit detection: {str(e)}")
                flash('Meyve tespiti sırasında beklenmeyen hata oluştu. Lütfen tekrar deneyin.', 'error')
                return redirect(url_for('detection.fruit_detection'))
        else:
            flash('Geçersiz dosya formatı. Lütfen JPG, PNG veya JPEG dosyası yükleyin.', 'error')
    
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('fruit_detection.html', projects=projects)

@detection_bp.route('/leaf', methods=['GET', 'POST'])
@login_required
@handle_errors
def leaf_detection():
    if request.method == 'POST':
        # Type-safe file validation
        if 'image' not in request.files:
            flash('Lütfen bir görüntü seçin.', 'error')
            return redirect(request.url)
        
        file: FileStorage = request.files['image']
        project_id_str: Optional[str] = request.form.get('project_id')
        
        # Comprehensive filename validation
        if not file or not file.filename or file.filename.strip() == '':
            flash('Dosya seçilmedi.', 'error')
            return redirect(request.url)
        
        # Enhanced security validation: MIME type + Magic number + Extension
        is_valid, security_error = validate_file_security(file, file.filename)
        if not is_valid:
            flash(f'Güvenlik hatası: {security_error}', 'error')
            return redirect(request.url)
        
        # Validate project_id if provided
        project_id: Optional[int] = None
        if project_id_str and project_id_str.strip():
            try:
                project_id = int(project_id_str.strip())
                # Verify user owns this project
                project = Project.query.filter_by(id=project_id, user_id=current_user.id).first()
                if not project:
                    flash('Geçersiz proje seçimi.', 'error')
                    return redirect(request.url)
            except (ValueError, TypeError):
                flash('Geçersiz proje ID\'si.', 'error')
                return redirect(request.url)
        
        # Secure filename handling with proper None check
        original_filename = file.filename.strip()
        if allowed_file(original_filename):
            start_time = time.time()
            
            # Save uploaded file with secure filename
            secure_name = secure_filename(original_filename)
            if not secure_name or secure_name == '':
                secure_name = f'leaf_upload_{int(time.time())}.jpg'
            file_path = save_uploaded_file(file, secure_name)
            
            try:
                # Perform leaf disease detection with enhanced error handling
                detection_result = detect_leaf_disease(file_path)
                
                processing_time = time.time() - start_time
                
                # Enhanced feedback for detection results with Turkish localization
                disease_name = detection_result.get('name', 'Bilinmeyen')
                confidence = detection_result.get('confidence', 0.0)
                
                if confidence == 0.0 or not disease_name or disease_name == 'Bilinmeyen':
                    flash('Yaprak hastalığı tespit edilemedi. Görüntü kalitesini artırmayı veya farklı açıdan çekmeyi deneyin.', 'warning')
                else:
                    flash(f'Yaprak hastalık tespiti tamamlandı! Tespit edilen: {disease_name} (Güven: %{confidence*100:.1f})', 'success')
                
                # Save to database
                result = DetectionResult(
                    image_path=file_path,
                    result_path=detection_result.get('result_path'),
                    detection_type='leaf_disease',
                    fruit_type=disease_name,
                    confidence=max(0.0, min(1.0, confidence)),  # Clamp to [0,1]
                    processing_time=max(0.0, processing_time),
                    user_id=current_user.id,
                    project_id=project_id if project_id else None
                )
                
                db.session.add(result)
                db.session.commit()
                
                return render_template('leaf_detection_result.html', 
                                     result=result,
                                     detection_result=detection_result,
                                     original_image=file_path)
                
            except FileNotFoundError as file_error:
                current_app.logger.error(f"File not found during leaf detection: {str(file_error)}")
                flash('Dosya bulunamadı. Lütfen dosyayı tekrar yükleyin.', 'error')
                return redirect(url_for('detection.leaf_detection'))
                
            except ValueError as value_error:
                current_app.logger.error(f"Value error in leaf detection: {str(value_error)}")
                flash(f'Girdi doğrulama hatası: {str(value_error)}', 'error')
                return redirect(url_for('detection.leaf_detection'))
                
            except Exception as e:
                current_app.logger.error(f"Unexpected error in leaf detection: {str(e)}")
                flash('Yaprak hastalık tespiti sırasında beklenmeyen hata oluştu. Lütfen tekrar deneyin.', 'error')
                return redirect(url_for('detection.leaf_detection'))
        else:
            flash('Geçersiz dosya formatı. Lütfen JPG, PNG veya JPEG dosyası yükleyin.', 'error')
    
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('leaf_detection.html', projects=projects)

@detection_bp.route('/tree', methods=['GET', 'POST'])
@login_required
def tree_detection():
    if request.method == 'POST':
        if 'image' not in request.files:
            flash('Lütfen bir görüntü seçin.', 'error')
            return redirect(request.url)
        
        file = request.files['image']
        project_id = request.form.get('project_id')
        
        if file.filename == '':
            flash('Dosya seçilmedi.', 'error')
            return redirect(request.url)
        
        # Enhanced security validation: MIME type + Magic number + Extension
        is_valid, security_error = validate_file_security(file, file.filename)
        if not is_valid:
            flash(f'Güvenlik hatası: {security_error}', 'error')
            return redirect(request.url)
        
        if file and allowed_file(file.filename):
            start_time = time.time()
            
            # Save uploaded file
            filename = secure_filename(file.filename or 'upload.jpg')
            file_path = save_uploaded_file(file, filename)
            
            try:
                # Perform tree detection
                detection_result = detect_trees(file_path)
                
                processing_time = time.time() - start_time
                
                # Save to database
                result = DetectionResult(
                    image_path=file_path,
                    result_path=detection_result.get('result_path'),
                    detection_type='tree',
                    fruit_type=detection_result.get('name'),
                    confidence=detection_result.get('confidence', 0.0),
                    processing_time=processing_time,
                    user_id=current_user.id,
                    project_id=project_id if project_id else None
                )
                
                db.session.add(result)
                db.session.commit()
                
                flash('Ağaç tespiti tamamlandı!', 'success')
                
                return render_template('tree_detection_result.html', 
                                     result=result,
                                     detection_result=detection_result,
                                     original_image=file_path)
                
            except Exception as e:
                flash(f'Tespit sırasında hata oluştu: {str(e)}', 'error')
                current_app.logger.error(f"Tree detection error: {str(e)}")
        else:
            flash('Geçersiz dosya formatı. Lütfen JPG, PNG veya JPEG dosyası yükleyin.', 'error')
    
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('tree_detection.html', projects=projects)

@detection_bp.route('/results')
@login_required
def results():
    page = request.args.get('page', 1, type=int)
    results = DetectionResult.query.filter_by(user_id=current_user.id)\
                                  .order_by(DetectionResult.created_at.desc())\
                                  .paginate(page=page, per_page=20, error_out=False)
    return render_template('detection_results.html', results=results)

@detection_bp.route('/advanced_multi_detection')
@login_required
def advanced_multi_detection():
    """Advanced multi-fruit detection page"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    return render_template('advanced_multi_detection.html', projects=projects)

@detection_bp.route('/advanced_multi_detection', methods=['POST'])
@login_required 
def process_advanced_multi_detection():
    """Process advanced multi-fruit detection"""
    try:
        if 'image' not in request.files:
            flash('Lütfen bir görüntü dosyası seçin.', 'error')
            return redirect(url_for('detection.advanced_multi_detection'))
        
        file = request.files['image']
        if file.filename == '':
            flash('Dosya seçilmedi.', 'error')
            return redirect(url_for('detection.advanced_multi_detection'))
        
        # Enhanced security validation: MIME type + Magic number + Extension
        is_valid, security_error = validate_file_security(file, file.filename)
        if not is_valid:
            flash(f'Güvenlik hatası: {security_error}', 'error')
            return redirect(url_for('detection.advanced_multi_detection'))
        
        if file and allowed_file(file.filename):
            # Fix: Proper file saving
            filename = secure_filename(file.filename or 'upload.jpg')
            file_path = save_uploaded_file(file, filename)
            
            # Check if file was actually saved
            if not file_path or not os.path.exists(file_path):
                flash('Dosya yüklenirken hata oluştu.', 'error')
                return redirect(url_for('detection.advanced_multi_detection'))
            
            try:
                # Get form parameters with validation
                confidence = float(request.form.get('confidence', 25)) / 100
                detection_mode = request.form.get('detection_mode', 'all')
                project_id = request.form.get('project_id')
                
                # Advanced fruit detection using uploaded algorithms
                if detection_mode == 'custom':
                    selected_fruits = request.form.getlist('fruits')
                    fruit_type = ','.join(selected_fruits) if selected_fruits else 'mixed'
                else:
                    fruit_type = detection_mode
                
                # Process detection with cleanup
                detection_result = detect_fruits_yolo(
                    file_path, 
                    confidence=confidence,
                    fruit_type=fruit_type
                )
                
                if detection_result:
                    result = DetectionResult(
                        image_path=file_path,
                        detection_type='advanced_multi_fruit',
                        fruit_type=fruit_type,
                        count=detection_result['total_count'],
                        total_weight=detection_result['total_weight'],
                        confidence=detection_result['confidence'],
                        processing_time=detection_result['processing_time'],
                        user_id=current_user.id,
                        project_id=int(project_id) if project_id else None
                    )
                    
                    db.session.add(result)
                    if safe_db_commit():
                        flash(f'{detection_result["total_count"]} adet meyve tespit edildi!', 'success')
                        return redirect(url_for('detection.results'))
                    else:
                        flash('Veritabanı hatası oluştu.', 'error')
                else:
                    flash('Tespit işlemi başarısız oldu.', 'error')
                    
            except Exception as e:
                current_app.logger.error(f'Detection error: {str(e)}')
                flash(f'İşlem sırasında hata oluştu: {str(e)}', 'error')
            finally:
                # Cleanup temporary files if needed
                if os.path.exists(file_path) and file_path.startswith('/tmp/'):
                    try:
                        os.remove(file_path)
                    except:
                        pass
        else:
            flash('Geçersiz dosya formatı.', 'error')
            
    except Exception as e:
        current_app.logger.error(f'Detection error: {str(e)}')
        flash(f'İşlem sırasında hata oluştu: {str(e)}', 'error')
    
    return redirect(url_for('detection.advanced_multi_detection'))
