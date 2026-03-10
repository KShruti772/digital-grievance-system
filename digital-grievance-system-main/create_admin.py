import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models import db, User
from run import app
from werkzeug.security import generate_password_hash

with app.app_context():
    # Create admin user
    admin_email = 'admin@test.com'
    admin_password = 'admin123'

    # Check if admin already exists
    existing_admin = User.query.filter_by(email=admin_email).first()
    if existing_admin:
        print(f"Admin user {admin_email} already exists!")
    else:
        # Hash password
        hashed_password = generate_password_hash(admin_password)

        # Create admin user
        admin_user = User(
            name='System Admin',
            email=admin_email,
            password=hashed_password,
            role='admin',
            phone='1234567890'
        )

        db.session.add(admin_user)
        db.session.commit()
        print(f"Admin user created successfully!")
        print(f"Email: {admin_email}")
        print(f"Password: {admin_password}")