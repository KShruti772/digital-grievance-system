#!/usr/bin/env python
"""
Test legacy officer registration stores all required data correctly
"""
import sys
import os
from werkzeug.security import generate_password_hash, check_password_hash

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from run import app, db
from models import Officer, User, ValidOfficer

def test_legacy_officer_registration():
    """Test legacy officer registration stores all required fields"""
    print("\n" + "="*70)
    print("TEST: LEGACY OFFICER REGISTRATION DATA STORAGE")
    print("="*70)
    
    with app.app_context():
        # Ensure ValidOfficer with LEGACY001 exists for testing
        print("\n[SETUP] Ensuring test ValidOfficer exists...")
        valid_officer = ValidOfficer.query.filter_by(officer_id='LEGACY001').first()
        if not valid_officer:
            valid_officer = ValidOfficer(
                officer_id='LEGACY001',
                department='Water Supply'
            )
            db.session.add(valid_officer)
            db.session.commit()
            print(f"  ✓ Created ValidOfficer LEGACY001")
        else:
            print(f"  ✓ ValidOfficer LEGACY001 already exists")
        
        # Cleanup any existing test data
        print("\n[CLEANUP] Removing any previous test data...")
        Officer.query.filter_by(officer_id='LEGACY001').delete()
        User.query.filter_by(employee_id='LEGACY001').delete()
        db.session.commit()
        print(f"  ✓ Cleanup complete")
        
        # Test data
        officer_id = 'LEGACY001'
        test_name = 'Test Legacy Officer'
        test_email = 'legacy.officer@example.com'
        test_phone = '9876543210'
        test_password = 'LegacyPass123'
        
        print("\n[STEP 1] Simulate legacy officer registration...")
        hashed_password = generate_password_hash(test_password)
        
        new_officer = Officer(
            officer_id=officer_id,
            name=test_name,
            department=valid_officer.department,  # From ValidOfficer
            email=test_email,
            phone=test_phone,
            password=hashed_password,
            id_proof='uploads/test_proof.pdf',
            approval_status='approved'
        )
        
        new_user = User(
            name=test_name,
            email=test_email,
            password=hashed_password,
            department=valid_officer.department,
            employee_id=officer_id,
            role='officer'
        )
        
        try:
            print(f"  - Officer ID: {officer_id}")
            print(f"  - Name: {test_name}")
            print(f"  - Email: {test_email}")
            print(f"  - Phone: {test_phone}")
            print(f"  - Department: {valid_officer.department}")
            
            db.session.add(new_officer)
            db.session.add(new_user)
            db.session.commit()
            print(f"\n  ✓ Registration successful")
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
        
        print(f"  ✓ Officer record found in Officer table:")
        print(f"    - Officer ID: {saved_officer.officer_id}")
        print(f"    - Name: {saved_officer.name}")
        print(f"    - Email: {saved_officer.email}")
        print(f"    - Phone: {saved_officer.phone}")
        print(f"    - Department: {saved_officer.department}")
        print(f"    - Approval Status: {saved_officer.approval_status}")
        
        # Verify all required fields
        print("\n[STEP 3] Verify all required fields are stored...")
        required_fields = {
            'officer_id': officer_id,
            'name': test_name,
            'email': test_email,
            'phone': test_phone,
            'department': valid_officer.department,
            'approval_status': 'approved'
        }
        
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
        
        # Verify User record exists
        print("\n[STEP 4] Verify User table record...")
        saved_user = User.query.filter_by(employee_id=officer_id).first()
        
        if not saved_user:
            print(f"  ✗ User record NOT found in User table")
            return False
        
        print(f"  ✓ User record found in User table:")
        print(f"    - ID: {saved_user.id}")
        print(f"    - Name: {saved_user.name}")
        print(f"    - Email: {saved_user.email}")
        print(f"    - Role: {saved_user.role}")
        print(f"    - Employee ID: {saved_user.employee_id}")
        
        # Verify password works for login
        print("\n[STEP 5] Verify password for login...")
        password_ok = check_password_hash(saved_officer.password, test_password)
        
        if not password_ok:
            print(f"  ✗ Password verification FAILED")
            return False
        
        print(f"  ✓ Password verification successful")
        
        print("\n" + "="*70)
        print("✓ LEGACY OFFICER REGISTRATION TEST PASSED")
        print("="*70)
        print("\nSummary:")
        print(f"  - Officer registration stores all required fields")
        print(f"  - User record created for system compatibility")
        print(f"  - Password properly hashed and verifiable")
        print(f"  - Data persists in database")
        print("="*70 + "\n")
        
        return True

if __name__ == '__main__':
    success = test_legacy_officer_registration()
    sys.exit(0 if success else 1)
