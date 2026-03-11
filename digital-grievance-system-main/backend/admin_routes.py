from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, Admin, User, Complaint, Officer
from functools import wraps
from werkzeug.security import check_password_hash
from datetime import datetime

admin = Blueprint('admin', __name__, url_prefix='/admin')

def admin_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('role') != 'admin':
            flash('Please login as an admin first', 'warning')
            return redirect(url_for('admin.admin_login'))
        return f(*args, **kwargs)
    return decorated_function

@admin.route('/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # debug existing admin attempt
        print(f"[ADMIN LOGIN DEBUG] attempt with {email}")

        # first try dedicated Admin table
        admin = Admin.query.filter_by(email=email).first()
        if admin:
            print(f"[ADMIN LOGIN DEBUG] found in Admin table id={admin.id}")
            if admin.password == password:
                session['user_id'] = admin.id
                session['role'] = 'admin'
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Incorrect password for admin account', 'danger')
                return render_template('admin_login.html')

        # next fallback to User table record with role=admin (legacy)
        user_admin = User.query.filter_by(email=email, role='admin').first()
        if user_admin:
            print(f"[ADMIN LOGIN DEBUG] found in User table id={user_admin.id}")
            # assuming password hashed for User table
            if check_password_hash(user_admin.password, password):
                session['user_id'] = user_admin.id
                session['role'] = 'admin'
                flash('Admin login successful!', 'success')
                return redirect(url_for('admin.dashboard'))
            else:
                flash('Incorrect password for admin account', 'danger')
                return render_template('admin_login.html')

        flash('Admin email not found', 'danger')

    return render_template('admin_login.html')

@admin.route('/dashboard')
@admin_login_required
def dashboard():
    # Get statistics
    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter_by(status='Pending').count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    escalated_complaints = Complaint.query.filter(Complaint.escalation_level > 0).count()

    # Analytics data
    complaints = Complaint.query.all()
    category_counts = {}
    location_counts = {}

    for c in complaints:
        category_counts[c.category] = category_counts.get(c.category, 0) + 1
        location_counts[c.location] = location_counts.get(c.location, 0) + 1

    resolution_rate = 0
    if total_complaints > 0:
        resolution_rate = (resolved_complaints / total_complaints) * 100

    # Check for expired deadlines and escalate
    all_complaints = Complaint.query.all()
    for c in all_complaints:
        if c.deadline and datetime.utcnow() > c.deadline and c.status != "Resolved":
            c.status = "Escalated"
    db.session.commit()

    # Get all complaints with officer assignments
    complaints = Complaint.query.order_by(Complaint.escalation_level.desc(), Complaint.created_at.desc()).all()
    
    # Get registered officers from dedicated Officer table
    registered_officers = Officer.query.all()
    
    # Use registered officers for display
    officers = registered_officers

    # Get officer assignments
    officer_assignments = {}
    for complaint in complaints:
        if complaint.assigned_officer:
            officer = User.query.get(complaint.assigned_officer)
            officer_assignments[complaint.id] = officer

    return render_template('admin_dashboard.html',
                         total_complaints=total_complaints,
                         pending_complaints=pending_complaints,
                         resolved_complaints=resolved_complaints,
                         escalated_complaints=escalated_complaints,
                         complaints=complaints,
                         officers=officers,
                         registered_officers=registered_officers,
                         officer_assignments=officer_assignments,
                         total=total_complaints,
                         resolved=resolved_complaints,
                         pending=pending_complaints,
                         category_counts=category_counts,
                         location_counts=location_counts,
                         resolution_rate=resolution_rate)

@admin.route('/assign_officer/<int:complaint_id>', methods=['POST'])
@admin_login_required
def assign_officer(complaint_id):
    officer_id = request.form.get('officer_id')

    complaint = Complaint.query.get_or_404(complaint_id)
    if officer_id:
        complaint.assigned_officer = int(officer_id)
        complaint.status = 'Assigned'
    else:
        complaint.assigned_officer = None

    db.session.commit()
    flash('Officer assigned successfully!', 'success')
    return redirect(url_for('admin.dashboard'))

@admin.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    flash('Admin logged out successfully!', 'info')
    return redirect(url_for('admin.admin_login'))