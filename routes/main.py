from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app
from flask_login import login_required, current_user
from models import Project, DetectionResult, VegetationAnalysis
from app import db
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

@main_bp.route('/projects/<int:project_id>')
@login_required
def project_detail(project_id):
    """Detailed project view with analytics and management"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    # Get project statistics
    detection_stats = {
        'total_detections': len(project.detection_results),
        'total_vegetation': len(project.vegetation_analyses),
        'avg_confidence': 0,
        'fruit_counts': {}
    }
    
    # Calculate authentic detection statistics
    if project.detection_results:
        confidences = [d.confidence for d in project.detection_results if d.confidence is not None]
        if confidences:
            detection_stats['avg_confidence'] = sum(confidences) / len(confidences)
        
        # Count fruits by type
        for detection in project.detection_results:
            if detection.fruit_type:
                detection_stats['fruit_counts'][detection.fruit_type] = detection_stats['fruit_counts'].get(detection.fruit_type, 0) + detection.count
    
    # Recent activity timeline
    recent_activity = []
    for detection in project.detection_results[-10:]:
        recent_activity.append({
            'type': 'detection',
            'description': f'{detection.fruit_type or "Genel"} tespiti ({detection.count} adet)',
            'timestamp': detection.created_at,
            'confidence': detection.confidence
        })
    
    for analysis in project.vegetation_analyses[-10:]:
        recent_activity.append({
            'type': 'analysis',
            'description': f'{analysis.algorithm.upper()} bitki örtüsü analizi',
            'timestamp': analysis.created_at,
            'algorithm': analysis.algorithm
        })
    
    # Sort by timestamp
    recent_activity.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return render_template('project_detail.html', 
                         project=project,
                         detection_stats=detection_stats,
                         recent_activity=recent_activity[:15])

@main_bp.route('/projects/<int:project_id>/edit', methods=['GET', 'POST'])
@login_required  
def edit_project(project_id):
    """Edit project details"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    if request.method == 'POST':
        project.title = request.form.get('title', '').strip()
        project.description = request.form.get('description', '').strip()
        project.farm_name = request.form.get('farm_name', '').strip()
        project.field_name = request.form.get('field_name', '').strip()
        project.location = request.form.get('location', '').strip()
        
        if not project.title:
            flash('Proje başlığı gereklidir.', 'error')
            return render_template('edit_project.html', project=project)
        
        try:
            project.updated_at = datetime.utcnow()
            db.session.commit()
            flash('Proje başarıyla güncellendi.', 'success')
            return redirect(url_for('main.project_detail', project_id=project.id))
        except Exception as e:
            db.session.rollback()
            flash('Proje güncellenirken bir hata oluştu.', 'error')
            return render_template('edit_project.html', project=project)
    
    return render_template('edit_project.html', project=project)

@main_bp.route('/projects/<int:project_id>/delete', methods=['POST'])
@login_required
def delete_project(project_id):
    """Delete project and all associated data"""
    project = Project.query.filter_by(id=project_id, user_id=current_user.id).first_or_404()
    
    try:
        # Clean up associated files
        for detection in project.detection_results:
            if detection.result_path and os.path.exists(detection.result_path):
                os.remove(detection.result_path)
        
        for analysis in project.vegetation_analyses:
            if analysis.result_path and os.path.exists(analysis.result_path):
                os.remove(analysis.result_path)
        
        project_title = project.title
        db.session.delete(project)
        db.session.commit()
        
        flash(f'Proje "{project_title}" başarıyla silindi.', 'success')
        return redirect(url_for('main.projects'))
        
    except Exception as e:
        db.session.rollback()
        flash('Proje silinirken bir hata oluştu.', 'error')
        return redirect(url_for('main.project_detail', project_id=project.id))

@main_bp.route('/projects/new', methods=['GET', 'POST'])
@login_required
def new_project():
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        description = request.form.get('description', '').strip()
        farm_name = request.form.get('farm_name', '').strip()
        field_name = request.form.get('field_name', '').strip()
        location = request.form.get('location', '').strip()
        
        if not title:
            flash('Proje başlığı gereklidir.', 'error')
            return render_template('new_project.html')
        
        project = Project()
        project.title = title
        project.description = description
        project.farm_name = farm_name
        project.field_name = field_name
        project.location = location
        project.user_id = current_user.id
        
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

