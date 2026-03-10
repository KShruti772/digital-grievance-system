#!/usr/bin/env python
"""Test to identify the BuildError and other routing issues"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from run import app

def test_submit_complaint_route():
    """Test the submit_complaint route that was causing the BuildError"""
    with app.app_context():
        with app.test_client() as client:
            print("\n" + "="*70)
            print("TESTING CITIZEN SUBMIT COMPLAINT ROUTE")
            print("="*70)
            
            # Try to access the submit complaint route without being logged in
            try:
                response = client.get('/citizen/submit')
                status = response.status_code
                location = response.headers.get('Location', 'N/A')
                
                print(f"[{status}] GET /citizen/submit")
                print(f"    Location header: {location}")
                
                if status == 302:
                    print("    ✓ Route redirects correctly (not throwing BuildError)")
                else:
                    print("    Response preview:", response.data.decode('utf-8')[:200])
                    
            except Exception as e:
                print(f"[ERROR] BuildError or other exception:")
                print(f"    {str(e)}")
                import traceback
                traceback.print_exc()
            
            # Test officer dashboard
            print("\n" + "-"*70)
            print("TESTING OFFICER DASHBOARD ROUTE")
            print("-"*70)
            
            try:
                response = client.get('/officer/dashboard')
                status = response.status_code
                location = response.headers.get('Location', 'N/A')
                
                print(f"[{status}] GET /officer/dashboard")
                print(f"    Location header: {location}")
                
                if status == 302:
                    print("    ✓ Route redirects correctly")
                else:
                    print("    Response preview:", response.data.decode('utf-8')[:200])
                    
            except Exception as e:
                print(f"[ERROR]:")
                print(f"    {str(e)}")
            
            # Test worker dashboard  
            print("\n" + "-"*70)
            print("TESTING WORKER DASHBOARD ROUTE")
            print("-"*70)
            
            try:
                response = client.get('/worker/dashboard')
                status = response.status_code
                location = response.headers.get('Location', 'N/A')
                
                print(f"[{status}] GET /worker/dashboard")
                print(f"    Location header: {location}")
                
                if status == 302:
                    print("    ✓ Route redirects correctly")
                else:
                    print("    Response preview:", response.data.decode('utf-8')[:200])
                    
            except Exception as e:
                print(f"[ERROR]:")
                print(f"    {str(e)}")
            
            print("\n" + "="*70)
            print("ROUTE TESTING COMPLETE")
            print("="*70 + "\n")

if __name__ == '__main__':
    test_submit_complaint_route()
