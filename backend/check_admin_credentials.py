"""
Check admin credentials in database
"""

import sqlite3
from werkzeug.security import check_password_hash

def check_admin_credentials():
    """Check admin credentials in database"""
    
    try:
        conn = sqlite3.connect('instance/fyp.db')
        cursor = conn.cursor()
        
        cursor.execute('SELECT email, password_hash FROM user WHERE email=?', ('admin@example.com',))
        result = cursor.fetchone()
        
        if result:
            email, password_hash = result
            print('Admin user found:')
            print(f'Email: {email}')
            print(f'Password hash exists: {"Yes" if password_hash else "No"}')
            
            if password_hash:
                print('\nTesting passwords:')
                admin_12345 = check_password_hash(password_hash, 'Admin@12345')
                old_password = check_password_hash(password_hash, 'change-this-strong-password')
                
                print(f'Password "Admin@12345" correct: {admin_12345}')
                print(f'Password "change-this-strong-password" correct: {old_password}')
                
                if not admin_12345 and not old_password:
                    print('\n❌ Neither password is working!')
                    print('The password hash might be corrupted.')
                elif admin_12345:
                    print('\n✅ Password "Admin@12345" is correct!')
                elif old_password:
                    print('\n✅ Password "change-this-strong-password" is correct!')
            else:
                print('❌ No password hash found!')
        else:
            print('❌ Admin user not found in database!')
        
        conn.close()
        
    except Exception as e:
        print(f'❌ Error checking credentials: {str(e)}')

if __name__ == '__main__':
    check_admin_credentials()
