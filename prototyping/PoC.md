Intent:
Creating an NDA Template

Description:
I need a Non Disclosure agreement for a mentoring role with a startup.


Prompt:
You are helping a person refine an intent. They are at the start of creating it. Please provide relevant insights that will add clarity to the intent and hence remove ambiguity when the intent is acted upon by an individual, machine or agaent.


An insights should have:
- Descroiption: description of a piece information or data points that will increase clarity
- Rational: An explanation why this incresing clarity
- Options: If meaningful, a set of concrete options or a text that can be presented and chosen or adapted by a user.


<Intent>
Name: Creating an NDA
Description: I need a Non Disclosure agreement for a mentoring role with a startup.
</Intent>

The result should be a list of insights that have a relevance score (1-10, 10 = highest relevance) and are sorted by relevance.
Start with defining a list of candidate insights, then return 5 top scored insights.
In the result also convey whether you have more insights with scores > 5.

The result should be in json following this schema:

{
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "https://example.com/schemas/intent-insights.schema.json",
    "title": "Intent Insights Result",
    "description": "Schema for intent refinement insights that add clarity and remove ambiguity",
    "type": "object",
    "required": ["intent", "insights"],
    "properties": {
      "intent": {
        "type": "object",
        "description": "The original intent being refined",
        "required": ["name", "description"],
        "properties": {
          "name": {
            "type": "string",
            "description": "Name or title of the intent",
            "minLength": 1
          },
          "description": {
            "type": "string",
            "description": "Detailed description of what the intent aims to accomplish",
            "minLength": 1
          }
        }
      },
      "insights": {
        "type": "object",
        "description": "Collection of insights to clarify the intent",
        "required": ["top_insights"],
        "properties": {
          "top_insights": {
            "type": "array",
            "description": "Top-ranked insights sorted by relevance",
            "minItems": 1,
            "items": {
              "$ref": "#/definitions/insight-candidate"
            }
          },
          "additional_insights_available": {
            "type": "boolean",
            "description": "Indicates whether more insights exist beyond those returned"
          },
          "additional_insights_count": {
            "type": "integer",
            "description": "Number of additional insights available",
            "minimum": 0
          },
          "additional_insights_summary": {
            "type": "array",
            "description": "Summary of additional available insights",
            "items": {
              "$ref": "#/definitions/insight_summary"
            }
          }
        }
      },
      "metadata": {
        "type": "object",
        "description": "Metadata about the insight generation process",
        "properties": {
          "total_candidate_insights": {
            "type": "integer",
            "description": "Total number of candidate insights identified",
            "minimum": 0
          },
          "insights_above_threshold": {
            "type": "integer",
            "description": "Number of insights above the relevance threshold",
            "minimum": 0
          },
          "threshold_score": {
            "type": "integer",
            "description": "Minimum relevance score threshold applied",
            "minimum": 1,
            "maximum": 10
          },
          "generated_at": {
            "type": "string",
            "description": "ISO 8601 date when insights were generated",
            "format": "date"
          }
        }
      }
    },
    "definitions": {
      "insight-candidate": {
        "type": "object",
        "description": "A single insight that adds clarity to the intent",
        "required": [
          "rank",
          "relevance_score",
          "title",
          "description",
          "rationale"
        ],
        "properties": {
          "rank": {
            "type": "integer",
            "description": "Ranking position of this insight (1 = highest)",
            "minimum": 1
          },
          "relevance_score": {
            "type": "integer",
            "description": "Relevance score from 1-10, where 10 is highest relevance",
            "minimum": 1,
            "maximum": 10
          },
          "title": {
            "type": "string",
            "description": "Short title summarizing the insight",
            "minLength": 1
          },
          "description": {
            "type": "string",
            "description": "Description of information or data points that will increase clarity",
            "minLength": 1
          },
          "rationale": {
            "type": "string",
            "description": "Explanation of why this insight increases clarity",
            "minLength": 1
          },
          "options": {
            "type": "array",
            "description": "Concrete options that can be presented and chosen or adapted by a user",
            "items": {
              "$ref": "#/definitions/option"
            }
          },
          "freeform_guidance": {
            "type": "string",
            "description": "Alternative to structured options: freeform text guidance for user input"
          }
        }
      },
      "option": {
        "type": "object",
        "description": "A selectable option for an insight",
        "required": ["id", "label"],
        "properties": {
          "id": {
            "type": "string",
            "description": "Unique identifier for this option",
            "pattern": "^[a-z0-9_]+$"
          },
          "label": {
            "type": "string",
            "description": "Human-readable label for the option",
            "minLength": 1
          },
          "detail": {
            "type": "string",
            "description": "Additional detail or explanation about this option"
          }
        }
      }
    }
  }