from app import app, db, User

with app.app_context():
    users = [
        ('admin@example.com', 'admin123', 'Admin', 'User', 'admin'),
        ('student@example.com', 'student123', 'Sarah', 'Johnson', 'student'),
        ('supervisor@example.com', 'supervisor123', 'David', 'Johnson', 'supervisor'),
        ('teacher@example.com', 'teacher123', 'John', 'Smith', 'cordinator'),
    ]
    
    for email, password, first_name, last_name, role in users:
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"✓ {email} already exists")
        else:
            user = User(email=email, first_name=first_name, last_name=last_name, role=role)
            user.set_password(password)
            db.session.add(user)
            try:
                db.session.commit()
                print(f"✓ Created {email} with password {password}")
            except Exception as e:
                db.session.rollback()
                print(f"✗ Failed to create {email}: {e}")
    
    print("\nAll sample users are ready!")
