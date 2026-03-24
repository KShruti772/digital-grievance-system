#!/usr/bin/env python
"""
Test JSON Serialization Fix for Complaint Objects
================================================

This test verifies that:
1. Complaint.to_dict() method works correctly
2. Officer dashboard can serialize complaints for JSON
3. Template receives JSON-safe complaint dictionaries
4. No TypeError when using tojson filter
"""

import json
from run import app, db
from models import Complaint, User, Officer

print("=" * 70)
print("COMPLAINT JSON SERIALIZATION TEST")
print("=" * 70)

with app.app_context():
    # Test 1: Create test data
    print("\n[TEST 1] Setup Test Data")
    print("-" * 70)
    
    # Create a test user if doesn't exist
    test_user = User.query.filter_by(email="test_complaint@example.com").first()
    if not test_user:
        test_user = User(
            name="Test Complaint User",
            email="test_complaint@example.com",
            password="test123",
            role='citizen'
        )
        db.session.add(test_user)
        db.session.commit()
        print("✓ Created test citizen user")
    else:
        print("✓ Test citizen user exists")
    
    # Create a test complaint
    test_complaint = Complaint(
        user_id=test_user.id,
        title="Test Complaint for JSON Serialization",
        description="This complaint is used to test JSON serialization",
        category="Roads & Infrastructure",
        location="Test Avenue, Test City",
        latitude=28.6139,
        longitude=77.2090,
        status="Pending",
        priority="High"
    )
    db.session.add(test_complaint)
    db.session.commit()
    print(f"✓ Created test complaint (ID: {test_complaint.id})")
    
    # Test 2: Test to_dict() method
    print("\n[TEST 2] Test to_dict() Method")
    print("-" * 70)
    
    try:
        complaint_dict = test_complaint.to_dict()
        print("✓ to_dict() executed successfully")
        print(f"  - Returns type: {type(complaint_dict).__name__}")
        print(f"  - Contains {len(complaint_dict)} fields")
        print(f"  - Sample: id={complaint_dict['id']}, title='{complaint_dict['title']}'")
    except Exception as e:
        print(f"✗ to_dict() failed: {str(e)}")
        exit(1)
    
    # Test 3: JSON Serialization
    print("\n[TEST 3] JSON Serialization")
    print("-" * 70)
    
    try:
        json_str = json.dumps(complaint_dict)
        print("✓ Dictionary is JSON serializable")
        print(f"  - JSON length: {len(json_str)} characters")
        print(f"  - Successfully deserialized")
        
        # Verify we can convert back
        deserialized = json.loads(json_str)
        print(f"  - Deserialized type: {type(deserialized).__name__}")
        print(f"  - Deserialized id: {deserialized['id']}")
    except TypeError as e:
        print(f"✗ JSON serialization failed: {str(e)}")
        exit(1)
    
    # Test 4: Simulate Officer Dashboard Route
    print("\n[TEST 4] Simulate Officer Dashboard Route")
    print("-" * 70)
    
    try:
        # Get all complaints (simulating dashboard route)
        complaints_query = Complaint.query.all()
        print(f"✓ Query returned {len(complaints_query)} complaints")
        
        # Convert to dictionaries (what officer_routes does now)
        complaints_dict = [c.to_dict() for c in complaints_query]
        print(f"✓ Converted {len(complaints_dict)} complaints to dictionaries")
        
        # Verify each can be JSON serialized
        for i, complaint_dict in enumerate(complaints_dict):
            json.dumps(complaint_dict)
        print(f"✓ All {len(complaints_dict)} complaint dictionaries are JSON-safe")
        
    except Exception as e:
        print(f"✗ Dashboard route simulation failed: {str(e)}")
        exit(1)
    
    # Test 5: Template tojson filter simulation
    print("\n[TEST 5] Template tojson Filter Simulation")
    print("-" * 70)
    
    try:
        # Simulate what Jinja2 tojson filter does
        complaints_for_js = json.dumps(complaints_dict)
        print("✓ Successfully serialized complaints for JavaScript")
        print(f"  - Output starts with: {complaints_for_js[:50]}...")
        print(f"  - Output is valid JSON: ✓")
        
        # Verify the JSON can be parsed by JavaScript
        parsed = json.loads(complaints_for_js)
        print(f"  - JavaScript can parse: {len(parsed)} complaints")
        
        # Check critical fields for officer_dashboard.html
        if parsed and len(parsed) > 0:
            sample = parsed[0]
            required_fields = ['id', 'title', 'latitude', 'longitude', 'status', 'category', 'location']
            missing = [f for f in required_fields if f not in sample]
            if missing:
                print(f"✗ Missing fields: {missing}")
                exit(1)
            print(f"  - Contains all required fields for dashboard")
        
    except Exception as e:
        print(f"✗ Template filter simulation failed: {str(e)}")
        exit(1)
    
    # Clean up
    print("\n[CLEANUP]")
    print("-" * 70)
    db.session.delete(test_complaint)
    db.session.commit()
    print("✓ Test data cleaned up")
    
    # Summary
    print("\n" + "=" * 70)
    print("✓ ALL TESTS PASSED")
    print("=" * 70)
    print("\nSummary:")
    print("  ✓ Complaint.to_dict() converts SQLAlchemy objects to dicts")
    print("  ✓ All fields are JSON-serializable (including datetime)")
    print("  ✓ Officer dashboard can convert complaints safely")
    print("  ✓ Templates can use tojson filter without errors")
    print("  ✓ Officer dashboard has all required fields")
    print("\nThe JSON serialization fix is working correctly!")
    print("=" * 70)
