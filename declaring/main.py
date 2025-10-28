"""
Backwards-compatible entry point.
Imports the app from the new modular structure.

You can run the application using either:
- uvicorn main:app --reload
- uvicorn app.main:app --reload

The app.main module is recommended for the new structure.
"""
from app.main import app

__all__ = ["app"]
