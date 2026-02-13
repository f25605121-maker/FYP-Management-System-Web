from app import app, db, User

with app.app_context():
    supervisors = [
        ('supervisor1@example.com', 'Dr. Muhammad', 'Hassan', 'PhD', 'Machine Learning'),
        ('supervisor2@example.com', 'Prof. Fatima', 'Khan', 'PhD', 'Cybersecurity'),
        ('supervisor3@example.com', 'Dr. Ahmed', 'Ali', 'MS', 'Web Development'),
        ('supervisor4@example.com', 'Prof. Sara', 'Ahmed', 'PhD', 'Blockchain'),
    ]
    
    created_count = 0
    existing_count = 0
    
    for email, first_name, last_name, degree, specialization in supervisors:
        # Check if supervisor already exists
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"  Supervisor {email} already exists")
            existing_count += 1
        else:
            # Create new supervisor
            new_supervisor = User(
                email=email, 
                first_name=first_name, 
                last_name=last_name, 
                role='supervisor',
                highest_degree=degree,
                specialization=specialization,
                affiliation='NUTECH'
            )
            new_supervisor.set_password('supervisor123')
            db.session.add(new_supervisor)
            created_count += 1
    
    try:
        db.session.commit()
        print(f"\nResults:")
        print(f"  Created: {created_count} new supervisors")
        print(f"  Already existed: {existing_count} supervisors")
        print(f"  Total: {created_count + existing_count} supervisors")
        print(f"\nAll supervisors can login with password: supervisor123")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
