#!/usr/bin/env python
"""
Comprehensive test to verify all user registration stores data correctly
Tests: Citizen registration, Officer (legacy) registration, Officer (new) registration
"""
import sys
import os
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from run import app, db
from models import Citizen, Officer, User, ValidOfficer

def cleanup_test_data():
    """Remove any test data from previous runs"""
    with app.app_context():
        # Remove test citizen
        test_citizen = Citizen.query.filter_by(email='test.citizen@example.com').first()
        if test_citizen:
            db.session.delete(test_citizen)
        
        # Remove test officer (new)
        test_officer_new = Officer.query.filter_by(officer_id='TEST001').first()
        if test_officer_new:
            db.session.delete(test_officer_new)
        
        # Remove test user records
        for email in ['test.citizen@example.com', 'test.officer@example.com']:
            test_user = User.query.filter_by(email=email).first()
            if test_user:
                db.session.delete(test_user)
        
        db.session.commit()

def test_citizen_registration():
    """Test citizen registration stores data correctly"""
    print("\n" + "="*70)
    print("TEST 1: CITIZEN REGISTRATION DATA STORAGE")
    print("="*70)
    
    with app.app_context():
        # Test data
        test_email = 'test.citizen@example.com'
        test_password = 'CitizenPass123'
        test_name = 'Test Citizen User'
        
        print("\n[STEP 1] Simulate citizen registration...")
        hashed_password = generate_password_hash(test_password)
        
        new_citizen = Citizen(
            name=test_name,
            email=test_email,
            password=hashed_password
        )
        
        new_user = User(
            name=test_name,
            email=test_email,
            password=hashed_password,
            role='citizen'
        )
        
        try:
            db.session.add(new_citizen)
            db.session.add(new_user)
            db.session.commit()
            print(f"  ✓ Registration successful")
        except Exception as e:
            print(f"  ✗ Registration FAILED: {e}")
            db.session.rollback()
            return False
        
        # Verify data was saved
        print("\n[STEP 2] Verify citizen data in database...")
        saved_citizen = Citizen.query.filter_by(email=test_email).first()
        saved_user = User.query.filter_by(email=test_email, role='citizen').first()
        
        if not saved_citizen:
            print(f"  ✗ Citizen NOT found in database")
            return False
        
        print(f"  ✓ Citizen table: {saved_citizen.name} ({saved_citizen.email})")
        print(f"    - ID: {saved_citizen.id}")
        print(f"    - Created: {saved_citizen.created_at}")
        
        if not saved_user:
            print(f"  ✗ User NOT found in database")
            return False
        
        print(f"  ✓ User table: {saved_user.name} ({saved_user.email})")
        print(f"    - ID: {saved_user.id}")
        print(f"    - Role: {saved_user.role}")
        
        # Verify password works for login
        print("\n[STEP 3] Verify password for login...")
        password_ok = check_password_hash(saved_citizen.password, test_password)
        
        if not password_ok:
            print(f"  ✗ Password verification FAILED")
            return False
        
        print(f"  ✓ Password verification successful")
        
        print("\n✓ CITIZEN REGISTRATION TEST PASSED")
        return True

def test_officer_registration_new():
    """Test new officer registration stores all required data"""
    print("\n" + "="*70)
    print("TEST 2: OFFICER REGISTRATION (NEW) DATA STORAGE")
    print("="*70)
    
    with app.app_context():
        # Test data
        officer_id = 'TEST001'
        test_name = 'Test Officer New'
        test_department = 'Roads & Infrastructure'
        test_email = 'test.officer.new@example.com'
        test_phone = '9876543210'
        test_password = 'OfficerNewPass123'
        
        print("\n[STEP 1] Simulate officer registration (new)...")
        hashed_password = generate_password_hash(test_password)
        
        new_officer = Officer(
            officer_id=officer_id,
            name=test_name,
            department=test_department,
            email=test_email,
            phone=test_phone,
            password=hashed_password,
            id_proof='uploads/test_proof.pdf',
            approval_status='approved'
        )
        
        try:
            db.session.add(new_officer)
            db.session.commit()
            print(f"  ✓ Registration successful")
        except Exception as e:
            print(f"  ✗ Registration FAILED: {e}")
            db.session.rollback()
            return False
        
        # Verify all data was saved
        print("\n[STEP 2] Verify officer data in database...")
        saved_officer = Officer.query.filter_by(officer_id=officer_id).first()
        
        if not saved_officer:
            print(f"  ✗ Officer NOT found in database")
            return False
        
        print(f"  ✓ Officer record found:")
        print(f"    - Officer ID: {saved_officer.officer_id}")
        print(f"    - Name: {saved_officer.name}")
        print(f"    - Email: {saved_officer.email}")
        print(f"    - Department: {saved_officer.department}")
        print(f"    - Phone: {saved_officer.phone}")
        print(f"    - Approval Status: {saved_officer.approval_status}")
        print(f"    - ID Proof: {saved_officer.id_proof}")
        print(f"    - Created: {saved_officer.created_at}")
        
        # Verify all required fields are stored
        required_fields = {
            'officer_id': officer_id,
            'name': test_name,
            'department': test_department,
            'email': test_email,
            'phone': test_phone,
            'approval_status': 'approved'
        }
        
        print("\n[STEP 3] Verify all required fields...")
        all_fields_ok = True
        for field, expected_value in required_fields.items():
            actual_value = getattr(saved_officer, field)
            if actual_value == expected_value:
                print(f"  ✓ {field}: {actual_value}")
            else:
                print(f"  ✗ {field}: Expected '{expected_value}', got '{actual_value}'")
                all_fields_ok = False
        
        if not all_fields_ok:
            return False
        
        # Verify password works for login
        print("\n[STEP 4] Verify password for login...")
        password_ok = check_password_hash(saved_officer.password, test_password)
        
        if not password_ok:
            print(f"  ✗ Password verification FAILED")
            return False
        
        print(f"  ✓ Password verification successful")
        
        print("\n✓ OFFICER REGISTRATION (NEW) TEST PASSED")
        return True

