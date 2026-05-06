# FYP System - Recommended Architecture

## Current Architecture (Monolithic) ❌

```
┌─────────────────────────────────────────┐
│  Frontend (Bootstrap + Jinja2)         │
│  - 34 templates                         │
│  - CSS/JS                               │
└──────────────┬──────────────────────────┘
               │ HTTP/WebSocket
┌──────────────▼──────────────────────────┐
│  app.py (5200+ LINES) ❌               │
│  - All routes (50+)                     │
│  - All business logic                   │
│  - WebSocket handlers                   │
│  - Database access scattered            │
│  - Error handling missing               │
│  - Impossible to test individually      │
└──────────────┬──────────────────────────┘
               │
┌──────────────▼──────────────────────────┐
│  Database (SQLAlchemy)                 │
│  - 19 models                            │
│  - PostgreSQL (prod) / SQLite (dev)     │
└─────────────────────────────────────────┘

Problems:
- Hard to test
- Code duplication (HTTP + WebSocket)
- Slow to onboard developers
- Hard to scale
- Difficult to maintain
```

---

## Recommended Architecture (Modular) ✅

```
┌─────────────────────────────────────────┐
│  Frontend (Bootstrap + Jinja2)         │
│  - 34 templates                         │
│  - CSS/JS                               │
│  - WebSocket client                     │
└──────────────┬──────────────────────────┘
               │ HTTP/WebSocket
    ┌──────────┴────────────┐
    │                       │
┌───▼────────┐    ┌────────▼────┐
│  REST API  │    │  WebSocket  │
│  Endpoints │    │  Handlers   │
└───┬────────┘    └────────┬────┘
    │                      │
    └──────────┬───────────┘
               │
┌──────────────▼──────────────────────────┐
│  app.py - Factory (100 lines only) ✅   │
│  ├─ Initialize extensions               │
│  ├─ Register blueprints                 │
│  └─ Setup middleware                    │
└──────────────┬──────────────────────────┘
               │
    ┌──────────┼──────────┐
    │          │          │
┌───▼──┐  ┌────▼────┐  ┌─▼──────┐
│ Auth │  │Dashboard│  │Projects│
│ BP   │  │   BP    │  │   BP   │
└──┬───┘  └────┬────┘  └─┬──────┘
   │           │         │
   │  ┌────────┴────┬────┤
   │  │             │    │
   ▼  ▼             ▼    ▼
┌─────────────────────────────────┐
│  Service Layer (Business Logic) │
│  ├─ UserService                 │
│  ├─ ProjectService              │
│  ├─ DashboardService            │
│  ├─ EmailService                │
│  ├─ ExportService               │
│  └─ NotificationService         │
└────────┬────────────────────────┘
         │
┌────────▼─────────────────────────┐
│  Database Layer                  │
│  ├─ Models (models.py)           │
│  ├─ Repositories (optional)      │
│  └─ SQLAlchemy ORM               │
└────────┬─────────────────────────┘
         │
┌────────▼─────────────────────────┐
│  Database (PostgreSQL/SQLite)    │
└──────────────────────────────────┘

Benefits:
✓ Each blueprint independently testable
✓ Code reuse via service layer
✓ Easy to extend
✓ Clear separation of concerns
✓ Easy to onboard new developers
✓ Can scale/parallelize work
```

---

## File Structure (Production-Ready)

