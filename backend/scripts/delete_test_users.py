#!/usr/bin/env python
"""
Script to delete all test user credentials except admin
"""
import os
import sys
from app import app, db, User, GroupMember, StudentGroup, Remark, LoginAttempt

def delete_test_users():
    with app.app_context():
        # List of emails to delete
        emails_to_delete = [
            # Students
            'student@example.com',
            'student1@example.com',
            'student2@example.com',
            'student3@example.com',
            'student4@example.com',
            'student5@example.com',
            'student6@example.com',
            'student7@example.com',
            'student8@example.com',
            'student9@example.com',
            'student10@example.com',
            # Supervisors
            'supervisor@example.com',
            'supervisor1@example.com',
            'supervisor2@example.com',
            'supervisor3@example.com',
            'supervisor4@example.com',
            # Teacher/cordinator
            'teacher@example.com',
        ]
        
        deleted_count = 0
        
        # First, get all users to delete
        users_to_delete = User.query.filter(User.email.in_(emails_to_delete)).all()
        
        for user in users_to_delete:
            # Delete group members for this user
            GroupMember.query.filter_by(user_id=user.id).delete()
            
            # Delete remarks where this user is the teacher
            Remark.query.filter_by(teacher_id=user.id).delete()
            
            # Delete login attempts for this user
            LoginAttempt.query.filter_by(user_id=user.id).delete()
            
            # Delete the user
            db.session.delete(user)
            deleted_count += 1
            print(f"✓ Deleted: {user.email}")
        
        db.session.commit()
        
        # Show remaining users
        remaining_users = User.query.all()
        print(f"\n{'='*50}")
        print(f"Total deleted: {deleted_count}")
        print(f"Remaining users: {len(remaining_users)}")
        print(f"{'='*50}\n")
        
        for user in remaining_users:
            print(f"  • {user.first_name} {user.last_name} ({user.email}) - {user.role}")

if __name__ == '__main__':
    delete_test_users()
    print("\n✓ Test users deleted successfully! Only admin remains.")
