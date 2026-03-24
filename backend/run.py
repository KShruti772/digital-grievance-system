from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
from models import db, ValidOfficer, User, Worker, Officer, create_default_workers, Admin, Citizen, Feedback

app = Flask(__name__, 
            template_folder='../app/templates', 
            static_folder='../app/static')

app.config['SECRET_KEY'] = 'your_super_secret_key_change_in_production_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///grievance.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db.init_app(app)

with app.app_context():
    db.create_all()

from routes import app as main_app
from auth_routes import auth_routes
from citizen_routes import citizen
from officer_routes import officer
from worker_routes import worker
from admin_routes import admin
from werkzeug.security import generate_password_hash
app.register_blueprint(auth_routes)
app.register_blueprint(citizen)
app.register_blueprint(officer)
app.register_blueprint(worker)
app.register_blueprint(admin)

def init_seed_data():
    """Initialize seed data for valid officers"""
    # Check if valid officers already exist
    if ValidOfficer.query.count() == 0:
        seed_officers = [
            ValidOfficer(officer_id='OFF001', department='Roads & Infrastructure'),
            ValidOfficer(officer_id='OFF002', department='Water Supply'),
            ValidOfficer(officer_id='OFF003', department='Sanitation'),
            ValidOfficer(officer_id='OFF004', department='Electricity'),
            ValidOfficer(officer_id='OFF005', department='General Administration'),
        ]
        for officer in seed_officers:
            db.session.add(officer)
        db.session.commit()
        print("[OK] Valid officers seeded successfully!")
    else:
        print("[OK] Valid officers already exist!")

def create_default_officers():
    """Create default officers if none exist"""
    if Officer.query.count() == 0:
        officers = [
            Officer(
                officer_id="OFF001",
                name="Rajesh Sharma",
                email="sanitation@city.gov",
                department="Sanitation",
                phone="9876543210",
                password="12345"
            ),
            Officer(
                officer_id="OFF002",
                name="Priya Verma",
                email="electricity@city.gov",
                department="Electricity",
                phone="9876543211",
                password="12345"
            ),
            Officer(
                officer_id="OFF003",
                name="Amit Kulkarni",
                email="roads@city.gov",
                department="Roads",
                phone="9876543212",
                password="12345"
            ),
            Officer(
                officer_id="OFF004",
                name="Neha Patil",
                email="water@city.gov",
                department="Water Supply",
                phone="9876543213",
                password="12345"
            ),
            Officer(
                officer_id="OFF005",
                name="Suresh Reddy",
                email="publicworks@city.gov",
                department="Public Works",
                phone="9876543214",
                password="12345"
            )
        ]
        db.session.add_all(officers)
        db.session.commit()
        print("[OK] Default officers created successfully!")
    else:
        print("[OK] Default officers already exist!")

if __name__ == '__main__':
    with app.app_context():
        # Drop and recreate all tables to ensure schema is correct
        db.drop_all()
        db.create_all()
        print("[OK] Database tables recreated!")
        
        # DEBUG: Print current database state
        print("\n" + "="*60)
        print("[DATABASE DEBUG] Current database state:")
        print(f"  - Citizens registered (Citizen table): {Citizen.query.count()}")
        print(f"  - Citizens registered (User table, role=citizen): {db.session.query(User).filter_by(role='citizen').count()}")
        print(f"  - Officers registered (User table, role=officer): {db.session.query(User).filter_by(role='officer').count()}")
        print(f"  - Admin users (User table, role=admin): {db.session.query(User).filter_by(role='admin').count()}")
        print(f"  - Valid officers (pre-approved IDs): {ValidOfficer.query.count()}")
        print(f"  - Workers: {Worker.query.count()}")
        print(f"  - Default officers: {Officer.query.count()}")
        # print database file location for debugging
        print(f"  - Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI')}")
        import os
        print(f"  - Database file path (cwd): {os.getcwd()}")
        # debug: list citizen objects
        citizens = Citizen.query.all()
        print(f"  - Registered Citizen objects: {citizens}")
        print("="*60 + "\n")
        init_seed_data()
        create_default_workers()
        create_default_officers()
        print("[OK] Default workers seeded successfully!")
        # ensure default admin exists
        def create_default_admin():
            admin = User.query.filter_by(email="shrutikondabathula@gmail.com").first()
            if not admin:
                admin_user = User(
                    name="Shruti Mahesh Kondabathula",
                    email="shrutikondabathula@gmail.com",
                    password=generate_password_hash("Shruti@12345#$"),
                    role="admin"
                )
                db.session.add(admin_user)
                db.session.commit()
                print("Default admin created successfully")
        create_default_admin()
        # debug existing admin users
        print("==== ADMIN USERS IN DATABASE ====")
        for a in Admin.query.all():
            print(f"Admin table: id={a.id}, username={a.username}, email={a.email}")
        for u in User.query.filter_by(role='admin').all():
            print(f"User table admin: id={u.id}, name={u.name}, email={u.email}")

        # Create default admin in Admin table only if none exist
        if Admin.query.count() == 0:
            admin = Admin(
                username="admin",
                email="admin@gmail.com",
                password="admin123"
            )
            db.session.add(admin)
            db.session.commit()
            print("Default admin in Admin table created successfully")
        print("\n" + "="*60)
        print("Digital Grievance Redressal System Started!")
        print("="*60)
        print("\nAccess the application at: http://127.0.0.1:5000")
        print("\nAuthentication URLs:")
        print("  - Citizen Registration: http://127.0.0.1:5000/citizen_register")
        print("  - Citizen Login: http://127.0.0.1:5000/citizen_login")
        print("  - Officer Registration: http://127.0.0.1:5000/officer_register")
        print("  - Officer Login: http://127.0.0.1:5000/officer_login")
        print("\nValid Officer IDs for testing:")
        for officer in ValidOfficer.query.all():
            print(f"  - {officer.officer_id} ({officer.department})")
        print("\nDefault Officer Login Credentials:")
        for officer in Officer.query.all():
            print(f"  - Email: {officer.email}, Password: {officer.password} ({officer.name} - {officer.department})")
        print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
