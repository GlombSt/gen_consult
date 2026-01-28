"""
Intents domain public API.

This module exports the public interface of the intents domain.
Other domains should only import from this module, not from internal modules.
"""

from .router import router
from .schemas import (
    FactAddRequest,
    FactResponse,
    FactUpdateValueRequest,
    IntentCreateRequest,
    IntentResponse,
    IntentUpdateConstraintsRequest,
    IntentUpdateContextRequest,
    IntentUpdateDescriptionRequest,
    IntentUpdateNameRequest,
    IntentUpdateOutputFormatRequest,
    IntentUpdateOutputStructureRequest,
)
from .service import (
    add_fact_to_intent,
    create_intent,
    get_intent,
    remove_fact_from_intent,
    update_fact_value,
    update_intent_constraints,
    update_intent_context,
    update_intent_description,
    update_intent_name,
    update_intent_output_format,
    update_intent_output_structure,
)

__all__ = [
    # Service functions (public API)
    "create_intent",
    "get_intent",
    "update_intent_name",
    "update_intent_description",
    "update_intent_output_format",
    "update_intent_output_structure",
    "update_intent_context",
    "update_intent_constraints",
    "add_fact_to_intent",
    "update_fact_value",
    "remove_fact_from_intent",
    # Schemas (API contract)
    "IntentCreateRequest",
    "IntentResponse",
    "FactResponse",
    "IntentUpdateNameRequest",
    "IntentUpdateDescriptionRequest",
    "IntentUpdateOutputFormatRequest",
    "IntentUpdateOutputStructureRequest",
    "IntentUpdateContextRequest",
    "IntentUpdateConstraintsRequest",
    "FactAddRequest",
    "FactUpdateValueRequest",
    # Router
    "router",
]
