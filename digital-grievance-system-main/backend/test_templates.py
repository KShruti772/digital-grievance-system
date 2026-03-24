#!/usr/bin/env python
"""Test script to detect template rendering errors"""

import sys
import os
from io import StringIO

sys.path.insert(0, os.path.dirname(__file__))

from run import app

def test_template_rendering():
    """Test template rendering for all routes"""
    with app.app_context():
        with app.test_client() as client:
            routes_to_test = [
                '/',
                '/home',
                '/citizen_register',
                '/citizen_login',
                '/officer_register',
                '/officer_login',
            ]
            
            print("Testing Template Rendering:\n" + "="*60)
            for route in routes_to_test:
                try:
                    response = client.get(route)
                    status = response.status_code
                    
                    if status == 200:
                        # Check if HTML contains expected elements
                        html = response.data.decode('utf-8')
                        has_form = '<form' in html
                        has_bootstrap = 'bootstrap' in html.lower()
                        has_content = len(html) > 100
                        
                        print(f"[{status}] {route}")
                        print(f"      - HTML Length: {len(html)} bytes")
                        print(f"      - Has Form: {has_form}")
                        print(f"      - Has Bootstrap: {has_bootstrap}")
                        if not has_content:
                            print(f"      - WARNING: Template appears empty!")
                            print(f"      - Content: {html[:200]}")
                    else:
                        print(f"[{status}] {route} - ERROR")
                        print(f"      Response: {response.data.decode('utf-8')[:200]}")
                        
                except Exception as e:
                    print(f"[ERROR] {route}")
                    print(f"      Exception: {str(e)}")
                    import traceback
                    traceback.print_exc()
            
            print("\n" + "="*60)
            print("Template rendering test complete!")

if __name__ == '__main__':
    test_template_rendering()
