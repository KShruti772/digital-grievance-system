#!/usr/bin/env python
"""Final comprehensive test after fixes"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from run import app

def test_complete_flow():
    """Test complete user flow through the system"""
    with app.app_context():
        with app.test_client() as client:
            print("\n" + "="*70)
            print("COMPREHENSIVE AUTHENTICATION SYSTEM TEST")
            print("="*70)
            
            # Test 1: All routes return valid status codes
            print("\n1. Testing All Routes for Errors:")
            print("-" * 70)
            
            routes_test = [
                ('/', 302, 'Home page should redirect'),
                ('/home', 200, 'Home page'),
                ('/citizen_register', 200, 'Citizen registration form'),
                ('/citizen_login', 200, 'Citizen login form'),
                ('/officer_register', 200, 'Officer registration form'),
                ('/officer_login', 200, 'Officer login form'),
                ('/login', 302, 'Old /login should redirect to /home'),
                ('/register', 302, 'Old /register should redirect to /home'),
            ]
            
            all_passed = True
            for route, expected_status, description in routes_test:
                response = client.get(route)
                status = response.status_code
                passed = status == expected_status
                symbol = "✓" if passed else "✗"
                print(f"{symbol} [{status}] {route:25} - {description}")
                
                if not passed:
                    print(f"    Expected: {expected_status}, Got: {status}")
                    all_passed = False
            
            # Test 2: Template references are valid
            print("\n2. Testing Template Links and References:")
            print("-" * 70)
            
            link_tests = [
                ('/citizen_register', '/citizen_login', 'Reg links to Login'),
                ('/citizen_register', '/home', 'Reg has home link'),
                ('/citizen_login', '/citizen_register', 'Login links to Reg'),
                ('/citizen_login', '/home', 'Login has home link'),
                ('/officer_register', '/officer_login', 'Off-Reg links to Login'),
                ('/officer_login', '/officer_register', 'Off-Login links to Reg'),
                ('/home', '/citizen_register', 'Home links to Citizen Reg'),
                ('/home', '/officer_login', 'Home links to Officer Login'),
            ]
            
            for route, reference, description in link_tests:
                response = client.get(route)
                html = response.data.decode('utf-8')
                has_link = reference in html or f'href="{reference}"' in html or f"href='{reference}'" in html
                symbol = "✓" if has_link else "✗"
                print(f"{symbol} {description:40} ({route} -> {reference})")
                
                if not has_link:
                    all_passed = False
            
            # Test 3: Form submission flow
            print("\n3. Testing Citizen Registration Form Submission:")
            print("-" * 70)
            
            test_data = {
                'name': 'Test Citizen',
                'email': 'testcitizen@example.com',
                'password': 'testpass123',
                'confirm_password': 'testpass123'
            }
            
            response = client.post('/citizen_register', data=test_data)
            if response.status_code == 302:  # Should redirect to login
                location = response.headers.get('Location', '')
                if 'citizen_login' in location:
                    print(f"✓ Registration form submission successful")
                    print(f"    Redirects to: {location}")
                else:
                    print(f"✗ Registration redirects to wrong location: {location}")
                    all_passed = False
            else:
                print(f"✗ Registration form failed: {response.status_code}")
                all_passed = False
            
            # Test 4: Check for 404 errors on all user-facing pages
            print("\n4. Checking for 404 Errors:")
            print("-" * 70)
            
            has_404 = False
            routes_for_404_check = [
                '/', '/home', '/citizen_register', '/citizen_login',
                '/officer_register', '/officer_login', '/login', '/register'
            ]
            
            for route in routes_for_404_check:
                response = client.get(route)
                if response.status_code == 404:
                    print(f"✗ Found 404 on {route}")
                    has_404 = True
                    all_passed = False
            
            if not has_404:
                print("✓ No 404 errors found on any user-facing routes")
            
            # Summary
            print("\n" + "="*70)
            if all_passed:
                print("SUCCESS! All tests passed!")
                print("The authentication system is working correctly.")
            else:
                print("WARNING! Some tests failed.")
                print("Please review the errors above.")
            print("="*70 + "\n")
            
            return all_passed

if __name__ == '__main__':
    success = test_complete_flow()
    sys.exit(0 if success else 1)