def test_database_integrity():
    """Verify database constraints and data integrity"""
    print("\n" + "="*70)
    print("TEST 3: DATABASE INTEGRITY")
    print("="*70)
    
    with app.app_context():
        print("\n[STEP 1] Verify unique email constraint...")
        
        # Try to register duplicate citizen
        test_email = 'duplicate.test@example.com'
        test_password = 'DuplicatePass123'
        
        citizen1 = Citizen(
            name='Citizen One',
            email=test_email,
            password=generate_password_hash(test_password)
        )
        
        db.session.add(citizen1)
        db.session.commit()
        print(f"  ✓ First citizen registered with email: {test_email}")
        
        # Try to add duplicate
        citizen2 = Citizen(
            name='Citizen Two',
            email=test_email,
            password=generate_password_hash(test_password)
        )
        
        try:
            db.session.add(citizen2)
            db.session.commit()
            print(f"  ✗ Duplicate email constraint NOT working (database should reject this)")
            db.session.rollback()
            # Delete the first one for cleanup
            Citizen.query.filter_by(email=test_email).delete()
            db.session.commit()
            return False
        except Exception as e:
            db.session.rollback()
            print(f"  ✓ Database correctly rejected duplicate email")
            # Cleanup
            Citizen.query.filter_by(email=test_email).delete()
            db.session.commit()
        
        print("\n[STEP 2] Verify password hashing...")
        
        # Create a citizen and verify password is hashed
        test_password_plain = 'PlainTextPassword123'
        citizen = Citizen(
            name='Hash Test',
            email='hash.test@example.com',
            password=generate_password_hash(test_password_plain)
        )
        
        db.session.add(citizen)
        db.session.commit()
        
        saved = Citizen.query.filter_by(email='hash.test@example.com').first()
        
        # Password should NOT be stored as plain text
        if saved.password == test_password_plain:
            print(f"  ✗ Password stored as plain text (SECURITY ISSUE)")
            Citizen.query.filter_by(email='hash.test@example.com').delete()
            db.session.commit()
            return False
        
        print(f"  ✓ Password is properly hashed")
        print(f"    Hash: {saved.password[:50]}...")
        
        # Password should verify correctly
        if not check_password_hash(saved.password, test_password_plain):
            print(f"  ✗ Password hash verification failed")
            Citizen.query.filter_by(email='hash.test@example.com').delete()
            db.session.commit()
            return False
        
        print(f"  ✓ Password hash verification successful")
        
        # Cleanup
        Citizen.query.filter_by(email='hash.test@example.com').delete()
        db.session.commit()
        
        print("\n✓ DATABASE INTEGRITY TEST PASSED")
        return True

def main():
    """Run all tests"""
    print("\n" + "█"*70)
    print("COMPREHENSIVE USER REGISTRATION DATA STORAGE TEST")
    print("█"*70)
    
    # Cleanup first
    print("\nCleaning up previous test data...")
    cleanup_test_data()
    print("✓ Cleanup complete")
    
    # Run tests
    results = []
    
    results.append(("Citizen Registration", test_citizen_registration()))
    results.append(("Officer Registration (New)", test_officer_registration_new()))
    results.append(("Database Integrity", test_database_integrity()))
    
    # Summary
    print("\n" + "█"*70)
    print("TEST SUMMARY")
    print("█"*70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✓ PASSED" if result else "✗ FAILED"
        print(f"{test_name}: {status}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    print("█"*70 + "\n")
    
    return all(result for _, result in results)

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
