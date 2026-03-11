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
    __tablename__ = "citizens"
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Officer Registration Table
class Officer(db.Model):
    __tablename__ = "officers"

    id = db.Column(db.Integer, primary_key=True)
    officer_id = db.Column(db.String(50), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    department = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(15))
    password = db.Column(db.String(100), nullable=False)
    approval_status = db.Column(db.String(20), default="approved")

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
    role = db.Column(db.String(20), nullable=False)  # citizen, officer, worker, admin
    id_proof = db.Column(db.String(200), nullable=True)

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
    deadline = db.Column(db.DateTime)

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    complaint_id = db.Column(db.Integer, db.ForeignKey('complaint.id'), nullable=False)
    worker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_by = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow)

class Worker(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    worker_id = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(10), nullable=False)

def create_default_workers():
    workers = [
        {"worker_id":"W101","name":"Ramesh Kumar","department":"Sanitation","contact":"9876543210"},
        {"worker_id":"W102","name":"Suresh Patil","department":"Electricity","contact":"9876543211"},
        {"worker_id":"W103","name":"Anil Sharma","department":"Road Maintenance","contact":"9876543212"},
        {"worker_id":"W104","name":"Ravi Verma","department":"Water Supply","contact":"9876543213"},
        {"worker_id":"W105","name":"Sunil Gupta","department":"Sanitation","contact":"9876543214"}
    ]

    for worker in workers:
        existing_worker = Worker.query.filter_by(worker_id=worker["worker_id"]).first()
        if not existing_worker:
            new_worker = Worker(
                worker_id=worker["worker_id"],
                name=worker["name"],
                department=worker["department"],
                contact_number=worker["contact"]
            )
            db.session.add(new_worker)
    db.session.commit()
