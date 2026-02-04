"""
Intents domain public API (V2).

This module exports the public interface of the intents domain.
Other domains should only import from this module, not from internal modules.
"""

from .router import router
from .schemas import (
    IntentCreateRequest,
    IntentResponse,
    IntentUpdateDescriptionRequest,
    IntentUpdateNameRequest,
)
from .service import (
    create_intent,
    get_intent,
    update_intent_description,
    update_intent_name,
)

__all__ = [
    # Service functions (public API)
    "create_intent",
    "get_intent",
    "update_intent_name",
    "update_intent_description",
    # Schemas (API contract)
    "IntentCreateRequest",
    "IntentResponse",
    "IntentUpdateNameRequest",
    "IntentUpdateDescriptionRequest",
    # Router
    "router",
]
