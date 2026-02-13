from app import app, db, User

with app.app_context():
    students = [
        ('student1@example.com', 'Ahmed Khan', 'Khan', 'CS'),
        ('student2@example.com', 'Fatima Ali', 'Ali', 'CS'),
        ('student3@example.com', 'Hassan Ahmed', 'Ahmed', 'IT'),
        ('student4@example.com', 'Zainab Hassan', 'Hassan', 'IT'),
        ('student5@example.com', 'Muhammad Ali', 'Ali', 'AI'),
        ('student6@example.com', 'Ayesha Khan', 'Khan', 'AI'),
        ('student7@example.com', 'Omar Malik', 'Malik', 'CS'),
        ('student8@example.com', 'Layla Ahmed', 'Ahmed', 'IT'),
        ('student9@example.com', 'Sara Hassan', 'Hassan', 'AI'),
        ('student10@example.com', 'Ali Raza', 'Raza', 'CS'),
    ]
    
    created_count = 0
    existing_count = 0
    
    for email, first_name, last_name, program in students:
        # Check if student already exists
        user = User.query.filter_by(email=email).first()
        if user:
            print(f"  Student {email} already exists")
            existing_count += 1
        else:
            # Create new student
            new_student = User(
                email=email, 
                first_name=first_name, 
                last_name=last_name, 
                role='student',
                program=program,
                semester='Final'
            )
            new_student.set_password('student123')
            db.session.add(new_student)
            created_count += 1
    
    try:
        db.session.commit()
        print(f"\nResults:")
        print(f"  Created: {created_count} new students")
        print(f"  Already existed: {existing_count} students")
        print(f"  Total: {created_count + existing_count} students")
        print(f"\nAll students can login with password: student123")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
