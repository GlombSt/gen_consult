# Debugging Guide for FastAPI + React

## What Logging Was Added

Your FastAPI backend now has comprehensive logging that will help you debug issues:

### 1. Request/Response Logging
Every incoming request logs:
- 📨 HTTP method and path
- Client IP address
- All request headers (including Origin for CORS debugging)
- Response status code
- Processing time

### 2. Endpoint-Specific Logging
Each endpoint logs:
- What data is being received
- What actions are being performed
- Success/failure status
- Warnings for missing data

### 3. Error Logging
Any exceptions are logged with:
- Full error message
- Stack trace
- Processing time when error occurred

## How to View Logs

### Run with Detailed Logging
```bash
uvicorn main:app --reload --log-level debug
```

### What You'll See

When a request comes from React, you'll see output like:
```
2025-10-27 14:30:45 - fastapi_app - INFO - ============================================================
2025-10-27 14:30:45 - fastapi_app - INFO - 🚀 FastAPI Application Starting...
2025-10-27 14:30:45 - fastapi_app - INFO - 📝 Allowed CORS origins: ['http://localhost', 'http://localhost:3000', ...]
2025-10-27 14:30:45 - fastapi_app - INFO - ============================================================
2025-10-27 14:30:50 - fastapi_app - INFO - 📨 Incoming: GET /items
2025-10-27 14:30:50 - fastapi_app - INFO -    Client: 127.0.0.1
2025-10-27 14:30:50 - fastapi_app - INFO -    Headers: {'host': 'localhost:8000', 'origin': 'http://localhost:3000', ...}
2025-10-27 14:30:50 - fastapi_app - INFO - 📦 Fetching all items (total: 5)
2025-10-27 14:30:50 - fastapi_app - INFO - ✅ Response: 200 | Time: 0.003s
```

## Common Issues and Solutions

### Issue 1: CORS Error

**Symptoms:**
- Browser console shows: "Access to fetch at '...' has been blocked by CORS policy"
- Network tab shows request status as "(failed)"

**What to Check in Logs:**
```
📨 Incoming: OPTIONS /items    <-- Look for OPTIONS request (preflight)
   Headers: {'origin': 'http://localhost:3001', ...}
```

**Solution:**
1. Check if your React app's origin is in the allowed origins list
2. Add your React app's exact origin to the `origins` list in `main.py`:
```python
origins = [
    "http://localhost:3001",  # Add your exact port!
]
```

### Issue 2: 404 Not Found

**Symptoms:**
- Request returns 404
- React gets empty response or error

**What to Check in Logs:**
```
📨 Incoming: GET /api/items    <-- Check the path!
```

**Solution:**
Make sure your React fetch URL matches your FastAPI endpoint:
```javascript
// ❌ Wrong - FastAPI doesn't have /api prefix by default
fetch('http://localhost:8000/api/items')

// ✅ Correct
fetch('http://localhost:8000/items')
```

### Issue 3: Network Error / Connection Refused

**Symptoms:**
- React shows: "Failed to fetch" or "Network Error"
- No logs appear in FastAPI

**Solution:**
1. Make sure FastAPI is actually running: `uvicorn main:app --reload`
2. Check the port number matches (default is 8000)
3. Use `http://localhost:8000` not `http://127.0.0.1:8000` if your CORS config uses `localhost`

### Issue 4: Request Body Not Being Received

**Symptoms:**
- POST/PUT request fails with validation error
- Logs show empty or incorrect data

**What to Check in Logs:**
```
➕ Creating new item: {'id': None, 'name': '', 'price': 0, ...}  <-- Check received data
```

**Solution:**
Make sure your React request has correct headers:
```javascript
fetch('http://localhost:8000/items', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',  // ⚠️ Important!
  },
  body: JSON.stringify({
    name: 'Test Item',
    price: 99.99,
    is_available: true
  })
})
```

### Issue 5: CORS Preflight Request Failing

**Symptoms:**
- Browser sends OPTIONS request before actual request
- OPTIONS request fails
- Actual request never gets sent

**What to Check in Logs:**
```
📨 Incoming: OPTIONS /items
   Headers: {..., 'access-control-request-method': 'POST', ...}
✅ Response: 200 | Time: 0.001s    <-- Should be 200!
```

**Solution:**
Already fixed! The CORS middleware handles OPTIONS requests automatically.

## React Fetch Example

### Basic GET Request
```javascript
async function fetchItems() {
  try {
    const response = await fetch('http://localhost:8000/items');
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    console.log('Items:', data);
    return data;
  } catch (error) {
    console.error('Error fetching items:', error);
  }
}
```

### POST Request
```javascript
async function createItem(itemData) {
  try {
    const response = await fetch('http://localhost:8000/items', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(itemData)
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    console.log('Created item:', data);
    return data;
  } catch (error) {
    console.error('Error creating item:', error);
  }
}

// Usage
createItem({
  name: 'Laptop',
  description: 'Gaming laptop',
  price: 1299.99,
  is_available: true
});
```

### Using Axios (Alternative)
```javascript
import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  headers: {
    'Content-Type': 'application/json',
  }
});

// GET
const items = await api.get('/items');
console.log(items.data);

// POST
const newItem = await api.post('/items', {
  name: 'Laptop',
  price: 1299.99,
  is_available: true
});
console.log(newItem.data);
```

## Debugging Checklist

When your React app can't connect to FastAPI:

- [ ] Is FastAPI running? Check terminal for "Uvicorn running on..."
- [ ] Are you using the correct URL? (`http://localhost:8000`)
- [ ] Is your React app's origin in the CORS allowed list?
- [ ] Check FastAPI logs - do you see the incoming request?
- [ ] Check browser DevTools Network tab - what's the actual error?
- [ ] For POST/PUT - is `Content-Type: application/json` header set?
- [ ] Are you sending data in the correct format?
- [ ] Check browser console for CORS or network errors

## Browser DevTools Tips

### Network Tab
1. Open DevTools (F12)
2. Go to Network tab
3. Make request from React app
4. Click on the failed request
5. Check:
   - **Headers tab**: See request/response headers, check Origin
   - **Response tab**: See error message from server
   - **Console tab**: See CORS errors

### What to Look For
```
Request URL: http://localhost:8000/items
Request Method: GET
Status Code: 200 OK  (or 404, 500, etc.)

Response Headers:
  access-control-allow-origin: http://localhost:3000  <-- Should match your origin!
```

## Need More Help?

1. **Check the logs** - Run `uvicorn main:app --reload` and watch the terminal
2. **Test in browser** - Visit `http://localhost:8000/docs` and try the API directly
3. **Compare headers** - Test from Swagger UI vs your React app to see differences
4. **Check exact URLs** - Make sure paths match exactly (no typos, extra slashes, etc.)

## Testing Without React

You can test the API directly to rule out React issues:

### Using curl
```bash
# GET request
curl http://localhost:8000/items

# POST request
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name":"Test","price":99.99,"is_available":true}'
```

### Using the Swagger UI
1. Go to `http://localhost:8000/docs`
2. Click on an endpoint
3. Click "Try it out"
4. Fill in the data
5. Click "Execute"

If it works here but not in React, the problem is likely in your React code or CORS configuration.

