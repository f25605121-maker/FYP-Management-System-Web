"""
Direct database update for admin password
"""

import sqlite3
from werkzeug.security import generate_password_hash

def fix_admin_password():
    """Directly update admin password in SQLite database"""
    
    try:
        # Connect to database
        conn = sqlite3.connect('instance/fyp.db')
        cursor = conn.cursor()
        
        # Generate new password hash
        new_password = 'Admin@12345'
        password_hash = generate_password_hash(new_password)
        
        # Update admin password
        cursor.execute(
            'UPDATE user SET password_hash = ? WHERE email = ?',
            (password_hash, 'admin@example.com')
        )
        
        conn.commit()
        
        # Verify update
        cursor.execute('SELECT email FROM user WHERE email = ?', ('admin@example.com',))
        result = cursor.fetchone()
        
        if result:
            print(f"✅ Admin password updated successfully!")
            print(f"   Email: {result[0]}")
            print(f"   New Password: {new_password}")
        else:
            print("❌ Admin user not found!")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Error updating password: {str(e)}")
        return False

if __name__ == '__main__':
    fix_admin_password()
