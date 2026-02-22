"""
Entry point to run the FYP Management System.
This file sits at the project root and imports the Flask app from backend/.
"""
import sys
import os

# Add backend directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend'))

from app import app

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
