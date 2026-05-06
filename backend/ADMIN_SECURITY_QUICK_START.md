# QUICK START: Admin Security Integration

## TL;DR - 5 Integration Steps

### Step 1: Database Table
```python
# In Python shell or migration
from app import app, db
with app.app_context():
    db.create_all()  # Creates AuditLog table
```

### Step 2: Register Blueprint (in backend/app.py)
```python
from .admin_routes_secure import admin_blueprint

app = Flask(__name__)
# ... existing setup ...

# ADD THIS:
app.register_blueprint(admin_blueprint, url_prefix='/admin')
```

### Step 3: Add Imports (in backend/app.py)
```python
from .admin_security import require_admin, require_admin_reauth, log_admin_action
from .admin_validation_schemas import CREATE_USER_SCHEMA, CHANGE_ROLE_SCHEMA
```

### Step 4: Protect Existing Routes (optional, in backend/app.py)
```python
# BEFORE:
@app.route('/admin/delete_user/<user_id>', methods=['POST'])
def delete_user(user_id):
    ...

# AFTER:
@app.route('/admin/delete_user/<user_id>', methods=['POST'])
@require_admin
@require_admin_reauth
def delete_user(user_id):
    ...
    log_admin_action('DELETE_USER', 'user', user_id, 'SUCCESS', f'Deleted: {user.email}')
    ...
```

### Step 5: Test
```bash
cd backend
pytest test_admin_security.py -v
```

---

## Key Decorators

```python
@require_auth                # 401 if not authenticated
@require_admin              # 401 if not auth, 403 if not admin
@require_admin_reauth       # 403 if re-auth not done/expired
```

## Key Functions

```python
validate_user_input(data, SCHEMA)           # Validates & returns sanitized data
check_resource_access(type, id, user_id)    # Returns bool
validate_no_privilege_escalation(uid, role) # Returns bool
log_admin_action(action, type, id, status, details)  # Logs to DB
detect_security_anomalies(admin_id, hours)  # Returns list of alerts
```

## Endpoint Template

```python
@app.route('/admin/resource/<int:resource_id>', methods=['PATCH'])
@require_admin
@require_admin_reauth  # For sensitive ops
def update_resource(resource_id):
    try:
        # 1. Validate input
        data = request.get_json() or {}
        validated = validate_user_input(data, SCHEMA)
        
        # 2. Resource check
        resource = db.session.get(Resource, resource_id)
        if not resource:
            return error_response('Not found', 404)
        
        # 3. Update
        resource.field = validated['field']
        db.session.commit()
        
        # 4. Log success
        log_admin_action('UPDATE_RESOURCE', 'resource', resource_id, 'SUCCESS')
        
        return success_response('Updated', code=200)
    
    except ValidationError as e:
        return error_response(str(e), 400)
    except Exception as e:
        logger.error(f"Error: {e}")
        log_admin_action('UPDATE_RESOURCE', 'resource', resource_id, 'FAILED', str(e))
        return error_response('Failed', 500)
```

---

## Response Format

### Success
```json
{
  "success": true,
  "message": "User created",
  "code": 201,
  "data": { "user_id": 123, "email": "user@test.com" }
}
```

### Error
```json
{
  "success": false,
  "error": "Validation error: Invalid email format",
  "code": 400
}
```

---

## Testing Commands

```bash
# Full suite
pytest test_admin_security.py -v

# Specific class
pytest test_admin_security.py::TestAdminSecurityMiddleware -v

# Specific test
pytest test_admin_security.py::TestAdminSecurityMiddleware::test_unauthenticated_access_to_admin_route_returns_401 -v

# With coverage
pytest test_admin_security.py -v --cov=admin_security
```

---

## Manual Testing via curl

```bash
# 1. Test unauthorized (no auth)
curl http://localhost:5000/admin/users
# → 401

# 2. Test admin access
# Login first, then:
curl -H "Authorization: Bearer TOKEN" http://localhost:5000/admin/users
# → 200

# 3. Test validation
curl -X POST http://localhost:5000/admin/users \
  -H "Content-Type: application/json" \
  -d '{"email":"invalid","first_name":"Test","last_name":"User","role":"student","password":"weak"}'
# → 400 with validation error

# 4. View audit logs
curl http://localhost:5000/admin/audit-logs?page=1
# → 200 with audit log entries
```

---

## Files Reference

| File | Purpose | Lines |
|------|---------|-------|
| admin_security.py | Core security middleware | 480+ |
| admin_validation_schemas.py | Validation schemas | 150+ |
| admin_routes_secure.py | Example endpoints | 550+ |
| test_admin_security.py | Test suite | 400+ |
| ADMIN_SECURITY_IMPLEMENTATION_GUIDE.py | Full documentation | 500+ |
| app.py (AuditLog model) | Persistent audit logging | 50+ |

---

## Security Checklist

Before deploying:
- [ ] All /admin/* routes have @require_admin
- [ ] Sensitive ops have @require_admin_reauth  
- [ ] Input validation on all endpoints
- [ ] log_admin_action() called on all ops
- [ ] Error responses don't leak info
- [ ] Tests pass
- [ ] AuditLog table created
- [ ] Blueprint registered
- [ ] Existing routes migrated (if needed)

---

## Common Issues & Fixes

**401 when accessing as admin:**
- Verify user.role = 'admin' in DB
- Check @require_admin decorator applied
- Verify current_user.is_authenticated

**403 when creating/deleting:**
- Did you call /admin/reauth first?
- Check @require_admin_reauth applied
- Verify re-auth hasn't expired (30 min)

**Validation not working:**
- Verify validate_user_input() called with schema
- Check schema field names match request
- Ensure ValidationError caught

**Audit logs empty:**
- Verify AuditLog table exists
- Check log_admin_action() being called
- Verify db.session.commit() called

---

For full documentation, see: `ADMIN_SECURITY_IMPLEMENTATION_GUIDE.py`
