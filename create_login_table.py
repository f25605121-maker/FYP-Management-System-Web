from app import app, db, LoginAttempt

with app.app_context():
    # Create the LoginAttempt table
    try:
        db.create_all()
        print("LoginAttempt table created successfully!")
        
        # Check if table exists
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'login_attempt' in tables:
            print("✓ login_attempt table is ready")
            login_count = LoginAttempt.query.count()
            print(f"  Current login records: {login_count}")
        else:
            print("✗ login_attempt table not found")
    except Exception as e:
        print(f"Error: {e}")