```
fyp-system/
│
├── backend/
│   ├── app.py                       # App factory (100 lines)
│   ├── config.py                    # Configuration classes
│   ├── extensions.py                # Initialize Flask extensions
│   ├── middleware.py                # Error handlers, middleware
│   ├── models.py                    # All database models
│   │
│   ├── blueprints/
│   │   ├── __init__.py
│   │   ├── auth.py                  # Login, signup, OAuth
│   │   ├── dashboard.py             # Dashboard routes
│   │   ├── projects.py              # Project management
│   │   ├── submissions.py           # Work submission
│   │   ├── scheduling.py            # Viva scheduling
│   │   ├── admin.py                 # Admin features
│   │   └── api.py                   # RESTful API
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py          # User operations
│   │   ├── project_service.py       # Project operations
│   │   ├── dashboard_service.py     # Dashboard logic
│   │   ├── email_service.py         # Email handling
│   │   ├── export_service.py        # Data export
│   │   └── notification_service.py  # Notifications
│   │
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── validators.py            # Input validation
│   │   ├── decorators.py            # Custom decorators
│   │   ├── constants.py             # String constants
│   │   └── helpers.py               # Utility functions
│   │
│   ├── websockets/
│   │   ├── __init__.py
│   │   ├── handlers.py              # WebSocket event handlers
│   │   └── manager.py               # WebSocket manager
│   │
│   ├── static/                      # Shared with frontend
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   │
│   ├── templates/                   # Shared with frontend
│   │
│   ├── instance/
│   │   ├── fyp.db
│   │   └── sessions/
│   │
│   ├── logs/
│   │
│   ├── uploads/
│   │
│   └── scripts/
│       ├── migrate.py
│       └── seed.py
│
├── frontend/
│   ├── static/
│   │   ├── css/
│   │   │   ├── style.css
│   │   │   └── responsive.css
│   │   └── js/
│   │       ├── main.js
│   │       ├── websocket-client.js
│   │       └── utils.js
│   └── templates/
│       └── [35 HTML files]
│
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_projects.py
│   ├── test_api.py
│   └── test_websocket.py
│
├── docker/
│   ├── Dockerfile
│   └── docker-compose.yml
│
├── docs/
│   ├── API.md
│   ├── ARCHITECTURE.md
│   └── DEPLOYMENT.md
│
├── .env.example
├── requirements.txt
├── setup.py
└── README.md
```

---

## Data Flow Diagrams

### User Login Flow
```
User enters credentials
        ↓
┌───────────────────────────────┐
│  routes/auth.py               │
│  - Validate input             │
│  - Check rate limit           │
│  - Get user from DB           │
└───────────────┬───────────────┘
                ↓
┌───────────────────────────────┐
│  services/user_service.py     │
│  - Verify password            │
│  - Create session             │
│  - Log audit event            │
└───────────────┬───────────────┘
                ↓
        ✓ Success
                ↓
    Redirect to dashboard
```

### Dashboard Update (HTTP + WebSocket)
```
┌─────────────────────────────────────────┐
│  Frontend - Dashboard Component         │
│  1. HTTP Request to /api/dashboard-data │
│  2. WebSocket subscribe to updates      │
└────────┬────────────────────────────────┘
         │
    ┌────┴────┬──────────────────┐
    │         │                  │
┌───▼──┐  ┌───▼──────┐  ┌───────▼────┐
│ HTTP │  │ WebSocket│  │ Every 5s   │
│Route │  │ Handler  │  │ Poll Check │
└───┬──┘  └───┬──────┘  └───────┬────┘
    │         │                 │
    └────┬────┴────────┬────────┘
         │             │
    ┌────▼──────────────▼──────────┐
    │ DashboardService             │
    │ - get_student_dashboard()    │
    │ - Eager load all relations   │
    │ - Single database query      │
    └────┬───────────────────────┬─┘
         │                       │
         │ Cache for 60s         │
         ▼                       ▼
    [Response to HTTP]      [WebSocket emit]
    JSON with data          Updated UI
```

### File Upload Security
```
User selects file
    ↓
┌─────────────────────────┐
│ Browser Upload          │
│ - Check file size       │
└─────────┬───────────────┘
          ↓
┌─────────────────────────┐
│ Server Validation       │
│ 1. Secure filename      │
│ 2. Extension check      │
│ 3. MIME type check      │
│ 4. File magic bytes     │
│ 5. Virus scan (opt)     │
└─────────┬───────────────┘
          ↓
    ✓ Valid
          ↓
┌─────────────────────────┐
│ Save File               │
│ - Random prefix         │
│ - No execution perms    │
│ - Separate upload dir   │
└─────────┬───────────────┘
          ↓
    Serve with proper
    MIME type (no execute)
```

---

## Deployment Architecture

