import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from models import db, User, Citizen, Officer
from run import app
from werkzeug.security import generate_password_hash, check_password_hash

def is_hashed(password):
    """Check if a password is already hashed by trying to verify it against itself"""
    try:
        return check_password_hash(password, password)
    except:
        return False

def update_plain_text_passwords():
    """Update any plain text passwords to hashed versions"""
    with app.app_context():
        print("Checking for plain text passwords...")

        # Update User table
        users = User.query.all()
        updated_users = 0
        for user in users:
            if not is_hashed(user.password):
                user.password = generate_password_hash(user.password)
                updated_users += 1
                print(f"Updated User: {user.email}")

        # Update Citizen table
        citizens = Citizen.query.all()
        updated_citizens = 0
        for citizen in citizens:
            if not is_hashed(citizen.password):
                citizen.password = generate_password_hash(citizen.password)
                updated_citizens += 1
                print(f"Updated Citizen: {citizen.email}")

        # Update Officer table
        officers = Officer.query.all()
        updated_officers = 0
        for officer in officers:
            if not is_hashed(officer.password):
                officer.password = generate_password_hash(officer.password)
                updated_officers += 1
                print(f"Updated Officer: {officer.officer_id}")

        if updated_users + updated_citizens + updated_officers > 0:
            db.session.commit()
            print(f"\nSuccessfully updated {updated_users} users, {updated_citizens} citizens, and {updated_officers} officers.")
        else:
            print("\nNo plain text passwords found. All passwords are already hashed.")

if __name__ == '__main__':
    update_plain_text_passwords()