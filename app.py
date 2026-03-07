"""
Entry point for the FYP Management System.
This file sits at the project root and imports the Flask app from backend/.
"""
import os
from backend.app import app

if __name__ == '__main__':
    debug = os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', debug=debug)
