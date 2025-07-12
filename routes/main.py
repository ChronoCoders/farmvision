from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from models import Project, DetectionResult, VegetationAnalysis
from app import db, app
import time
import os
from datetime import datetime, timedelta

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        # Get user statistics
        total_projects = Project.query.filter_by(user_id=current_user.id).count()
        total_detections = DetectionResult.query.filter_by(user_id=current_user.id).count()
        recent_projects = Project.query.filter_by(user_id=current_user.id).order_by(Project.updated_at.desc()).limit(5).all()
        
        return render_template('index.html', 
                             total_projects=total_projects,
                             total_detections=total_detections,
                             recent_projects=recent_projects)
    else:
        return render_template('index.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    # Get comprehensive user statistics
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    stats = {
        'total_projects': len(projects),
        'total_detections': DetectionResult.query.filter_by(user_id=current_user.id).count(),
        'total_vegetation_analyses': VegetationAnalysis.query.join(Project).filter(Project.user_id == current_user.id).count(),
        'recent_activities': []
    }
    
    # Recent detection results
    recent_detections = DetectionResult.query.filter_by(user_id=current_user.id)\
                                           .order_by(DetectionResult.created_at.desc())\
                                           .limit(10).all()
    
    # Activity data for chart - only authentic data
    activity_data = []
    for i in range(7):
        date = datetime.now() - timedelta(days=6-i)
        day_detections = DetectionResult.query.filter_by(user_id=current_user.id)\
                                            .filter(DetectionResult.created_at >= date.replace(hour=0, minute=0, second=0, microsecond=0))\
                                            .filter(DetectionResult.created_at < date.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1))\
                                            .count()
        activity_data.append(day_detections)
    
    return render_template('dashboard.html', stats=stats, 
                         projects=projects, recent_detections=recent_detections,
                         activity_data=activity_data)

@main_bp.route('/projects')
@login_required
def projects():
    user_projects = Project.query.filter_by(user_id=current_user.id)\
                                .order_by(Project.updated_at.desc()).all()
    return render_template('projects.html', projects=user_projects)

@main_bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title')
        description = request.form.get('description')
        farm_name = request.form.get('farm_name')
        field_name = request.form.get('field_name')
        location = request.form.get('location')
        
        if not title:
            flash('Proje başlığı gereklidir.', 'error')
            return render_template('new_project.html')
        
        project = Project(
            title=title,
            description=description,
            farm_name=farm_name,
            field_name=field_name,
            location=location,
            user_id=current_user.id
        )
        
        db.session.add(project)
        db.session.commit()
        
        flash('Proje başarıyla oluşturuldu.', 'success')
        return redirect(url_for('main.projects'))
    
    return render_template('new_project.html')

@main_bp.route('/ai_status')
@login_required
def ai_status():
    """AI System Status page showing real YOLO model information"""
    try:
        from utils.real_yolo_inference import yolo_engine
        ai_info = yolo_engine.get_model_info()
    except Exception as e:
        ai_info = {
            'device': 'CPU',
            'loaded_models': [],
            'cuda_available': False,
            'error': str(e)
        }
    
    return render_template('ai_system_status.html', ai_info=ai_info)

@main_bp.route('/robots.txt')
def robots_txt():
    """Serve robots.txt for SEO"""
    from flask import send_from_directory
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')

@main_bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    # Get project statistics
    detections = DetectionResult.query.filter_by(project_id=project_id).all()
    vegetation_analyses = VegetationAnalysis.query.filter_by(project_id=project_id).all()
    
    return render_template('project_detail.html', project=project,
                         detections=detections, vegetation_analyses=vegetation_analyses)

@main_bp.route('/health')
def health_check():
    """Application health check"""
    try:
        # Check database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        # Check required directories
        required_dirs = [app.config['UPLOAD_FOLDER'], app.config['RESULTS_FOLDER']]
        for directory in required_dirs:
            if not os.path.exists(directory):
                os.makedirs(directory)
        
        return jsonify({
            'status': 'healthy',
            'timestamp': time.time(),
            'database': 'connected',
            'version': '1.0.0'
        }), 200
    except Exception as e:
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': time.time()
        }), 503
