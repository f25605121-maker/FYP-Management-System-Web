import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
# Import only what we need for database connection, not the models
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import inspect, text

# Create a minimal app just for database operations
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:\\Users\\01-135231-091\\Desktop\\PROJECTS\\fyp\\backend\\instance\\fyp.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

def create_remark_response_table():
    """Create the remark_response table if it doesn't exist"""
    with app.app_context():
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        
        if 'remark_response' in tables:
            print("Dropping existing remark_response table...")
            with db.engine.begin() as conn:
                conn.execute(text("DROP TABLE remark_response"))
            print("Table dropped")
        
        print("Creating remark_response table...")
        
        # Create table using raw SQL for better control
        create_table_sql = """
        CREATE TABLE remark_response (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            content TEXT NOT NULL,
            timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            remark_id INTEGER NOT NULL,
            responder_id INTEGER NOT NULL,
            FOREIGN KEY (remark_id) REFERENCES remark (id),
            FOREIGN KEY (responder_id) REFERENCES user (id)
        )
        """
        
        try:
            with db.engine.begin() as conn:
                conn.execute(text(create_table_sql))
            print("remark_response table created successfully")
            return True
        except Exception as e:
            print(f"Error creating table: {e}")
            return False

if __name__ == "__main__":
    success = create_remark_response_table()
    if success:
        print("Migration completed successfully!")
    else:
        print("Migration failed!")