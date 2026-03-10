from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from models import db, Citizen, Officer, ValidOfficer, User
import os
from functools import wraps

auth_routes = Blueprint('auth', __name__)

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'doc', 'docx'}
UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'uploads')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def citizen_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'citizen_id' not in session:
            flash('Please login as a citizen first', 'warning')
            return redirect(url_for('auth.citizen_login'))
        return f(*args, **kwargs)
    return decorated_function

def officer_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'officer_id' not in session:
            flash('Please login as an officer first', 'warning')
            return redirect(url_for('auth.officer_login'))
        return f(*args, **kwargs)
    return decorated_function

# ==================== CITIZEN AUTHENTICATION ====================

@auth_routes.route('/citizen_register', methods=['GET', 'POST'])
def citizen_register():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        
        # Validation
        if not all([name, email, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.citizen_register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.citizen_register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('auth.citizen_register'))
        
        # Check if email already exists in either table
        if Citizen.query.filter_by(email=email).first() or User.query.filter_by(email=email).first():
            flash('Email already registered. Please login or use a different email.', 'danger')
            return redirect(url_for('auth.citizen_register'))

        # Create new citizen record
        hashed_password = generate_password_hash(password)
        new_citizen = Citizen(
            name=name,
            email=email,
            password=hashed_password
        )

        # also add to generic User table so complaints can reference user_id
        new_user = User(
            name=name,
            email=email,
            password=hashed_password,
            role='citizen'
        )

        try:
            db.session.add(new_citizen)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.citizen_login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.citizen_register'))
    
    return render_template('citizen_register.html')

@auth_routes.route('/citizen_login', methods=['GET', 'POST'])
def citizen_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return redirect(url_for('auth.citizen_login'))
        
        citizen = Citizen.query.filter_by(email=email).first()
        
        if not citizen:
            flash('Invalid email address', 'danger')
            return redirect(url_for('auth.citizen_login'))
        
        if not check_password_hash(citizen.password, password):
            flash('Incorrect password', 'danger')
            return redirect(url_for('auth.citizen_login'))
        
        # Ensure there is a corresponding User record (for complaints, assignments, etc.)
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=citizen.name,
                        email=email,
                        password=citizen.password,
                        role='citizen')
            db.session.add(user)
            db.session.commit()

        # Set session variables (we keep citizen_* for compatibility)
        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = citizen.name
        session['citizen_id'] = citizen.id
        session['citizen_name'] = citizen.name
        session['citizen_email'] = citizen.email

        flash(f'Login successful! Welcome {citizen.name}', 'success')
        return redirect(url_for('citizen.dashboard'))
    
    return render_template('citizen_login.html')

@auth_routes.route('/citizen_dashboard')
@citizen_login_required
def citizen_dashboard():
    # legacy route - redirect to the new blueprint endpoint
    return redirect(url_for('citizen.dashboard'))

# ==================== OFFICER AUTHENTICATION ====================

