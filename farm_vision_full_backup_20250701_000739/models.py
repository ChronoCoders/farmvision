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
