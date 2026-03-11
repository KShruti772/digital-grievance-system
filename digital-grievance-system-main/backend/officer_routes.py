from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Complaint, Assignment, User, Officer
from sqlalchemy import func
from datetime import datetime
import json

officer = Blueprint('officer', __name__, url_prefix='/officer')

def check_escalations():
    """Check and escalate complaints based on time pending and deadline"""
    complaints = Complaint.query.filter_by(status="Pending").all()
    
    for complaint in complaints:
        days_pending = (datetime.utcnow() - complaint.created_at).days
        
        if days_pending > 2 and complaint.escalation_level == 0:
            complaint.escalation_level = 1
        elif days_pending > 5 and complaint.escalation_level == 1:
            complaint.escalation_level = 2
        
        # Check deadline
        if complaint.deadline and datetime.utcnow() > complaint.deadline:
            complaint.status = "Escalated"
    
    db.session.commit()

@officer.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'officer':
        flash('Please login as an officer first', 'warning')
        return redirect(url_for('auth.officer_login'))
    
    # Check for escalations
    check_escalations()
    
    # Get the logged-in officer's department from User table
    current_user = User.query.get(session['user_id'])
    officer_department = current_user.department if current_user else None
    
    category = request.args.get('category')
    status = request.args.get('status')
    
    query = Complaint.query
    
    # Filter by officer's department
    if officer_department:
        query = query.filter_by(category=officer_department)
    
    if category and category != '':
        query = query.filter_by(category=category)
    if status and status != '':
        query = query.filter_by(status=status)
    
    complaints = query.order_by(
        Complaint.escalation_level.desc(),
        db.case(
            (Complaint.priority == 'High', 1),
            (Complaint.priority == 'Medium', 2),
            (Complaint.priority == 'Low', 3),
            else_=4
        ),
        Complaint.created_at.asc()
    ).all()
    
    workers = User.query.filter_by(role='worker').all()
    
    # Get citizen information for each complaint
    complaint_citizens = {}
    for complaint in complaints:
        citizen = User.query.get(complaint.user_id)
        complaint_citizens[complaint.id] = citizen
    
    # Get worker assignments for complaints
    complaint_workers = {}
    assignments = Assignment.query.all()
    for assignment in assignments:
        complaint_workers[assignment.complaint_id] = User.query.get(assignment.worker_id)
    
    # Get assigned officers for complaints
    complaint_officers = {}
    for complaint in complaints:
        if complaint.assigned_officer:
            officer = User.query.get(complaint.assigned_officer)
            complaint_officers[complaint.id] = officer
    
    # Get unique categories and statuses for filters
    categories = db.session.query(Complaint.category).distinct().all()
    categories = [cat[0] for cat in categories]
    statuses = ['Pending', 'Assigned', 'In Progress', 'Resolved']
    
    return render_template('officer_dashboard.html', 
                         complaints=complaints, 
                         workers=workers,
                         categories=categories,
                         statuses=statuses,
                         complaint_citizens=complaint_citizens,
                         complaint_workers=complaint_workers,
                         complaint_officers=complaint_officers,
                         officer_department=officer_department)

@officer.route('/assign/<int:complaint_id>', methods=['POST'])
def assign(complaint_id):
    if 'user_id' not in session or session.get('role') != 'officer':
        flash('Please login as an officer first', 'warning')
        return redirect(url_for('auth.officer_login'))
    
    worker_id = request.form.get('worker_id')
    worker_name = request.form.get('worker_name')
    worker_contact = request.form.get('worker_contact')
    estimated_time = request.form.get('estimated_time')
    
    if not worker_id:
        flash('Please select a worker', 'danger')
        return redirect(url_for('officer.dashboard'))
    
    if not worker_name or not worker_contact or not estimated_time:
        flash('Please provide all worker details', 'danger')
        return redirect(url_for('officer.dashboard'))
    
    assignment = Assignment(
        complaint_id=complaint_id,
        worker_id=int(worker_id),
        assigned_by=session['user_id']
    )
    db.session.add(assignment)
    
    complaint = Complaint.query.get(complaint_id)
    complaint.status = 'Assigned'
    complaint.worker_name = worker_name
    complaint.worker_contact = worker_contact
    complaint.estimated_resolution_time = estimated_time
    complaint.assigned_officer = session['user_id']
    complaint.last_updated = datetime.utcnow()
    
    db.session.commit()
    flash('Complaint assigned successfully with worker details!', 'success')
    return redirect(url_for('officer.dashboard'))

