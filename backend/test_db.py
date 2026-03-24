#!/usr/bin/env python
"""Test script to check database operations and form submissions"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from run import app, db
from models import Citizen, Officer, ValidOfficer

def test_database_operations():
    """Test database operations"""
    with app.app_context():
        print("Testing Database Operations:\n" + "="*60)
        
        try:
            # Check database tables
            inspector = db.inspect(db.engine)
            tables = inspector.get_table_names()
            print(f"[OK] Database Tables: {', '.join(tables)}")
        except Exception as e:
            print(f"[ERROR] Cannot inspect database: {str(e)}")
            return
        
        try:
            # Check ValidOfficer table
            valid_officers = ValidOfficer.query.all()
            print(f"[OK] ValidOfficer records: {len(valid_officers)}")
            for officer in valid_officers:
                print(f"      - {officer.officer_id}: {officer.department}")
        except Exception as e:
            print(f"[ERROR] Cannot query ValidOfficer: {str(e)}")
        
        try:
            # Check Citizen table
            citizens = Citizen.query.all()
            print(f"[OK] Citizen records: {len(citizens)}")
        except Exception as e:
            print(f"[ERROR] Cannot query Citizen: {str(e)}")
        
        try:
            # Check Officer table
            officers = Officer.query.all()
            print(f"[OK] Officer records: {len(officers)}")
        except Exception as e:
            print(f"[ERROR] Cannot query Officer: {str(e)}")
        
        print("\n" + "="*60)
        print("Testing Form Submission (Citizen Registration)...")
        print("="*60)
        
        with app.test_client() as client:
            # Test citizen registration form submission
            test_data = {
                'name': 'Test User',
                'email': 'test@example.com',
                'password': 'password123',
                'confirm_password': 'password123'
            }
            
            try:
                response = client.post('/citizen_register', data=test_data, follow_redirects=False)
                print(f"[{response.status_code}] POST /citizen_register")
                print(f"      Location: {response.headers.get('Location', 'N/A')}")
                
                if response.status_code >= 400:
                    print(f"      Response: {response.data.decode('utf-8')[:200]}")
            except Exception as e:
                print(f"[ERROR] Form submission: {str(e)}")
                import traceback
                traceback.print_exc()
        
        print("\n" + "="*60)
        print("Database and form submission test complete!")

if __name__ == '__main__':
    test_database_operations()
