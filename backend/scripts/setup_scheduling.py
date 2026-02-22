from app import app, db, TimeSlot, Room

with app.app_context():
    # Check and create time slots
    count = TimeSlot.query.count()
    print(f"Current TimeSlots: {count}")
    
    if count == 0:
        print("\n✓ Creating default time slots...")
        
        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
        times = [
            ('08:00', '09:00'),
            ('09:00', '10:00'),
            ('10:00', '11:00'),
            ('11:00', '12:00'),
            ('13:00', '14:00'),
            ('14:00', '15:00'),
            ('15:00', '16:00'),
            ('16:00', '17:00'),
        ]
        
        for day in days:
            for start, end in times:
                slot = TimeSlot(day=day, start_time=start, end_time=end)
                db.session.add(slot)
        
        db.session.commit()
        print(f"✓ Created {len(days) * len(times)} time slots")
    
    # Check and create rooms
    room_count = Room.query.count()
    print(f"\nCurrent Rooms: {room_count}")
    
    if room_count == 0:
        print("✓ Creating default rooms...")
        rooms_to_create = [
            ('A101', 30),
            ('A102', 30),
            ('A103', 30),
            ('Lab1', 25),
            ('Lab2', 25),
            ('Conference Room', 50),
        ]
        for room_name, capacity in rooms_to_create:
            room = Room(name=room_name, capacity=capacity)  # Use 'name' not 'room_name'
            db.session.add(room)
        db.session.commit()
        print(f"✓ Created {len(rooms_to_create)} rooms")
    
    print("\n✓ All scheduling data is ready!")
