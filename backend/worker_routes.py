from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from models import db, Complaint, Assignment, User
import os
from datetime import datetime

worker = Blueprint('worker', __name__, url_prefix='/worker')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@worker.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'worker':
        flash('Please login as a worker first', 'warning')
        return redirect(url_for('auth.home'))
    
    assignments = Assignment.query.filter_by(worker_id=session['user_id']).all()
    complaint_assignments = []
    
    for assignment in assignments:
        complaint = Complaint.query.get(assignment.complaint_id)
        if complaint:
            complaint_assignments.append({
                'complaint': complaint,
                'assignment': assignment
            })
    
    return render_template('worker_dashboard.html', complaint_assignments=complaint_assignments)

@worker.route('/update/<int:complaint_id>', methods=['POST'])
def update(complaint_id):
    if 'user_id' not in session or session.get('role') != 'worker':
        flash('Please login as a worker first', 'warning')
        return redirect(url_for('auth.home'))
    
    status = request.form.get('status')
    image = request.files.get('image')
    
    complaint = Complaint.query.get(complaint_id)
    
    if not complaint:
        flash('Complaint not found', 'danger')
        return redirect(url_for('worker.dashboard'))
    
    # Check if this complaint is assigned to this worker
    assignment = Assignment.query.filter_by(
        complaint_id=complaint_id,
        worker_id=session['user_id']
    ).first()
    
    if not assignment:
        flash('You are not assigned to this complaint', 'danger')
        return redirect(url_for('worker.dashboard'))
    
    if image and allowed_file(image.filename):
        filename = secure_filename(f"{datetime.now().timestamp()}_{image.filename}")
        upload_path = current_app.config['UPLOAD_FOLDER']
        os.makedirs(upload_path, exist_ok=True)
        image.save(os.path.join(upload_path, filename))
    
    complaint.status = status
    db.session.commit()
    
    flash('Complaint updated successfully!', 'success')
    return redirect(url_for('worker.dashboard'))