@auth_routes.route('/officer_register', methods=['GET', 'POST'])
def officer_register():
    if request.method == 'POST':
        officer_id = request.form.get('officer_id')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        proof_file = request.files.get('proof_file')
        
        # Validation
        if not all([officer_id, password, confirm_password, proof_file]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.officer_register'))
        
        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.officer_register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('auth.officer_register'))
        
        # Check if officer_id is valid
        valid_officer = ValidOfficer.query.filter_by(officer_id=officer_id).first()
        if not valid_officer:
            flash('Invalid officer ID. Please contact administration.', 'danger')
            return redirect(url_for('auth.officer_register'))
        
        # Check if officer already registered
        existing_officer = Officer.query.filter_by(officer_id=officer_id).first()
        if existing_officer:
            flash('Officer ID already registered. Please login.', 'danger')
            return redirect(url_for('auth.officer_login'))
        
        # Handle file upload
        if proof_file and allowed_file(proof_file.filename):
            os.makedirs(UPLOAD_FOLDER, exist_ok=True)
            filename = secure_filename(f"{officer_id}_{proof_file.filename}")
            filepath = os.path.join(UPLOAD_FOLDER, filename)
            proof_file.save(filepath)
        else:
            flash('Invalid file format. Allowed: PDF, JPG, JPEG, PNG, DOC, DOCX', 'danger')
            return redirect(url_for('auth.officer_register'))
        
        # Create new officer
        hashed_password = generate_password_hash(password)
        new_officer = Officer(
            officer_id=officer_id,
            password=hashed_password,
            proof_file=f"uploads/{filename}",
            approval_status='pending'
        )
        
        try:
            db.session.add(new_officer)
            db.session.commit()
            flash('Registration successful! Your account will be reviewed by administrators.', 'success')
            return redirect(url_for('auth.officer_login'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.officer_register'))
    
    return render_template('officer_register.html')

@auth_routes.route('/officer_login', methods=['GET', 'POST'])
def officer_login():
    if request.method == 'POST':
        officer_id = request.form.get('officer_id')
        password = request.form.get('password')

        if not officer_id or not password:
            flash('Officer ID and password are required', 'danger')
            return redirect(url_for('auth.officer_login'))

        officer = Officer.query.filter_by(officer_id=officer_id).first()

        if not officer:
            flash('Invalid officer ID', 'danger')
            return redirect(url_for('auth.officer_login'))

        if not check_password_hash(officer.password, password):
            flash('Incorrect password', 'danger')
            return redirect(url_for('auth.officer_login'))

        if officer.approval_status != 'approved':
            flash(f'Your account status is: {officer.approval_status}. Please contact administration.', 'warning')
            return redirect(url_for('auth.officer_login'))

        # Ensure a User entry exists for this officer
        email = f"{officer_id}@officer.local"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(name=officer_id,
                        email=email,
                        password=officer.password,
                        role='officer')
            db.session.add(user)
            db.session.commit()

        # Set session variables
        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = officer_id
        session['officer_id'] = officer.officer_id

        flash(f'Login successful! Welcome Officer {officer.officer_id}', 'success')
        return redirect(url_for('officer.dashboard'))

    return render_template('officer_login.html')

# ==================== NEW OFFICER REGISTRATION ====================
# This registration stores officer details in Officer table

@auth_routes.route('/officer_register_new', methods=['GET', 'POST'])
def officer_register_new():
    if request.method == 'POST':
        officer_id = request.form.get('officer_id')
        name = request.form.get('name')
        department = request.form.get('department')
        email = request.form.get('email')
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # Validation
        if not all([officer_id, name, department, email, phone, password, confirm_password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.officer_register_new'))

        if password != confirm_password:
            flash('Passwords do not match', 'danger')
            return redirect(url_for('auth.officer_register_new'))

        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('auth.officer_register_new'))

        # Check if officer_id already exists
        existing_officer = Officer.query.filter_by(officer_id=officer_id).first()
        if existing_officer:
            flash('Officer ID already registered. Please use a different ID or login.', 'danger')
            return redirect(url_for('auth.officer_register_new'))

        # Check if email already exists
        existing_email = Officer.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please login or use a different email.', 'danger')
            return redirect(url_for('auth.officer_register_new'))

        try:
            # Create new officer record
            hashed_password = generate_password_hash(password)
            new_officer = Officer(
                officer_id=officer_id,
                name=name,
                department=department,
                email=email,
                phone=phone,
                password=hashed_password
            )

            db.session.add(new_officer)
            db.session.commit()

            flash('Registration successful! Please login with your officer ID and password.', 'success')
            return redirect(url_for('auth.officer_login_new'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.officer_register_new'))

    return render_template('officer_register_new.html')

@auth_routes.route('/officer_login_new', methods=['GET', 'POST'])
def officer_login_new():
    if request.method == 'POST':
        officer_id = request.form.get('officer_id')
        password = request.form.get('password')

        if not officer_id or not password:
            flash('Officer ID and password are required', 'danger')
            return redirect(url_for('auth.officer_login_new'))

        officer = Officer.query.filter_by(officer_id=officer_id).first()

        if not officer:
            flash('Invalid officer ID', 'danger')
            return redirect(url_for('auth.officer_login_new'))

        if not check_password_hash(officer.password, password):
            flash('Incorrect password', 'danger')
            return redirect(url_for('auth.officer_login_new'))

        # Ensure a User entry exists for this officer (for compatibility with complaint system)
        email = f"{officer_id}@officer.local"
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name=officer.name,
                email=email,
                password=officer.password,
                phone=officer.phone,
                department=officer.department,
                role='officer'
            )
            db.session.add(user)
            db.session.commit()

        # Set session variables
        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = officer.name
        session['officer_id'] = officer.officer_id
        session['department'] = officer.department

        flash(f'Login successful! Welcome Officer {officer.name}', 'success')
        return redirect(url_for('officer.dashboard'))

    return render_template('officer_login_new.html')

@auth_routes.route('/officer_dashboard')
@officer_login_required
def officer_dashboard():
    # legacy endpoint
    return redirect(url_for('officer.dashboard'))

# ==================== COMMON ROUTES ====================

@auth_routes.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.home'))

@auth_routes.route('/')
@auth_routes.route('/home')
def home():
    return render_template('home.html')

# ==================== BACKWARD COMPATIBILITY ROUTES ====================
# These routes redirect old links to the new authentication system

@auth_routes.route('/login')
def old_login_redirect():
    """Redirect old /login to home page with role selection"""
    flash('Please select your role to login', 'info')
    return redirect(url_for('auth.home'))

@auth_routes.route('/register')
def old_register_redirect():
    """Redirect old /register to home page with role selection"""
    flash('Please select your role to register', 'info')
    return redirect(url_for('auth.home'))
