from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from werkzeug.utils import secure_filename
from models import db, Citizen, Officer, ValidOfficer, User, Feedback
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
        email = request.form.get('email').strip().lower()
        phone = request.form.get('phone', '')
        password = request.form.get('password')
        
        # Validation
        if not all([name, email, password]):
            flash('All fields are required', 'danger')
            return redirect(url_for('auth.citizen_register'))
        
        if len(password) < 6:
            flash('Password must be at least 6 characters', 'danger')
            return redirect(url_for('auth.citizen_register'))
        
        # Check if email already exists
        existing_citizen = Citizen.query.filter_by(email=email).first()
        if existing_citizen:
            flash('Account already exists. Please login.', 'danger')
            return redirect(url_for('auth.citizen_login'))

        try:
            # Create new citizen record and a corresponding User entry for compatibility
            new_citizen = Citizen(
                name=name,
                email=email,
                phone=phone,
                password=password
            )
            # prepare user record (legacy complaints system relies on User table)
            new_user = User(
                name=name,
                email=email,
                password=password,
                phone=phone,
                role='citizen'
            )

            db.session.add(new_citizen)
            db.session.add(new_user)
            db.session.commit()
            
            print(f"[✓] Citizen registered and user created: {email}")
            flash('Registration successful! Please login.', 'success')
            return redirect(url_for('auth.citizen_login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"[✗] Registration error: {str(e)}")
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.citizen_register'))
    
    return render_template('citizen_register.html')

@auth_routes.route('/citizen_login', methods=['GET', 'POST'])
def citizen_login():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')
        
        if not email or not password:
            flash('Email and password are required', 'danger')
            return redirect(url_for('auth.citizen_login'))
        
        # Look up citizen in Citizen table
        citizen = Citizen.query.filter_by(email=email).first()
        
        if not citizen:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.citizen_login'))
        
        # Check password
        if citizen.password != password:
            flash('Invalid email or password', 'danger')
            return redirect(url_for('auth.citizen_login'))
        
        # For complaint system compatibility, ensure User record exists
        user = User.query.filter_by(email=email).first()
        if not user:
            user = User(
                name=citizen.name,
                email=email,
                password=password,
                phone=citizen.phone,
                role='citizen'
            )
            db.session.add(user)
            db.session.commit()
        
        # Set session variables
        session['citizen_id'] = citizen.id
        session['citizen_name'] = citizen.name
        session['citizen_email'] = citizen.email
        session['user_id'] = user.id
        session['role'] = 'citizen'
        
        print(f"[✓] Citizen login successful: {citizen.name} (ID: {citizen.id})")
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
        name = request.form.get('name')
        email = request.form.get('email')
        password = request.form.get('password')
        department = request.form.get('department')

        existing_officer = Officer.query.filter_by(email=email).first()

        if existing_officer:
            flash("Officer already registered. Please login.")
            return redirect(url_for('auth.officer_login'))

        officer = Officer(
            officer_id=officer_id,
            name=name,
            email=email,
            password=password,
            department=department,
            approval_status="approved"
        )

        db.session.add(officer)
        db.session.commit()

        print("Registered email:", email)

        flash("Registration successful. Please login.")
        return redirect(url_for('auth.officer_login'))

    return render_template('officer_register.html')

@auth_routes.route('/officer_login', methods=['GET', 'POST'])
def officer_login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        print("Login attempt:", email)

        officer = Officer.query.filter_by(email=email).first()

        print("Officer found:", officer)

        if officer is None:
            flash("Email not registered")
            return redirect(url_for('auth.officer_register'))

        if officer.password != password:
            flash("Incorrect password")
            return redirect(url_for('auth.officer_login'))

        session['user_id'] = officer.id
        session['role'] = 'officer'
        session['officer_id'] = officer.id

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
        email = request.form.get('email').strip().lower()
        phone = request.form.get('phone')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        id_proof_file = request.files.get('id_proof')

        # Validation
        if not all([officer_id, name, department, email, phone, password, confirm_password, id_proof_file]):
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
        existing_email_officer = Officer.query.filter_by(email=email).first()
        existing_email_user = User.query.filter_by(email=email).first()
        if existing_email_officer or existing_email_user:
            flash('You are already registered. Please login.', 'danger')
            return redirect(url_for('auth.officer_login_new'))

        # Validate and handle ID proof file upload
        id_proof_path = None
        if id_proof_file and id_proof_file.filename:
            if allowed_file(id_proof_file.filename):
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                filename = secure_filename(f"{officer_id}_{id_proof_file.filename}")
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                id_proof_file.save(file_path)
                id_proof_path = f"uploads/{filename}"
            else:
                flash('Invalid file format. Allowed: Images (JPG, PNG, PDF, DOC, DOCX)', 'danger')
                return redirect(url_for('auth.officer_register_new'))
        else:
            flash('ID proof file is required', 'danger')
            return redirect(url_for('auth.officer_register_new'))

        try:
            # Create new officer record
            new_officer = Officer(
                officer_id=officer_id,
                name=name,
                department=department,
                email=email,
                phone=phone,
                password=password,  # Store plain text password
                id_proof=id_proof_path,
                approval_status='approved'
            )

            db.session.add(new_officer)
            db.session.commit()

            flash('Officer Verified Successfully!', 'success')
            return redirect(url_for('auth.officer_login_new'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'danger')
            return redirect(url_for('auth.officer_register_new'))

    return render_template('officer_register_new.html')

@auth_routes.route('/officer_login_new', methods=['GET', 'POST'])
def officer_login_new():
    if request.method == 'POST':
        email = request.form.get('email').strip().lower()
        password = request.form.get('password')

        print(f"\n[OFFICER LOGIN NEW DEBUG] Attempt to login with normalized email: {email}")

        if not email or not password:
            print(f"[OFFICER LOGIN NEW DEBUG] Missing email or password")
            flash('Email and password are required', 'danger')
            return redirect(url_for('auth.officer_login_new'))

        officer = Officer.query.filter_by(email=email).first()

        if not officer:
            print(f"[OFFICER LOGIN NEW DEBUG] Officer with email {email} not found")
            print(f"[OFFICER LOGIN NEW DEBUG] Available officer emails: {[o.email for o in Officer.query.all()]}")
            flash('Invalid email address', 'danger')
            return redirect(url_for('auth.officer_login_new'))

        print(f"[OFFICER LOGIN NEW DEBUG] Officer found: {officer.name} (ID: {officer.officer_id})")
        
        if officer.password != password:  # Check plain text password
            print(f"[OFFICER LOGIN NEW DEBUG] Password verification FAILED")
            flash('Incorrect password', 'danger')
            return redirect(url_for('auth.officer_login_new'))

        print(f"[OFFICER LOGIN NEW DEBUG] Password verification SUCCESS")

        if officer.approval_status != 'approved':
            print(f"[OFFICER LOGIN NEW DEBUG] Officer status is: {officer.approval_status}")
            flash(f'Your account status is: {officer.approval_status}. Please contact administration.', 'warning')
            return redirect(url_for('auth.officer_login_new'))

        # Ensure a User entry exists for this officer (use actual email from Officer record)
        user = User.query.filter_by(email=officer.email).first()
        if not user:
            print(f"[OFFICER LOGIN NEW DEBUG] User record not found, creating new one with email: {officer.email}")
            user = User(
                name=officer.name,
                email=officer.email,
                password=officer.password,
                phone=officer.phone,
                department=officer.department,
                employee_id=officer.officer_id,
                role='officer'
            )
            db.session.add(user)
            db.session.commit()
            print(f"[OFFICER LOGIN NEW DEBUG] User record created with ID: {user.id}")
        else:
            print(f"[OFFICER LOGIN NEW DEBUG] User record found with ID: {user.id}")

        # Set session variables
        session['user_id'] = user.id
        session['role'] = user.role
        session['name'] = officer.name
        session['officer_id'] = officer.officer_id
        session['department'] = officer.department

        print(f"[OFFICER LOGIN NEW DEBUG] Session set successfully. Redirecting to dashboard...")
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
    name = session.get('citizen_name', session.get('name', 'User'))
    session.clear()
    flash('Logged out successfully', 'info')
    return redirect(url_for('auth.home'))

@auth_routes.route('/')
@auth_routes.route('/home')
def home():
    # redirect authenticated users to their respective dashboards
    role = session.get('role')
    if role == 'citizen':
        return redirect(url_for('citizen.dashboard'))
    elif role == 'officer':
        return redirect(url_for('officer.dashboard'))
    elif role == 'worker':
        return redirect(url_for('worker.dashboard'))
    elif role == 'admin':
        return redirect(url_for('admin.dashboard'))
    # public homepage
    return render_template('home.html')

@auth_routes.route('/feedback', methods=['GET', 'POST'])
def feedback():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        message = request.form.get('message')

        new_feedback = Feedback(
            name=name,
            email=email,
            message=message
        )
        db.session.add(new_feedback)
        db.session.commit()
        flash('Thank you for your feedback!', 'success')
        return redirect(url_for('auth.home'))

    return render_template('feedback.html')

@auth_routes.route('/admin_login')
def admin_login_redirect():
    return redirect(url_for('admin.admin_login'))

# ==================== BACKWARD COMPATIBILITY ROUTES ====================
# These routes redirect old links to the new authentication system

@auth_routes.route('/login', methods=['GET','POST'])
def login():

    if request.method == 'POST':

        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and check_password_hash(user.password, password):

            session['user_id'] = user.id
            session['role'] = user.role

            if user.role == "admin":
                return redirect('/admin_dashboard')

            elif user.role == "officer":
                return redirect('/officer_dashboard')

            else:
                return redirect('/citizen_dashboard')

        else:
            flash("Invalid email or password")

    return render_template('login.html')

@auth_routes.route('/admin_dashboard')
def admin_dashboard_redirect():
    # redirect to admin dashboard
    return redirect(url_for('admin.dashboard'))

@auth_routes.route('/register')
def old_register_redirect():
    """Redirect old /register to home page with role selection"""
    flash('Please select your role to register', 'info')
    return redirect(url_for('auth.home'))
