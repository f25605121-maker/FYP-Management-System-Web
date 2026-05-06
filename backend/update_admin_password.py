"""
Script to update admin password to Admin@12345
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User

def update_admin_password():
    """Update admin password to Admin@12345"""
    
    with app.app_context():
        # Find admin user
        admin = User.query.filter_by(email='admin@example.com').first()
        
        if admin:
            # Update password
            admin.set_password('Admin@12345')
            db.session.commit()
            print("✅ Admin password updated successfully!")
            print("   Email: admin@example.com")
            print("   New Password: Admin@12345")
        else:
            print("❌ Admin user not found!")
            return False
    
    return True

if __name__ == '__main__':
    update_admin_password()
