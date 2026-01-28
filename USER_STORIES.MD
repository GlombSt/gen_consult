User stories build on the domain concepts described in the ./intentions/app/* directories, e.g. INTENTS_DOMAIN.MD


Increment 1: Declaration
US-000: User creates new intent.
US-001: User edits the intent name.
US-002: User edits the intent description.
US-003: User edits the intent output format.
US-004: User edits the intent output structure.
US-005: User edits the intent context.
US-006: User edits the intent constraints.
US-007: User edits a fact value.
US-008: User adds a new fact to an intent.
US-009: User removes a fact from an intent. 
US-010: User sees aspects of declaration inside its own panel, sligthlty separate from outputs or chat.
US-010: User reviews output and prompt in an output section with 2 large text areas. Both parts are not editable.
US-011: User has a chat window on the right to communicate with the consultant
US-012: Systems stores edits automatically in the background, so that user does not have to worry about save semantics


Increment 2: Trivial Generation and Review

US-201: User annotates output so consultant adjusts declarations to improve prompt generation.
US-204: User reviews and annotates prompt so consultant improves declarations.
US-205: User triggers prompt and output generation to test output.

Increment x: Backlog
Consultant uses DSPy to derive best prompt.
Consultant chooses right prompting technique for definition of prompt, based on declaration and output information.
User connects external sources (e.g., JIRA, Confluence, Zapier) to context to reference facts.
User publishes prompt via API.
Consultant uses sample output to infer declarations required for generating desired output.
User versions declaration explicitly, including latest prompt
System automatically versions declaration on first execution of a generated prompt.