# PII and Privacy Protection Guide

## What is PII?

**PII (Personally Identifiable Information)** is any data that could potentially identify a specific individual. Logging PII can violate privacy regulations like GDPR, CCPA, HIPAA, and others.

### Common Types of PII

#### ❌ Never Log These
- **Email addresses** - `john.doe@example.com`
- **Phone numbers** - `555-123-4567`, `+1-555-123-4567`
- **Social Security Numbers** - `123-45-6789`
- **Credit card numbers** - `4532-1234-5678-9010`
- **Passwords** - Any form of passwords or authentication credentials
- **API keys / tokens** - Authentication tokens, API keys, secrets
- **Physical addresses** - Street addresses, postal codes with names
- **Driver's license numbers**
- **Passport numbers**
- **Biometric data** - Fingerprints, facial recognition data
- **Health information** - Medical records, diagnoses
- **Financial data** - Bank account numbers, transaction details
- **National ID numbers** - Any government-issued ID numbers

#### ⚠️ Log With Caution
- **IP addresses** - Can be considered PII in some jurisdictions (EU)
- **Usernames** - Depends on your privacy policy
- **User IDs** - Usually OK if they're non-reversible identifiers
- **Device identifiers** - MAC addresses, device UUIDs
- **Geolocation data** - Precise location can be sensitive

#### ✅ Generally Safe to Log
- **Aggregate metrics** - "500 users logged in today"
- **Non-identifying IDs** - Random UUIDs, auto-incremented IDs
- **Hashed identifiers** - SHA-256 hash of email for correlation
- **HTTP methods and paths** - GET, POST, /api/items
- **Response codes** - 200, 404, 500
- **Timing data** - Request duration, timestamps
- **Error types** - Exception class names
- **Feature flags** - Which features are enabled

## How Our Application Protects PII

### 1. Automatic PII Sanitization

The `PIISanitizer` class automatically redacts PII from all logs:

```python
# Before sanitization
"User email: john.doe@example.com called us at 555-123-4567"

# After sanitization
"User email: [EMAIL_REDACTED] called us at [PHONE_REDACTED]"
```

### 2. Pattern Matching

Automatically detects and redacts:
- Email addresses (regex pattern matching)
- Phone numbers (various formats)
- Social Security Numbers
- Credit card numbers
- IP addresses (optional)

### 3. Field-Based Redaction

Automatically redacts fields with sensitive names:

```python
# Input
{
    "username": "johndoe",
    "email": "john@example.com",
    "password": "secret123",
    "api_key": "abc123def456"
}

# Logged as
{
    "username": "johndoe",
    "email": "[EMAIL_REDACTED]",
    "password": "[REDACTED]",
    "api_key": "[REDACTED]"
}
```

### 4. Hash-Based Correlation

For cases where you need to correlate logs without exposing PII:

```python
email = "john.doe@example.com"
email_hash = PIISanitizer.hash_identifier(email)  # "a1b2c3d4e5f6g7h8"

# Log the hash instead
logger.info("User action", extra={'email_hash': email_hash})
```

This allows you to:
- Track the same user across multiple logs
- Correlate user actions
- Debug user-specific issues
- Without ever logging the actual email

## Examples: Before and After

### Example 1: User Registration

#### ❌ Bad (Logs PII)
```python
@app.post("/users")
async def create_user(user: User):
    logger.info(f"Creating user: {user.email}")  # ❌ Logs email directly
    logger.info(f"User data: {user.dict()}")      # ❌ Logs all fields
    return user
```

**Log output:**
```json
{
  "message": "Creating user: john.doe@example.com",
  "user_data": {"email": "john.doe@example.com", "phone": "555-1234"}
}
```

#### ✅ Good (PII-Safe)
```python
@app.post("/users")
async def create_user(user: User):
    email_hash = PIISanitizer.hash_identifier(user.email)
    logger.info(
        "User created",
        extra={
            'user_id': user.id,
            'email_hash': email_hash  # Hashed for correlation
        }
    )
    return user
```

**Log output:**
```json
{
  "message": "User created",
  "user_id": 123,
  "email_hash": "a1b2c3d4e5f6g7h8"
}
```

### Example 2: Login Attempt

#### ❌ Bad
```python
logger.info(f"Login attempt from {email} at {ip_address}")
```

