from flask import Flask
import os
from models import db, ValidOfficer, User
from werkzeug.security import generate_password_hash
from routes import app as main_app
from auth_routes import auth_routes
from citizen_routes import citizen
from officer_routes import officer
from worker_routes import worker
from admin_routes import admin

app = Flask(__name__, 
            template_folder='../app/templates', 
            static_folder='../app/static')

app.config['SECRET_KEY'] = 'your_super_secret_key_change_in_production_2026'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(__file__), '..', 'app', 'static', 'uploads')
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

db.init_app(app)

app.register_blueprint(main_app)
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

def create_default_admin():
    """Create a default admin user if none exists"""
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
        print("[OK] Default admin created successfully")
    else:
        print("[OK] Default admin already exists")

if __name__ == '__main__':
    with app.app_context():
        # Drop all tables and recreate (for development - handles schema changes)
        db.drop_all()
        db.create_all()
        print("[OK] Database tables recreated!")
        init_seed_data()
        create_default_admin()
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
        print("="*60 + "\n")
    
    app.run(debug=True, port=5000)