### Production Deployment (Recommended)
```
┌──────────────────────────────────────────────────────────┐
│  HTTPS & CDN (Cloudflare/Nginx)                         │
├──────────────────────────────────────────────────────────┤
│  Nginx Reverse Proxy (Load Balancer)                    │
│  - SSL termination                                      │
│  - Static file serving                                  │
│  - Compression                                          │
│  - Rate limiting                                        │
├──────────────────────────────────────────────────────────┤
│  Application Tier (Multiple Instances)                  │
│  - Gunicorn worker 1 (4 workers each)                   │
│  - Gunicorn worker 2                                    │
│  - Gunicorn worker 3 (for scaling)                      │
├──────────────────────────────────────────────────────────┤
│  Cache Layer                                            │
│  - Redis (in-memory cache)                              │
│  - Session store                                        │
├──────────────────────────────────────────────────────────┤
│  Database Tier                                          │
│  - PostgreSQL 15+ (Primary)                             │
│  - Read replica (optional)                              │
│  - Backup (daily)                                       │
├──────────────────────────────────────────────────────────┤
│  Background Jobs (Optional)                             │
│  - Celery + Redis                                       │
│  - Email sending                                        │
│  - Report generation                                    │
└──────────────────────────────────────────────────────────┘
```

---

## Technology Stack Recommendations

### Backend Stack
```
Language:       Python 3.11
Framework:      Flask 3.0.2
ORM:            SQLAlchemy 2.0.28
Database:       PostgreSQL 15+ (production)
                SQLite (development)
Cache:          Redis (production)
                Simple cache (development)
Task Queue:     Celery + Redis (optional)
Web Server:     Gunicorn 21.2.0
Reverse Proxy:  Nginx
Containerization: Docker
```

### Frontend Stack
```
Template:       Jinja2 (Flask)
CSS:            Bootstrap 5 + Custom CSS
JavaScript:     Vanilla JS + Socket.IO
Real-time:      Socket.IO (WebSocket)
Fallback:       HTTP polling
Charts:         Chart.js (for analytics)
Notifications:  Toast notifications
Forms:          HTML5 + Bootstrap forms
Icons:          Bootstrap Icons / FontAwesome
```

### Development Stack
```
Testing:        Pytest + coverage
Code Quality:   Pylint / Flake8
Type Checking:  mypy (optional)
Linting:        black (formatter)
API Testing:    Postman / Insomnia
Load Testing:   Apache JMeter / Locust
Monitoring:     Prometheus + Grafana (optional)
Logging:        Python logging + ELK (optional)
```

---

## Performance Targets (Post-Optimization)

```
Metric                      Target      Current     Improvement
─────────────────────────────────────────────────────────────
Dashboard Load              <1 second   15-30s      15-30x
Export Data                 <3 seconds  Crashes     ∞
Data Verification           <200ms      60s+        300x+
List 100 Records            <100ms      3-5s        30-50x
User Login                  <500ms      1-2s        2-4x
API Response                <200ms      500-1000ms  2.5-5x
WebSocket Message           <100ms      500-1000ms  5-10x
Database Queries/Request    <8          50-150      6-19x
Concurrent Users Support    1000+       <100        10x+
Database Connection Time    <50ms       500-1000ms  10-20x
```

---

## Migration Strategy (Current → Recommended)

```
Week 1: Preparation
├─ Create new directory structure
├─ Initialize blueprints
├─ Setup services
└─ Refactor models.py

Week 2: Blueprint Migration
├─ Move auth routes to auth.py
├─ Move dashboard routes to dashboard.py
├─ Move project routes to projects.py
├─ Create service layer
└─ Update imports throughout

Week 3: Optimization
├─ Add eager loading
├─ Implement caching
├─ Add pagination
├─ Create repository pattern (optional)
└─ Add comprehensive logging

Week 4: Testing & Deployment
├─ Write tests for services
├─ Write tests for blueprints
├─ Integration tests
├─ Load testing
└─ Production deployment

Result: Professional, scalable system
```

---

**This architecture follows:**
- ✅ Flask best practices
- ✅ Separation of concerns
- ✅ DRY principle
- ✅ SOLID principles
- ✅ Industry standards
- ✅ Scalability patterns