#### ✅ Good
```python
email_hash = PIISanitizer.hash_identifier(email)
logger.info("Login attempt", extra={'email_hash': email_hash})
```

### Example 3: Error Messages

#### ❌ Bad
```python
logger.error(f"Failed to send email to {user.email}: {error}")
```

#### ✅ Good
```python
user_id = user.id
logger.error(
    "Failed to send email",
    extra={'user_id': user_id, 'error_type': type(error).__name__}
)
```

### Example 4: Request Logging

#### ❌ Bad
```python
# Logging raw headers (may contain auth tokens)
logger.info(f"Headers: {dict(request.headers)}")
```

#### ✅ Good (Our Implementation)
```python
# Automatically sanitizes sensitive headers
# Authorization, Cookie, API-Key headers are redacted
logger.info("Incoming request", extra={
    'method': request.method,
    'path': request.url.path,
    'user_agent': request.headers.get('user-agent')
    # Sensitive headers are automatically filtered out
})
```

## Configuration

### Customizing PII Protection

You can customize what gets redacted:

```python
# In PIISanitizer class, add more patterns:
SENSITIVE_FIELDS = {
    'password', 'passwd', 'pwd', 'secret', 'token',
    'date_of_birth', 'dob',  # Add custom fields
    'government_id',
    # Add any fields that contain PII in your domain
}

# Add custom regex patterns
CUSTOM_PATTERN = re.compile(r'your-pattern-here')
```

### Environment-Based Configuration

```python
# For development: log more details (be careful!)
if os.getenv('ENVIRONMENT') == 'development':
    # Maybe show partial emails in dev only
    pass

# For production: strict PII protection
if os.getenv('ENVIRONMENT') == 'production':
    # Always redact everything
    # Consider hashing IP addresses too
    pass
```

## Best Practices

### ✅ DO

1. **Use hashed identifiers for correlation**
   ```python
   email_hash = PIISanitizer.hash_identifier(user.email)
   logger.info("Action", extra={'email_hash': email_hash})
   ```

2. **Log aggregate data instead of individual records**
   ```python
   logger.info("Bulk operation", extra={'users_affected': len(users)})
   ```

3. **Use user IDs instead of emails**
   ```python
   logger.info("User action", extra={'user_id': user.id})
   ```

4. **Redact query parameters that might contain PII**
   ```python
   # /search?email=john@example.com → automatically sanitized
   ```

5. **Review logs before production**
   - Run a sample and check for any PII leaks
   - Test with realistic data

6. **Document what you log and why**
   - Maintain a log inventory
   - Include in privacy policy if required

7. **Set log retention policies**
   - Don't keep logs forever
   - Rotate and delete old logs

### ❌ DON'T

1. **Don't log raw request bodies with user data**
   ```python
   # ❌ Bad
   logger.info(f"Request: {request.body}")
   ```

2. **Don't log error messages that contain PII**
   ```python
   # ❌ Bad
   try:
       send_email(user.email)
   except Exception as e:
       logger.error(f"Error: {e}")  # Exception might contain email
   ```

3. **Don't log database query results directly**
   ```python
   # ❌ Bad
   users = db.query(User).all()
   logger.info(f"Users: {users}")  # Contains all PII
   ```

4. **Don't disable PII protection "temporarily"**
   - It never gets re-enabled
   - Creates compliance risks

5. **Don't log authentication headers**
   - Already handled by PIISanitizer
   - But be careful with custom headers

6. **Don't log third-party API responses without checking**
   - They might contain PII
   - Sanitize or log only status codes

## Compliance Considerations

### GDPR (EU)
- Right to be forgotten: Don't log PII you can't delete
- Data minimization: Only log what's necessary
- Purpose limitation: Only log for specific purposes
- IP addresses are considered PII

### CCPA (California)
- Similar to GDPR
- Consumers have right to know what data you collect
- Right to deletion

### HIPAA (Healthcare - US)
- Extra strict: no health information in logs
- Audit trails must be maintained separately
- Encryption requirements

### PCI DSS (Payment Cards)
- Never log credit card numbers
- Never log CVV/CVC codes
- Never log PINs
- Never log full magnetic stripe data

## Testing PII Protection

### Manual Testing

