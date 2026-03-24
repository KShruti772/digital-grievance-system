#!/usr/bin/env python
"""Comprehensive test to find the actual error"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from run import app

def test_all_routes():
    """Test both old and new routes"""
    with app.app_context():
        with app.test_client() as client:
            # Test NEW routes (should work)
            new_routes = [
                ('/citizen_register', 200),
                ('/citizen_login', 200),
                ('/officer_register', 200),
                ('/officer_login', 200),
                ('/home', 200),
            ]
            
            # Test OLD routes (might not exist)
            old_routes = [
                ('/login', None),  # None = unknown expected status
                ('/register', None),
            ]
            
            print("Testing NEW Routes (Auth System):\n" + "="*60)
            for route, expected_status in new_routes:
                response = client.get(route)
                status = response.status_code
                status_ok = "✓" if status == expected_status else "✗"
                print(f"{status_ok} [{status}] {route}")
                if status != expected_status:
                    print(f"   Content preview: {response.data.decode('utf-8')[:100]}")
            
            print("\n\nTesting OLD Routes (might not exist):\n" + "="*60)
            for route, _ in old_routes:
                response = client.get(route)
                status = response.status_code
                print(f"[{status}] {route}")
                if status >= 400:
                    print(f"   This route is NOT defined (404 or similar)")
                else:
                    print(f"   This route EXISTS (might cause conflicts)")
            
            # Check template references
            print("\n\nChecking for broken template references:\n" + "="*60)
            test_pages = [
                ('/citizen_register', '/citizen_login'),
                ('/citizen_login', '/citizen_register'),
                ('/home', '/citizen_register'),
                ('/', 'base.html'),
            ]
            
            for route, reference in test_pages:
                response = client.get(route)
                html = response.data.decode('utf-8')
                if reference in html or f'"{reference}"' in html or f"'{reference}'" in html:
                    print(f"✓ {route} -> has reference to {reference}")
                else:
                    # Don't print if reference is NOT in HTML (might be expected)
                    pass

if __name__ == '__main__':
    test_all_routes()
