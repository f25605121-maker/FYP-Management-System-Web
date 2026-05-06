"""
Test script to verify admin login with new password
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User

def test_admin_login():
    """Test admin login with new password"""
    
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if admin:
            print("Admin user found:")
            print(f"  Email: {admin.email}")
            print(f"  Name: {admin.first_name} {admin.last_name}")
            print(f"  Role: {admin.role}")
            
            # Test password verification
            print("\nTesting password verification:")
            print(f"  Password 'Admin@12345' correct: {admin.check_password('Admin@12345')}")
            print(f"  Password 'change-this-strong-password' correct: {admin.check_password('change-this-strong-password')}")
            
            if admin.check_password('Admin@12345'):
                print("\n✅ SUCCESS: New password 'Admin@12345' is working!")
            else:
                print("\n❌ ERROR: New password is not working!")
                
        else:
            print("❌ Admin user not found!")

if __name__ == '__main__':
    test_admin_login()
