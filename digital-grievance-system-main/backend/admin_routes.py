from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from models import db, User, Complaint
from functools import wraps

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

        admin = User.query.filter_by(email=email, role='admin').first()

        if admin and admin.password == password:  # In production, use proper password hashing
            session['user_id'] = admin.id
            session['role'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
            flash('Invalid admin credentials', 'danger')

    return render_template('admin_login.html')

@admin.route('/dashboard')
@admin_login_required
def dashboard():
    # Get statistics
    total_complaints = Complaint.query.count()
    pending_complaints = Complaint.query.filter_by(status='Pending').count()
    resolved_complaints = Complaint.query.filter_by(status='Resolved').count()
    escalated_complaints = Complaint.query.filter(Complaint.escalation_level > 0).count()

    # Get all complaints with officer assignments
    complaints = Complaint.query.order_by(Complaint.escalation_level.desc(), Complaint.created_at.desc()).all()
    officers = User.query.filter_by(role='officer').all()

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
                         officer_assignments=officer_assignments)

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