```python
# Test email redaction
test_string = "Contact john.doe@example.com for info"
result = PIISanitizer.sanitize_string(test_string)
assert "[EMAIL_REDACTED]" in result
assert "john.doe@example.com" not in result

# Test phone redaction
test_string = "Call us at 555-123-4567"
result = PIISanitizer.sanitize_string(test_string)
assert "[PHONE_REDACTED]" in result
assert "555-123-4567" not in result

# Test field redaction
test_dict = {"username": "john", "password": "secret"}
result = PIISanitizer.sanitize_dict(test_dict)
assert result["password"] == "[REDACTED]"
assert result["username"] == "john"
```

### Automated Testing

Create unit tests to ensure PII protection:

```python
def test_pii_sanitization():
    """Test that PII is redacted from logs"""
    # Capture logs
    with LogCapture() as logs:
        user = User(email="test@example.com", password="secret123")
        create_user(user)
    
    # Check that logs don't contain PII
    all_logs = str(logs)
    assert "test@example.com" not in all_logs
    assert "secret123" not in all_logs
    assert "[EMAIL_REDACTED]" in all_logs or "email_hash" in all_logs
```

## Incident Response

### If PII is Accidentally Logged

1. **Stop the logging immediately**
   - Deploy a fix ASAP

2. **Identify what was logged**
   - Audit affected log files
   - Determine timeframe

3. **Delete the PII from logs**
   - CloudWatch: Delete log streams
   - Files: Scrub the data
   - Backups: Consider rotation

4. **Assess impact**
   - Who had access?
   - Was it exported anywhere?

5. **Notify if required**
   - GDPR: 72 hours to notify authority
   - CCPA: Notify affected consumers
   - Check your local regulations

6. **Document and learn**
   - What went wrong?
   - How to prevent it?
   - Update training/processes

## Real-World Examples

### Example: Debugging User-Specific Issue

**Scenario:** User reports they can't log in.

#### ❌ Bad Approach
```python
# User reports issue with email: john.doe@example.com
logger.info("Debugging login for john.doe@example.com")
# Now email is in logs forever
```

#### ✅ Good Approach
```python
# Get the email from support ticket
email = "john.doe@example.com"
email_hash = PIISanitizer.hash_identifier(email)

# Debug using the hash
logger.info(f"Debugging login issue", extra={'email_hash': email_hash})

# Share hash with dev team
# They can search logs for email_hash without seeing the actual email
```

### Example: Fraud Detection

**Scenario:** Detecting suspicious activity patterns.

#### ✅ Good Approach
```python
# Instead of logging individual users
logger.info(
    "Suspicious activity detected",
    extra={
        'user_id': user.id,  # Use ID, not email
        'action_count': 150,
        'time_window_minutes': 5,
        'user_hash': PIISanitizer.hash_identifier(user.email)
    }
)
```

### Example: A/B Testing

**Scenario:** Tracking feature usage.

#### ✅ Good Approach
```python
# Log aggregate metrics
logger.info(
    "Feature usage",
    extra={
        'feature': 'new_checkout',
        'variant': 'B',
        'success': True,
        'user_id': user.id  # ID, not email
    }
)
```

## Summary

### Key Takeaways

1. ✅ **Always assume logs might be seen by others**
2. ✅ **Use hashing for correlation without exposing PII**
3. ✅ **Sanitization is automatic, but stay vigilant**
4. ✅ **When in doubt, don't log it**
5. ✅ **Test your logging code for PII leaks**
6. ✅ **Keep logs only as long as needed**
7. ✅ **Document your logging practices**

### Quick Reference

| Data Type | Action | Method |
|-----------|--------|--------|
| Email | Hash | `PIISanitizer.hash_identifier(email)` |
| Password | Never log | - |
| User ID | Log directly | ✅ OK |
| Phone | Redacted automatically | Automatic |
| IP Address | Log with caution | Depends on jurisdiction |
| Username | Depends on policy | Check your privacy policy |
| Credit Card | Never log | - |
| API Key | Never log | Auto-redacted |

### Your Application's Protection

✅ Automatic pattern-based redaction  
✅ Field-name-based redaction  
✅ Sensitive header filtering  
✅ Hash-based correlation support  
✅ Exception message sanitization  
✅ Zero external dependencies  

**Stay compliant, protect your users, and log responsibly!** 🔒

