from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.utils import secure_filename
from models import db, Complaint, Worker
from priority_classifier import classify_priority
import os
from datetime import datetime, timedelta
import random

citizen = Blueprint('citizen', __name__, url_prefix='/citizen')

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@citizen.route('/dashboard')
def dashboard():
    if 'user_id' not in session or session.get('role') != 'citizen':
        flash('Please login as a citizen first', 'warning')
        return redirect(url_for('auth.citizen_login'))
    
    user_id = session['user_id']
    complaints = Complaint.query.filter_by(user_id=user_id).all()
    return render_template('citizen_dashboard.html', complaints=complaints)

@citizen.route('/submit', methods=['GET', 'POST'])
def submit_complaint():
    if 'user_id' not in session or session.get('role') != 'citizen':
        flash('Please login as a citizen first', 'warning')
        return redirect(url_for('auth.citizen_login'))

    if request.method == 'POST':
        title = request.form['title']
        description = request.form['description']
        category = request.form['category']
        location_link = request.form.get('location_link')
        
        # Validate that location link is provided
        if not location_link:
            flash('Please provide a Google Maps location link.', 'danger')
            return redirect(url_for('citizen.submit_complaint'))
        
        image = request.files.get('image')
        
        # Extract location string from Google Maps link for location field
        # For simplicity, use the category + timestamp as location identifier
        location = f"{category} - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
        
        image_path = None
        if image and allowed_file(image.filename):
            filename = secure_filename(f"{datetime.now().timestamp()}_{image.filename}")
            upload_path = current_app.config['UPLOAD_FOLDER']
            os.makedirs(upload_path, exist_ok=True)
            image.save(os.path.join(upload_path, filename))
            image_path = f'uploads/{filename}'
        
        # Classify priority based on category and description
        priority = classify_priority(category, description)
        # generate random estimated resolution days
        resolution_days = random.randint(1, 5)
        
        # Set deadline
        deadline = datetime.utcnow() + timedelta(days=3)
        
        # Map category to department
        if category == "Garbage":
            department = "Sanitation"
        elif category == "Electricity":
            department = "Electrical"
        elif category == "Road Damage":
            department = "Road"
        else:
            department = "General"
        
        # Assign worker
        worker = Worker.query.filter_by(department=department).first()
        worker_name = worker.name if worker else "Not Assigned"
        worker_contact = worker.contact_number if worker else ""
        
        complaint = Complaint(
            user_id=session['user_id'],
            title=title,
            description=description,
            category=category,
            location=location,
            location_link=location_link,
            image_path=image_path,
            priority=priority,
            estimated_resolution_days=resolution_days,
            deadline=deadline,
            worker_name=worker_name,
            worker_contact=worker_contact
        )
        db.session.add(complaint)
        db.session.commit()
        
        flash('Complaint submitted successfully!', 'success')
        return redirect(url_for('citizen.dashboard'))
    
    return render_template('complaint_form.html')
