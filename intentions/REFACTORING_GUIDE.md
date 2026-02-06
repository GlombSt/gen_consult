# Refactoring Guide: Modular Structure

## What Changed?

Your FastAPI application has been refactored from a single `main.py` file into a clean, modular structure that follows best practices for production applications.

## New Project Structure

```
intentions/
├── app/
│   ├── __init__.py              # Package initialization
│   ├── main.py                  # Application factory & configuration
│   ├── logging_config.py        # Structured logging setup
│   ├── models.py                # Pydantic models (Item, User)
│   ├── middleware.py            # Request logging middleware
│   ├── exception_handlers.py   # Custom exception handlers
│   └── routers/
│       ├── __init__.py
│       ├── items.py             # Item CRUD endpoints
│       └── users.py             # User CRUD endpoints
├── main.py                      # Backwards-compatible entry point
├── docker-compose.yml
├── pyproject.toml              # Project metadata and dependencies
└── README.md
```

## How to Run

### Option 1: Backwards Compatible (Recommended for Development)
Your existing command still works:
```bash
uvicorn main:app --reload --port 8000
```

### Option 2: Using New Module Path
```bash
uvicorn app.main:app --reload --port 8000
```

### Option 3: Docker
```bash
docker-compose up
```

## Key Benefits

### 1. **Separation of Concerns**
- Each module has a single, clear responsibility
- Logging configuration is isolated and reusable
- Routes are organized by resource type

### 2. **Maintainability**
- Easier to find and update specific functionality
- Changes to logging don't affect route handlers
- Can modify middleware without touching business logic

### 3. **Scalability**
- Easy to add new routers (e.g., `routers/products.py`)
- Can split large routers into sub-routers
- Simple to add new middleware or exception handlers

### 4. **Testability**
- Each module can be tested independently
- Mock dependencies easily
- Unit tests are more focused and faster

### 5. **Reusability**
- Logging config can be imported into other projects
- Models can be shared between services
- Middleware can be reused across applications

## Module Responsibilities

### `app/main.py`
- Creates and configures the FastAPI application
- Registers middleware and exception handlers
- Includes routers
- Defines application-level endpoints (/, /health)
- Startup/shutdown event handlers

### `app/logging_config.py`
- `StructuredFormatter`: JSON formatter for logs
- `setup_logger()`: Logger configuration function
- `logger`: Pre-configured global logger instance

### `app/models.py`
- Pydantic models for request/response validation
- `Item`: Inventory item model
- `User`: User account model

### `app/middleware.py`
- `log_requests_middleware()`: Logs all HTTP requests/responses
- Tracks request duration
- Logs errors with full context

### `app/exception_handlers.py`
- `validation_exception_handler()`: Handles 422 validation errors
- Logs detailed validation error information
- Returns proper error responses

### `app/routers/items.py`
- All item-related endpoints (CRUD + search)
- In-memory storage for items
- Uses APIRouter with `/items` prefix

### `app/routers/users.py`
- All user-related endpoints
- In-memory storage for users
- Uses APIRouter with `/users` prefix

## Adding New Features

### Adding a New Router
1. Create `app/routers/products.py`:
```python
from fastapi import APIRouter
from app.models import Product
from app.logging_config import logger

router = APIRouter(
    prefix="/products",
    tags=["products"],
)

@router.get("")
async def get_products():
    logger.info("Fetching products")
    return []
```

2. Register it in `app/main.py`:
```python
from app.routers import items, users, products

app.include_router(products.router)
```

### Adding a New Model
Add to `app/models.py`:
```python
class Product(BaseModel):
    id: Optional[int] = None
    name: str
    category: str
    price: float
```

### Adding Custom Middleware
1. Create function in `app/middleware.py`
2. Register in `app/main.py`:
```python
app.middleware("http")(your_middleware_function)
```

## Migration Notes

### API Endpoint Changes
⚠️ **Important:** The search endpoint has moved!

**Old:**
```
GET /search?name=laptop
```

**New:**
```
GET /items/search/query?name=laptop
```

This change improves API organization by grouping the search with other item operations.

### No Breaking Changes for Other Endpoints
All other endpoints remain the same:
- `GET /items` ✓
- `POST /items` ✓
- `GET /items/{item_id}` ✓
- `PUT /items/{item_id}` ✓
- `DELETE /items/{item_id}` ✓
- `GET /users` ✓
- `POST /users` ✓

### Environment Variables (Unchanged)
- `LOG_LEVEL`: Set logging level (default: DEBUG)
- `ENVIRONMENT`: Set environment name (default: development)

## Testing the Refactored Application

### 1. Test Import
```bash
python -c "from app.main import app; print('✓ Success')"
```

### 2. Start Server
```bash
uvicorn main:app --reload
```

### 3. Test Endpoints
```bash
# Health check
curl http://localhost:8000/health

# Create an item
curl -X POST http://localhost:8000/items \
  -H "Content-Type: application/json" \
  -d '{"name": "Laptop", "price": 999.99}'

# Search items (new path!)
curl http://localhost:8000/items/search/query?name=laptop
```

### 4. Check Logs
You should see structured JSON logs with validation error details when sending invalid requests.

## Best Practices Implemented

✅ **Modular Architecture**: Separate concerns, easy to maintain  
✅ **Type Safety**: Full Pydantic validation  
✅ **Structured Logging**: JSON logs for cloud-native environments  
✅ **Error Handling**: Detailed validation error logging  
✅ **CORS Configuration**: Properly configured for frontend integration  
✅ **Health Checks**: Built-in health endpoint for orchestration  
✅ **Documentation**: Auto-generated OpenAPI docs at `/docs`  
✅ **Backwards Compatible**: Old commands still work  

## Next Steps

1. **Add Database**: Replace in-memory storage with SQLAlchemy
2. **Add Authentication**: Implement JWT or OAuth2
3. **Add Tests**: Create unit and integration tests
4. **Add Async Database**: Use `databases` or `asyncpg`
5. **Add Caching**: Implement Redis caching layer
6. **Add Rate Limiting**: Protect endpoints from abuse

## Questions?

- See `README.md` for general application documentation
- See `LOGGING_STANDARDS.md` and `LOGGING_GUIDE.md` for logging details
- See `DEBUGGING.md` for troubleshooting tips
- Check `/docs` endpoint for interactive API documentation

