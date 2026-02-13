#!/usr/bin/env python
"""
Script to create missing ProjectStatus records for existing vivas.
This ensures that faculty members can see assigned groups in their dashboard.
"""

import sys
sys.path.insert(0, 'c:\\Users\\01-135231-091\\Desktop\\fyp')

from app import app, db, Viva, ProjectStatus

def fix_viva_assignments():
    with app.app_context():
        # Get all vivas
        vivas = Viva.query.all()
        print(f"Found {len(vivas)} vivas")
        
        created_count = 0
        
        for viva in vivas:
            # Check if ProjectStatus exists for this viva
            project_status = ProjectStatus.query.filter_by(
                group_id=viva.group_id,
                teacher_id=viva.teacher_id
            ).first()
            
            if not project_status:
                # Create missing ProjectStatus record
                project_status = ProjectStatus(
                    group_id=viva.group_id,
                    teacher_id=viva.teacher_id,
                    status='Pending'
                )
                db.session.add(project_status)
                created_count += 1
                print(f"✓ Created ProjectStatus for Viva: Group {viva.group.group_id} → Teacher {viva.teacher.first_name} {viva.teacher.last_name}")
            else:
                print(f"✓ ProjectStatus already exists for Group {viva.group.group_id} → Teacher {viva.teacher.first_name} {viva.teacher.last_name}")
        
        # Commit all changes
        if created_count > 0:
            db.session.commit()
            print(f"\n✓ Successfully created {created_count} ProjectStatus records")
        else:
            print(f"\n✓ All vivas already have ProjectStatus records")

if __name__ == '__main__':
    fix_viva_assignments()
