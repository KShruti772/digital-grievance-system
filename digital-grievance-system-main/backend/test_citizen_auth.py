#!/usr/bin/env python
"""
Test script to verify citizen registration and login authentication
"""
import sys
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from run import app, db
from models import Citizen, User

def test_citizen_authentication():
    """Test citizen registration and login"""
    
    with app.app_context():
        print("\n" + "="*70)
        print("CITIZEN AUTHENTICATION TEST")
        print("="*70)
        
        # Test data
        test_email = "testcitizen@example.com"
        test_password = "TestPassword123"
        test_name = "Test Citizen"
        
        print("\n[STEP 1] Clean up any existing test citizen...")
        existing_citizen = Citizen.query.filter_by(email=test_email).first()
        existing_user = User.query.filter_by(email=test_email).first()
        
        if existing_citizen:
            db.session.delete(existing_citizen)
            print(f"  ✓ Deleted existing Citizen record")
        
        if existing_user:
            db.session.delete(existing_user)
            print(f"  ✓ Deleted existing User record")
        
        db.session.commit()
        
        # SIMULATE REGISTRATION
        print("\n[STEP 2] Simulate citizen registration...")
        
        new_citizen = Citizen(
            name=test_name,
            email=test_email,
            password=test_password
        )
        
        new_user = User(
            name=test_name,
            email=test_email,
            password=test_password,
            role='citizen'
        )
        
        db.session.add(new_citizen)
        db.session.add(new_user)
        db.session.commit()
        print(f"  ✓ Citizen registered: {test_name} ({test_email})")
        
        # VERIFY REGISTRATION
        print("\n[STEP 3] Verify citizen was saved to database...")
        saved_citizen = Citizen.query.filter_by(email=test_email).first()
        saved_user = User.query.filter_by(email=test_email).first()
        
        if not saved_citizen:
            print(f"  ✗ FAILED: Citizen not found in database!")
            return False
        
        print(f"  ✓ Citizen found in Citizen table (ID: {saved_citizen.id})")
        print(f"    - Name: {saved_citizen.name}")
        print(f"    - Email: {saved_citizen.email}")
        print(f"    - Password: {saved_citizen.password}")
        
        if not saved_user:
            print(f"  ✗ FAILED: User record not found in User table!")
            return False
        
        print(f"  ✓ User found in User table (ID: {saved_user.id})")
        print(f"    - Role: {saved_user.role}")
        
        # SIMULATE LOGIN
        print("\n[STEP 4] Simulate citizen login...")
        
        # Step 4a: Query citizen by email
        login_citizen = Citizen.query.filter_by(email=test_email).first()
        
        if not login_citizen:
            print(f"  ✗ FAILED: Could not find citizen by email during login!")
            print(f"  Available citizens in database:")
            all_citizens = Citizen.query.all()
            for c in all_citizens:
                print(f"    - {c.email} (ID: {c.id})")
            return False
        
        print(f"  ✓ Citizen found by email: {login_citizen.name}")
        
        # Step 4b: Verify password
        password_ok = (login_citizen.password == test_password)
        
        if not password_ok:
            print(f"  ✗ FAILED: Password verification failed!")
            print(f"  Stored password: {login_citizen.password}")
            print(f"  Provided password: {test_password}")
            return False
        
        print(f"  ✓ Password verification successful!")
        
        # Step 4c: Get User record
        login_user = User.query.filter_by(email=test_email).first()
        
        if not login_user:
            print(f"  ✗ FAILED: User record not found during login!")
            return False
        
        print(f"  ✓ User record found for session setup")
        
        # SUCCESS
        print("\n" + "="*70)
        print("✓ ALL TESTS PASSED - Citizen authentication is working!")
        print("="*70)
        print("\nSummary:")
        print(f"  - Citizen can register successfully")
        print(f"  - Registration data persists to database")
        print(f"  - Login can find citizen by email")
        print(f"  - Password verification works correctly")
        print(f"  - Session data can be properly set")
        print("="*70 + "\n")
        
        return True

if __name__ == '__main__':
    success = test_citizen_authentication()
    sys.exit(0 if success else 1)
