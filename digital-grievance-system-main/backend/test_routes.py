#!/usr/bin/env python
"""Test script to check Flask routes and identify issues"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from run import app

def test_routes():
    """Test all authentication routes"""
    with app.app_context():
        with app.test_client() as client:
            routes_to_test = [
                ('/', 'GET'),
                ('/home', 'GET'),
                ('/citizen_register', 'GET'),
                ('/citizen_login', 'GET'),
                ('/officer_register', 'GET'),
                ('/officer_login', 'GET'),
            ]
            
            print("Testing Routes:\n" + "="*60)
            for route, method in routes_to_test:
                try:
                    if method == 'GET':
                        response = client.get(route)
                        status = response.status_code
                        print(f"[{status}] {method} {route}")
                        if status >= 400:
                            print(f"      Error: {response.data.decode()[:200]}")
                except Exception as e:
                    print(f"[ERROR] {method} {route} - {str(e)}")
            
            print("\n" + "="*60)
            print("Route testing complete!")

if __name__ == '__main__':
    test_routes()