@officer.route('/update_status/<int:complaint_id>', methods=['POST'])
def update_status(complaint_id):
    if 'user_id' not in session or session.get('role') != 'officer':
        flash('Please login as an officer first', 'warning')
        return redirect(url_for('auth.officer_login'))
    
    status = request.form.get('status')
    complaint = Complaint.query.get(complaint_id)
    
    if complaint:
        complaint.status = status
        complaint.last_updated = datetime.utcnow()
        db.session.commit()
        flash('Status updated successfully!', 'success')
    else:
        flash('Complaint not found', 'danger')
    
    return redirect(url_for('officer.dashboard'))

@officer.route('/update_complaint/<int:complaint_id>', methods=['POST'])
def update_complaint(complaint_id):
    """Comprehensive route to update complaint details"""
    if 'user_id' not in session or session.get('role') != 'officer':
        flash('Please login as an officer first', 'warning')
        return redirect(url_for('auth.officer_login'))
    
    complaint = Complaint.query.get(complaint_id)
    if not complaint:
        flash('Complaint not found', 'danger')
        return redirect(url_for('officer.dashboard'))
    
    # Update complaint fields from form data
    if request.form.get('status'):
        complaint.status = request.form.get('status')
    
    if request.form.get('worker_name'):
        complaint.worker_name = request.form.get('worker_name')
    
    if request.form.get('worker_contact'):
        complaint.worker_contact = request.form.get('worker_contact')
    
    if request.form.get('resolution_time'):
        complaint.estimated_resolution_time = request.form.get('resolution_time')
    
    if request.form.get('priority'):
        complaint.priority = request.form.get('priority')
    
    # Always update the last_updated timestamp
    complaint.last_updated = datetime.utcnow()
    complaint.assigned_officer = session['user_id']
    
    db.session.commit()
    flash('Complaint updated successfully!', 'success')
    return redirect(url_for('officer.dashboard'))

@officer.route('/complaint/<int:complaint_id>')
def complaint_details(complaint_id):
    if 'user_id' not in session or session.get('role') != 'officer':
        flash('Please login as an officer first', 'warning')
        return redirect(url_for('auth.officer_login'))
    
    complaint = Complaint.query.get(complaint_id)
    citizen = User.query.get(complaint.user_id)
    assignment = Assignment.query.filter_by(complaint_id=complaint_id).first()
    worker = None
    
    if assignment:
        worker = User.query.get(assignment.worker_id)
    
    return render_template('complaint_details.html', 
                         complaint=complaint, 
                         citizen=citizen,
                         worker=worker)

@officer.route('/analytics/status')
def get_status_analytics():
    if 'user_id' not in session or session.get('role') != 'officer':
        return {'error': 'Unauthorized'}, 401
    
    # Get complaint counts by status
    status_counts = db.session.query(Complaint.status, func.count(Complaint.id)).group_by(Complaint.status).all()
    status_data = {status: count for status, count in status_counts}
    
    return {
        'Pending': status_data.get('Pending', 0),
        'Assigned': status_data.get('Assigned', 0),
        'In Progress': status_data.get('In Progress', 0),
        'Resolved': status_data.get('Resolved', 0)
    }

@officer.route('/analytics/category')
def get_category_analytics():
    if 'user_id' not in session or session.get('role') != 'officer':
        return {'error': 'Unauthorized'}, 401
    
    # Get complaint counts by category
    category_counts = db.session.query(Complaint.category, func.count(Complaint.id)).group_by(Complaint.category).all()
    category_data = {category: count for category, count in category_counts}
    
    return category_data

@officer.route('/analytics/summary')
def get_analytics_summary():
    if 'user_id' not in session or session.get('role') != 'officer':
        return {'error': 'Unauthorized'}, 401
    
    total = Complaint.query.count()
    pending = Complaint.query.filter_by(status='Pending').count()
    assigned = Complaint.query.filter_by(status='Assigned').count()
    in_progress = Complaint.query.filter_by(status='In Progress').count()
    resolved = Complaint.query.filter_by(status='Resolved').count()
    
    return {
        'total': total,
        'pending': pending,
        'assigned': assigned,
        'in_progress': in_progress,
        'resolved': resolved
    }