@main_bp.route('/analytics')
@login_required
def analytics_dashboard():
    """Comprehensive analytics dashboard with authentic data only"""
    try:
        # Calculate real analytics from user's authentic data
        user_projects = Project.query.filter_by(user_id=current_user.id).all()
        all_detections = DetectionResult.query.filter_by(user_id=current_user.id).all()
        
        analytics = {
            'total_yield': sum(d.total_weight for d in all_detections if d.total_weight),
            'avg_confidence': sum(d.confidence for d in all_detections if d.confidence) / len([d for d in all_detections if d.confidence]) if any(d.confidence for d in all_detections) else 0,
            'active_fields': len(set(p.field_name for p in user_projects if p.field_name)),
            'health_score': 0,  # Will be calculated from vegetation analyses
            'weekly_data': [],
            'fruit_distribution': {}
        }
        
        # Calculate fruit distribution from authentic data
        for detection in all_detections:
            if detection.fruit_type:
                analytics['fruit_distribution'][detection.fruit_type] = analytics['fruit_distribution'].get(detection.fruit_type, 0) + detection.count
        
        # Weekly trend data (last 7 days)
        for i in range(7):
            date = datetime.now() - timedelta(days=6-i)
            day_detections = len([d for d in all_detections if d.created_at.date() == date.date()])
            analytics['weekly_data'].append({
                'date': date.strftime('%d.%m'),
                'detections': day_detections
            })
        
        # Vegetation analysis statistics (authentic only)
        vegetation_stats = {}
        for project in user_projects:
            for analysis in project.vegetation_analyses:
                if analysis.algorithm not in vegetation_stats:
                    vegetation_stats[analysis.algorithm] = {
                        'values': [],
                        'avg_value': 0,
                        'min_value': 0,
                        'max_value': 0
                    }
                
                # In a real implementation, this would read actual analysis results
                # For now, we store the range values as placeholders for real data
                if analysis.min_range is not None and analysis.max_range is not None:
                    avg_val = (analysis.min_range + analysis.max_range) / 2
                    vegetation_stats[analysis.algorithm]['values'].append(avg_val)
        
        # Calculate vegetation stats from authentic data
        for alg, stats in vegetation_stats.items():
            if stats['values']:
                stats['avg_value'] = sum(stats['values']) / len(stats['values'])
                stats['min_value'] = min(stats['values'])
                stats['max_value'] = max(stats['values'])
        
        # Recent performance metrics (authentic data)
        recent_metrics = DetectionResult.query.filter_by(user_id=current_user.id)\
                                            .order_by(DetectionResult.created_at.desc())\
                                            .limit(20).all()
        
        return render_template('analytics_dashboard.html',
                             analytics=analytics,
                             vegetation_stats=vegetation_stats,
                             recent_metrics=recent_metrics)
                             
    except Exception as e:
        flash('Analitik verileri yüklenirken hata oluştu.', 'error')
        return redirect(url_for('main.dashboard'))

@main_bp.route('/reports')
@login_required
def reports():
    """Reports generation and management page"""
    projects = Project.query.filter_by(user_id=current_user.id).all()
    
    # Recent reports (would be stored in database in full implementation)
    recent_reports = []  # Only authentic reports will be shown
    
    return render_template('reports.html', projects=projects, recent_reports=recent_reports)

@main_bp.route('/generate_report', methods=['POST'])
@login_required
def generate_report():
    """Generate comprehensive agricultural reports from authentic data"""
    try:
        report_type = request.form.get('report_type')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        project_id = request.form.get('project_id')
        
        if not start_date or not end_date:
            flash('Başlangıç ve bitiş tarihi gereklidir.', 'error')
            return redirect(url_for('main.reports'))
        
        # Convert date strings to datetime objects
        from datetime import datetime
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        if report_type == 'fruit_detection':
            return generate_fruit_detection_report(start_dt, end_dt, project_id)
        elif report_type == 'vegetation_analysis':
            return generate_vegetation_report(start_dt, end_dt, project_id)
        elif report_type == 'comprehensive':
            return generate_comprehensive_report(start_dt, end_dt, project_id)
        else:
            flash('Geçersiz rapor türü.', 'error')
            return redirect(url_for('main.reports'))
            
    except Exception as e:
        flash(f'Rapor oluşturulurken hata oluştu: {str(e)}', 'error')
        return redirect(url_for('main.reports'))

