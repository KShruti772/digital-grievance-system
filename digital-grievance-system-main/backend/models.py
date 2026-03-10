from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

# Valid Officers Table - Stores pre-approved officer IDs
class ValidOfficer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.String(50), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Citizen Registration Table
class Citizen(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Officer Registration Table
class Officer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.String(50), unique=True, nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Legacy User Model - for compatibility with existing complaint system
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(20), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    employee_id = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(20), default="citizen", nullable=False)  # citizen, officer, worker, admin

class Complaint(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    location = db.Column(db.String(200), nullable=False)
    location_link = db.Column(db.String(500), nullable=True)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    image_path = db.Column(db.String(200))
    estimated_resolution_days = db.Column(db.Integer)  # random days estimate
    status = db.Column(db.String(20), default='Pending')
    priority = db.Column(db.String(20), default='Medium')  # High, Medium, Low
    worker_name = db.Column(db.String(100), nullable=True)
    worker_contact = db.Column(db.String(20), nullable=True)
    estimated_resolution_time = db.Column(db.String(50), nullable=True)
    assigned_officer = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    escalation_level = db.Column(db.Integer, default=0)  # 0=Normal, 1=Escalated, 2=High Priority
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)
