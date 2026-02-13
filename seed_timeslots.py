from app import app, db, TimeSlot
import datetime

with app.app_context():
    # Check if time slots already exist
    if TimeSlot.query.first():
        print("Time slots already exist in the database")
    else:
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        start = datetime.datetime.strptime('09:00', '%H:%M')
        end = datetime.datetime.strptime('17:00', '%H:%M')
        
        count = 0
        for day in days:
            current = start
            while current < end:
                slot_start = current.strftime('%H:%M')
                current += datetime.timedelta(minutes=30)
                slot_end = current.strftime('%H:%M')
                
                slot = TimeSlot(day=day, start_time=slot_start, end_time=slot_end)
                db.session.add(slot)
                count += 1
        
        db.session.commit()
        print(f"Successfully created {count} time slots")
        
        # Verify
        total = TimeSlot.query.count()
        print(f"Total time slots in database: {total}")
