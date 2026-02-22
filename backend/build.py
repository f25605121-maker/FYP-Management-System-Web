"""Build script for Render deployment.
Initialises the database on the persistent disk so data survives re-deploys.
"""
import os, sys

def main():
    # Make sure /opt/render/project/data exists (the Render persistent disk)
    data_dir = os.environ.get('RENDER_DATA_DIR', '/opt/render/project/data')
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'uploads'), exist_ok=True)

    # Set env so app.py picks up the right DB path
    os.environ.setdefault('RENDER', '1')
    os.environ.setdefault('FLASK_ENV', 'production')

    from app import app, db, User
    from werkzeug.security import generate_password_hash

    with app.app_context():
        db.create_all()
        print("[build] Database tables ensured.")

        # Create default admin if missing
        if not User.query.filter_by(role='admin').first():
            admin = User(
                email='admin@example.com',
                first_name='Admin',
                last_name='User',
                role='admin',
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("[build] Default admin user created (admin@example.com / admin123)")
        else:
            print("[build] Admin user already exists – skipping.")

    print("[build] Build complete.")

if __name__ == '__main__':
    main()
