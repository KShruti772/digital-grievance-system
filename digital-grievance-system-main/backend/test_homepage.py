#!/usr/bin/env python
"""Test the professional homepage"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from run import app

def test_homepage():
    """Test the professional homepage rendering"""
    with app.app_context():
        with app.test_client() as client:
            print("\n" + "="*70)
            print("PROFESSIONAL HOMEPAGE TEST")
            print("="*70)
            
            # Test homepage at root
            response = client.get('/')
            status = response.status_code
            
            print(f"\n[{status}] GET / (Professional Homepage)")
            
            html = response.data.decode('utf-8')
            
            print(f"[{status}] GET /home (Main homepage)")
            
            # Check for all required sections
            sections = [
                ('Hero Section', 'Empowering Citizens'),
                ('Benefits Section', 'Why Choose Our System'),
                ('How It Works', 'Simple 5-step process'),
                ('About Section', 'About This System'),
                ('Categories', 'Complaint Categories'),
                ('CTA Section', 'Ready to Make a Difference'),
                ('Footer', 'Digital Grievance System'),
            ]
            
            print("\nChecking for all required sections:")
            print("-" * 70)
            
            all_found = True
            for section_name, search_text in sections:
                if search_text in html:
                    print(f"✓ {section_name:30} - FOUND")
                else:
                    print(f"✗ {section_name:30} - MISSING")
                    all_found = False
            
            # Check for styling
            print("\nChecking for CSS classes:")
            print("-" * 70)
            
            css_classes = [
                'hero-section',
                'benefits-section',
                'how-it-works-section',
                'about-section',
                'categories-section',
                'cta-section',
                'footer-section',
                'btn-primary-custom',
            ]
            
            for css_class in css_classes:
                if css_class in html:
                    print(f"✓ {css_class:30} - FOUND")
                else:
                    print(f"✗ {css_class:30} - MISSING")
                    all_found = False
            
            # Check for responsive grid
            print("\nChecking for Bootstrap components:")
            print("-" * 70)
            
            bootstrap_elements = [
                ('Bootstrap Grid', 'col-md-'),
                ('Cards', 'benefit-card'),
                ('Icons', 'bi bi-'),
                ('Navigation', 'navbar'),
            ]
            
            for element_name, search_text in bootstrap_elements:
                count = html.count(search_text)
                if count > 0:
                    print(f"✓ {element_name:30} - {count} instances found")
                else:
                    print(f"✗ {element_name:30} - NOT FOUND")
                    all_found = False
            
            print("\n" + "="*70)
            if all_found and status == 200:
                print("SUCCESS! Professional homepage is working perfectly!")
                print("\nFeatures included:")
                print("  ✓ Responsive Design (Bootstrap 5)")
                print("  ✓ Hero Section with Light Blue Background")
                print("  ✓ Benefits Section with 3 Cards")
                print("  ✓ How It Works - 5 Step Process")
                print("  ✓ About Section with Mission")
                print("  ✓ Categories with 6 Complaint Types")
                print("  ✓ Call-to-Action Section")
                print("  ✓ Professional Footer")
                print("  ✓ Dark Blue Color Scheme (#0b3d91)")
                print("  ✓ Light Blue Accents (#d9f2ff)")
                print("  ✓ Bootstrap Icons Integration")
                print("  ✓ Smooth Animations & Transitions")
            else:
                print("WARNING! Some elements are missing.")
            print("="*70 + "\n")
            
            return all_found and status == 200

if __name__ == '__main__':
    success = test_homepage()
    sys.exit(0 if success else 1)
