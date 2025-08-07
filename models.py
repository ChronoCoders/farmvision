from app import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Float, Boolean, ForeignKey
from sqlalchemy.orm import relationship

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    username = Column(String(80), unique=True, nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(256), nullable=False)
    first_name = Column(String(50))
    last_name = Column(String(50))
    phone = Column(String(20))
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    projects = relationship('Project', backref='owner', lazy=True, cascade='all, delete-orphan')
    detection_results = relationship('DetectionResult', backref='user', lazy=True)
    
    def __init__(self, username=None, email=None, password_hash=None, first_name=None, 
                 last_name=None, phone=None, is_active=True):
        self.username = username
        self.email = email
        self.password_hash = password_hash
        self.first_name = first_name
        self.last_name = last_name
        self.phone = phone
        self.is_active = is_active

class Project(db.Model):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    farm_name = Column(String(100))
    field_name = Column(String(100))
    location = Column(String(200))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    
    # Relationships
    detection_results = relationship('DetectionResult', backref='project', lazy=True)
    vegetation_analyses = relationship('VegetationAnalysis', backref='project', lazy=True)
    
    def __init__(self, title=None, description=None, farm_name=None, field_name=None, 
                 location=None, user_id=None):
        self.title = title
        self.description = description
        self.farm_name = farm_name
        self.field_name = field_name
        self.location = location
        self.user_id = user_id

class DetectionResult(db.Model):
    __tablename__ = 'detection_results'
    
    id = Column(Integer, primary_key=True)
    image_path = Column(String(500), nullable=False)
    result_path = Column(String(500))
    detection_type = Column(String(50))  # 'fruit', 'leaf_disease', 'tree'
    fruit_type = Column(String(50))
    count = Column(Integer, default=0)
    total_weight = Column(Float, default=0.0)
    confidence = Column(Float)
    processing_time = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_id = Column(Integer, ForeignKey('projects.id'))
    
    def __init__(self, image_path=None, result_path=None, detection_type=None, 
                 fruit_type=None, count=0, total_weight=0.0, confidence=None, 
                 processing_time=None, user_id=None, project_id=None):
        self.image_path = image_path
        self.result_path = result_path
        self.detection_type = detection_type
        self.fruit_type = fruit_type
        self.count = count
        self.total_weight = total_weight
        self.confidence = confidence
        self.processing_time = processing_time
        self.user_id = user_id
        self.project_id = project_id

class VegetationAnalysis(db.Model):
    __tablename__ = 'vegetation_analyses'
    
    id = Column(Integer, primary_key=True)
    image_path = Column(String(500), nullable=False)
    result_path = Column(String(500))
    algorithm = Column(String(50))  # 'ndvi', 'gli', 'vari', etc.
    colormap = Column(String(50))
    min_range = Column(Float)
    max_range = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    project_id = Column(Integer, ForeignKey('projects.id'))
    
    def __init__(self, image_path=None, result_path=None, algorithm=None, 
                 colormap=None, min_range=None, max_range=None, project_id=None):
        self.image_path = image_path
        self.result_path = result_path
        self.algorithm = algorithm
        self.colormap = colormap
        self.min_range = min_range
        self.max_range = max_range
        self.project_id = project_id
