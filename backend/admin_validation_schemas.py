"""
INPUT VALIDATION SCHEMAS FOR ADMIN OPERATIONS
Defines request validation rules for all admin endpoints.
"""

# Schema format: field_name -> { type, required, min_length, max_length, pattern, allowed, etc. }

# ─────────────────────────────────────────────────────────────
# USER MANAGEMENT SCHEMAS
# ─────────────────────────────────────────────────────────────

CREATE_USER_SCHEMA = {
    'email': {
        'type': 'email',
        'required': True,
        'min_length': 5,
        'max_length': 120,
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    },
    'first_name': {
        'type': 'string',
        'required': True,
        'min_length': 2,
        'max_length': 50,
        'pattern': r'^[a-zA-Z\s\-\.]*$'  # Letters, spaces, hyphens, dots only
    },
    'last_name': {
        'type': 'string',
        'required': True,
        'min_length': 2,
        'max_length': 50,
        'pattern': r'^[a-zA-Z\s\-\.]*$'
    },
    'role': {
        'type': 'string',
        'required': True,
        'allowed': ['student', 'supervisor', 'cordinator', 'teacher', 'evaluator', 'admin']
    },
    'password': {
        'type': 'string',
        'required': True,
        'min_length': 8,
        'max_length': 128,
        'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'  # Strong password
    },
    'program': {
        'type': 'string',
        'required': False,
        'max_length': 50,
        'allowed': ['CS', 'IT', 'AI', 'SE', 'CE']
    },
    'semester': {
        'type': 'string',
        'required': False,
        'max_length': 20,
        'allowed': ['Spring', 'Fall', 'Summer', '1', '2', '3', '4', '5', '6', '7', '8']
    },
    '_strict': True
}


UPDATE_USER_SCHEMA = {
    'email': {
        'type': 'email',
        'required': False,
        'min_length': 5,
        'max_length': 120,
        'pattern': r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    },
    'first_name': {
        'type': 'string',
        'required': False,
        'min_length': 2,
        'max_length': 50,
        'pattern': r'^[a-zA-Z\s\-\.]*$'
    },
    'last_name': {
        'type': 'string',
        'required': False,
        'min_length': 2,
        'max_length': 50,
        'pattern': r'^[a-zA-Z\s\-\.]*$'
    },
    '_strict': True
}


CHANGE_ROLE_SCHEMA = {
    'user_id': {
        'type': 'int',
        'required': True,
        'min': 1
    },
    'new_role': {
        'type': 'string',
        'required': True,
        'allowed': ['student', 'supervisor', 'cordinator', 'teacher', 'evaluator']
        # Note: 'admin' not allowed here - use separate endpoint with stronger checks
    },
    '_strict': True
}


RESET_USER_PASSWORD_SCHEMA = {
    'user_id': {
        'type': 'int',
        'required': True,
        'min': 1
    },
    'new_password': {
        'type': 'string',
        'required': True,
        'min_length': 8,
        'max_length': 128,
        'pattern': r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$'
    },
    '_strict': True
}


# ─────────────────────────────────────────────────────────────
# PROJECT MANAGEMENT SCHEMAS
# ─────────────────────────────────────────────────────────────

CREATE_PROJECT_SCHEMA = {
    'title': {
        'type': 'string',
        'required': True,
        'min_length': 5,
        'max_length': 200
    },
    'description': {
        'type': 'string',
        'required': True,
        'min_length': 20,
        'max_length': 2000
    },
    'major': {
        'type': 'string',
        'required': True,
        'allowed': ['AI/ML', 'Cyber Security', 'Blockchain', 'Web Development', 'Mobile Development', 'Data Science', 'Cloud Computing', 'Other']
    },
    'supervisor_id': {
        'type': 'int',
        'required': False,
        'min': 1
    },
    '_strict': True
}


UPDATE_PROJECT_SCHEMA = {
    'title': {
        'type': 'string',
        'required': False,
        'min_length': 5,
        'max_length': 200
    },
    'description': {
        'type': 'string',
        'required': False,
        'min_length': 20,
        'max_length': 2000
    },
    'status': {
        'type': 'string',
        'required': False,
        'allowed': ['Pending', 'Approved', 'Rejected', 'In Progress', 'Completed']
    },
    '_strict': True
}


# ─────────────────────────────────────────────────────────────
# GROUP MANAGEMENT SCHEMAS
# ─────────────────────────────────────────────────────────────

ASSIGN_SUPERVISOR_SCHEMA = {
    'group_id': {
        'type': 'int',
        'required': True,
        'min': 1
    },
    'supervisor_id': {
        'type': 'int',
        'required': True,
        'min': 1
    },
    '_strict': True
}


ADD_GROUP_MEMBER_SCHEMA = {
    'group_id': {
        'type': 'int',
        'required': True,
        'min': 1
    },
    'student_id': {
        'type': 'int',
        'required': True,
        'min': 1
    },
    '_strict': True
}


# ─────────────────────────────────────────────────────────────
# AUDIT & ADMIN SCHEMAS
# ─────────────────────────────────────────────────────────────

ADMIN_REAUTH_SCHEMA = {
    'password': {
        'type': 'string',
        'required': True,
        'min_length': 1,
        'max_length': 256
    },
    '_strict': True
}


BULK_DELETE_SCHEMA = {
    'user_ids': {
        'type': 'list',
        'required': True,
        'min_length': 1,
        'max_length': 100
    },
    '_strict': True
}


EXPORT_AUDIT_LOG_SCHEMA = {
    'format': {
        'type': 'string',
        'required': False,
        'allowed': ['json', 'csv'],
        'default': 'json'
    },
    'filters': {
        'type': 'dict',
        'required': False,
        'allowed_keys': ['action', 'status', 'start_date', 'end_date']
    },
    '_strict': True
}
