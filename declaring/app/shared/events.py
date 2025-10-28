"""
Domain event system for event-driven analytics.

All significant business actions must publish domain events.
"""

import asyncio
from abc import ABC
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List

from .logging_config import logger


@dataclass
class DomainEvent(ABC):
    """
    Base class for all domain events.

    All events must include timestamp and event_type.
    """

    timestamp: datetime
    event_type: str

    def to_dict(self) -> dict:
        """Convert event to dictionary for serialization."""
        result = {"timestamp": self.timestamp.isoformat(), "event_type": self.event_type}
        # Add all other attributes
        for key, value in self.__dict__.items():
            if key not in ["timestamp", "event_type"]:
                if isinstance(value, datetime):
                    result[key] = value.isoformat()
                else:
                    result[key] = value
        return result


class EventBus:
    """
    Simple in-memory event bus for domain events.

    In production, this would be replaced with a message queue (RabbitMQ, Kafka, etc.)
    """

    def __init__(self):
        self._handlers: Dict[str, List[Callable]] = {}

    def subscribe(self, event_type: str, handler: Callable) -> None:
        """
        Subscribe a handler to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Async function to handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        logger.info(
            "Event handler subscribed",
            extra={"event_type": event_type, "handler": handler.__name__}
        )

    async def publish(self, event: DomainEvent) -> None:
        """
        Publish a domain event to all subscribed handlers.

        Args:
            event: The domain event to publish
        """
        logger.info(
            "Domain event published",
            extra={"event_type": event.event_type, "event_data": event.to_dict()}
        )

        handlers = self._handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)
            except Exception as e:
                logger.error(
                    "Event handler failed",
                    extra={
                        "event_type": event.event_type,
                        "handler": handler.__name__,
                        "error_message": str(e)
                    },
                    exc_info=True,
                )


# Global event bus instance
event_bus = EventBus()
