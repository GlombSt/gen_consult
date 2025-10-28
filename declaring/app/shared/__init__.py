"""
Shared infrastructure and cross-cutting concerns.

This module contains components that are used across multiple domains.
"""

from .events import DomainEvent, EventBus, event_bus
from .logging_config import logger

__all__ = ["event_bus", "DomainEvent", "EventBus", "logger"]
