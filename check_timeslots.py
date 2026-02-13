from app import app, db, TimeSlot

with app.app_context():
    slots = TimeSlot.query.all()
    print(f"Total slots: {len(slots)}")
    for slot in slots:
        print(f"ID: {slot.id}, Day: '{slot.day}', Time: {slot.start_time}-{slot.end_time}")