def generate_fruit_detection_report(start_date, end_date, project_id):
    """Generate fruit detection report from authentic data only"""
    try:
        # Query authentic detection results
        query = DetectionResult.query.filter(
            DetectionResult.user_id == current_user.id,
            DetectionResult.created_at >= start_date,
            DetectionResult.created_at <= end_date
        )
        
        if project_id:
            query = query.filter(DetectionResult.project_id == project_id)
        
        detections = query.all()
        
        if not detections:
            flash('Seçilen tarih aralığında tespit verisi bulunamadı.', 'warning')
            return redirect(url_for('main.reports'))
        
        # Generate report data
        report_data = {
            'title': 'Meyve Tespit Raporu',
            'period': f'{start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}',
            'total_detections': len(detections),
            'total_fruits': sum(d.count for d in detections),
            'total_weight': sum(d.total_weight for d in detections if d.total_weight),
            'avg_confidence': sum(d.confidence for d in detections if d.confidence) / len([d for d in detections if d.confidence]) if any(d.confidence for d in detections) else 0,
            'fruit_breakdown': {},
            'detections': detections
        }
        
        # Calculate fruit type breakdown
        for detection in detections:
            if detection.fruit_type:
                if detection.fruit_type not in report_data['fruit_breakdown']:
                    report_data['fruit_breakdown'][detection.fruit_type] = {
                        'count': 0,
                        'weight': 0,
                        'detections': 0
                    }
                report_data['fruit_breakdown'][detection.fruit_type]['count'] += detection.count
                report_data['fruit_breakdown'][detection.fruit_type]['weight'] += detection.total_weight or 0
                report_data['fruit_breakdown'][detection.fruit_type]['detections'] += 1
        
        return render_template('fruit_detection_report.html', report=report_data)
        
    except Exception as e:
        flash(f'Meyve tespit raporu oluşturulamadı: {str(e)}', 'error')
        return redirect(url_for('main.reports'))

def generate_vegetation_report(start_date, end_date, project_id):
    """Generate vegetation analysis report from authentic data only"""
    try:
        # Query authentic vegetation analyses
        from models import VegetationAnalysis
        query = VegetationAnalysis.query.join(Project).filter(
            Project.user_id == current_user.id,
            VegetationAnalysis.created_at >= start_date,
            VegetationAnalysis.created_at <= end_date
        )
        
        if project_id:
            query = query.filter(VegetationAnalysis.project_id == project_id)
            
        analyses = query.all()
        
        if not analyses:
            flash('Seçilen tarih aralığında bitki örtüsü analizi bulunamadı.', 'warning')
            return redirect(url_for('main.reports'))
        
        report_data = {
            'title': 'Bitki Örtüsü Analiz Raporu',
            'period': f'{start_date.strftime("%d.%m.%Y")} - {end_date.strftime("%d.%m.%Y")}',
            'total_analyses': len(analyses),
            'algorithms_used': list(set(a.algorithm for a in analyses)),
            'analyses': analyses,
            'algorithm_stats': {}
        }
        
        # Calculate algorithm statistics
        for analysis in analyses:
            if analysis.algorithm not in report_data['algorithm_stats']:
                report_data['algorithm_stats'][analysis.algorithm] = {
                    'count': 0,
                    'avg_min': [],
                    'avg_max': []
                }
            report_data['algorithm_stats'][analysis.algorithm]['count'] += 1
            if analysis.min_range is not None:
                report_data['algorithm_stats'][analysis.algorithm]['avg_min'].append(analysis.min_range)
            if analysis.max_range is not None:
                report_data['algorithm_stats'][analysis.algorithm]['avg_max'].append(analysis.max_range)
        
        return render_template('vegetation_report.html', report=report_data)
        
    except Exception as e:
        flash(f'Bitki örtüsü raporu oluşturulamadı: {str(e)}', 'error')
        return redirect(url_for('main.reports'))

def generate_comprehensive_report(start_date, end_date, project_id):
    """Generate comprehensive agricultural report combining all authentic data"""
    flash('Kapsamlı rapor oluşturma özelliği geliştiriliyor.', 'info')
    return redirect(url_for('main.reports'))

@main_bp.route('/robots.txt')
def robots_txt():
    """Serve robots.txt for SEO"""
    from flask import send_from_directory
    return send_from_directory('static', 'robots.txt', mimetype='text/plain')



@main_bp.route('/health')
def health_check():
    """Application health check"""
    try:
        # Check database connection
        from sqlalchemy import text
        db.session.execute(text('SELECT 1'))
        
        # Check required directories
        required_dirs = [current_app.config['UPLOAD_FOLDER'], current_app.config['RESULTS_FOLDER']]
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
