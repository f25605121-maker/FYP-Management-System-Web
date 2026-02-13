# FYP Management System

A comprehensive platform for managing Final Year Projects, built with Flask and Bootstrap.

## Features

- User authentication (login/signup)
- Role-based access (Students, Teachers, Supervisors, Administrators)
- Modern and responsive UI
- Secure password handling
- SQLite database for data persistence

## Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd fyp
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
```

3. Activate the virtual environment:
- Windows:
```bash
venv\Scripts\activate
```
- Unix/MacOS:
```bash
source venv/bin/activate
```

4. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Make sure your virtual environment is activated

2. Run the Flask application:
```bash
python app.py
```

3. Open your web browser and navigate to:
```
http://localhost:5000
```

## Project Structure

```
fyp/
├── app.py              # Main Flask application
├── requirements.txt    # Python dependencies
├── static/            # Static files
│   ├── css/          # CSS stylesheets
│   ├── js/           # JavaScript files
│   └── images/       # Image assets
└── templates/        # HTML templates
    ├── index.html    # Landing page
    ├── login.html    # Login page
    └── signup.html   # Registration page
```

## Security Notes

- The application uses secure password hashing
- Session management is handled by Flask-Login
- CSRF protection is enabled by default
- SQL injection protection through SQLAlchemy

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 