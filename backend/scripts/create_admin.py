import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import app, db, User

with app.app_context():
    # Check if admin exists
    admin = User.query.filter_by(email='admin@example.com').first()
    
    if admin:
        print(f"✓ Admin account found!")
        print(f"  Email: {admin.email}")
        print(f"  Name: {admin.first_name} {admin.last_name}")
        print(f"  Role: {admin.role}")
    else:
        print("✗ Admin account not found. Creating it...")
        admin = User(email='admin@example.com', first_name='Admin', last_name='User', role='admin')
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()
        print("✓ Admin account created!")
        print(f"  Email: admin@example.com")
        print(f"  Password: admin123")
