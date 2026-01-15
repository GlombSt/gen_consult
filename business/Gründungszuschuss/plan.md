# plan.md — Cursor Execution Plan

## Goal
Generate a complete Businessplan for a **Gründungszuschuss** application that is suitable for review and confirmation by a fachkundige Stelle (IHK).

---

## Inputs (Authoritative Sources)

Use inputs in the following order of precedence:

1. `business_plan_template.md`  
   Defines the required structure, section order, and headings. Do not change structure.

2. `business_plan_requirements - ihk.md`  
   Defines mandatory IHK constraints. Treat as hard requirements.

3. `business_plan_input.md`  
   Provides factual content and bullet points per section. Treat as ground truth.

4. `business_model_canvas.md`  
   Provides facts about the business idea in the structure of the business model canvas. Treat as additional ground truth for the generation.

5. `business-case-sheet.xlsx`  
   Provides all financials, assumptions, and calculations. Do not invent or adjust numbers.

6. `writing-style_policy.txt`  
   Governs wording, tone, and language rules.

7. `writing-correction-loop_policy.txt`  
   Governs post-processing and rewrite behavior.

---

## Process

1. **Drafting**
   - Populate each section from `business_plan_template.md`
   - Use only facts from `business_plan_input.md`
   - Use only numbers and assumptions from `business-case-sheet.xlsx`
   - Do not introduce new facts, estimates, or interpretations

2. **Consistency Check**
   - Ensure all numbers align with the spreadsheet
   - Ensure assumptions described in text match the financial model
   - Ensure no section contradicts IHK requirements

3. **Rewrite / Correction Loop**
   - Apply `writing-correction-loop_policy.txt`
   - Revise only wording and phrasing
   - Do not change facts, logic, or figures

---

## Output Rules

- Output must be in German
- Output a single, complete Businessplan document
- Follow the template structure exactly
- Do not include meta commentary, explanations, or notes
- Do not restate style or policy rules in the document

---

## Output Format & Media Handling

### Primary Output Format
The Businessplan is generated as **Markdown (CommonMark)**.  
This file (`business_plan.md`) is the single source of truth and is intended for downstream conversion to formatted documents (e.g. DOCX, PDF).

### Images
- Images may be included using standard Markdown syntax.
- Only images that support understanding (e.g. charts, diagrams) are permitted.
- Images must not replace required textual explanations.

Syntax:
```md
![Abbildung: Beschreibung](images/dateiname.png)

---

## Completion Criteria

The task is complete when:
- All template sections are filled
- All IHK requirements are satisfied
- Financials are internally consistent
- The document passes the correction loop without further changes