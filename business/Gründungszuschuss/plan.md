# plan.md — Cursor Execution Plan

## Goal
Generate a complete Businessplan for a **Gründungszuschuss** application that is suitable for review and confirmation by a fachkundige Stelle (IHK).

---

## Inputs (Authoritative Sources)

Use inputs in the following order of precedence:

1. `business_plan_template with requirements.md`  
   Defines the required structure, section order, headings and questions that must be answered in each section. Do not change structure.

2. `business_plan_input.md`  
   Provides factual content and bullet points per section. Treat as ground truth.

3. `business_model_canvas.md`  
   Provides facts about the business idea in the structure of the business model canvas. Treat as additional ground truth for the generation.

4. `business-case-sheet.xlsx`  
   Provides all financials, assumptions, and calculations (authoritative).  
   **Do not parse the XLSX directly.** Instead, regenerate and use the LLM-friendly exports in:  
   `business/Gründungszuschuss/llm_exports/business-case-sheet/` (see Phase 2).

5. `writing-style_policy.txt`  
   Governs wording, tone, and language rules.

6. `writing-correction-loop_policy.txt`  
   Governs post-processing and rewrite behavior.


## Outputs 

To be created or populated as part of the task. May be empty at start.

1. `business_plan.md`
2. `open_questions.md`
3. `coverage_checklist.md`

---

## Process

### Phase 1: Section 1-5

0. **Initialize Coverage Checklist (must be done first)**
   - (Re-)generate `coverage_checklist.md` at the start of the task (overwrite file)
   - Populate it with **one row per template prompt** from `business_plan_template with requirements.md`
   - This checklist is the driver for completeness and must exist before drafting starts

1. **Drafting**
   - Create a new file `business_plan.md` and apply the section structure from `business_plan_template with requirements.md` for each section write the text that answers the questions. 
   - Do not introduce new facts, estimates, or interpretations
   - **Synthesize, don't enumerate:** Treat input bullet points as raw material. Combine related points into coherent paragraphs. Avoid repeating the input structure verbatim. Write flowing prose that integrates multiple facts into single, well-constructed sentences.
   - Write the section 1, Executive Summary, when sections 2 and 5 are complete.
   - If input for a section is missing: explicitly state what is missing in a file: "open_questions.md"

2. **Coverage Checklist (Agent-owned, maintained during drafting)**
   - Purpose: ensure **every template question/prompt is covered** (answered, partially answered, or explicitly missing) so nothing gets lost during synthesis.
   - Update the pre-populated `coverage_checklist.md` rows as drafting progresses.
   - Maintain and update `coverage_checklist.md` (agent-owned) during drafting. Each row maps **one template prompt** to:
     - where it is answered in `business_plan.md` (section/heading)
     - the authoritative source(s) used (e.g. `business_plan_input.md`, `business_model_canvas.md`, `llm_exports/...`)
     - status: `answered | information_missing | not_started`
   - For `information_missing` prompts: add a concrete bullet to `open_questions.md` that states exactly what information is needed to complete the prompt.
   - The user does **not** need to maintain this checklist; the agent keeps it and uses it to drive completeness.

3. **Consistency Check**
   - all section must be consistent with each other in use of terms, style and semantic consistency
   - will be done by a human

4. **Rewrite / Correction Loop**
   - Apply `writing-correction-loop_policy.txt`
   - Revise only wording and phrasing
   - Do not change facts, logic, or figures

### Phase 2: Section 6, Financials 

#### Where the financials can be found

- **Source XLSX (authoritative)**: `business/Gründungszuschuss/business-case-sheet.xlsx`
- **LLM-friendly exports (use these for extraction/charting)**:  
  `business/Gründungszuschuss/llm_exports/business-case-sheet/`
  - `workbook.json` = sheet index + used ranges + artifact paths  
  - `sheets/<sheet_slug>/grid.csv` = rectangular values grid (easy for charts)  
  - `sheets/<sheet_slug>/cells.jsonl` = typed values + formulas (best for reasoning)

#### Step 0: Regenerate exports (always run this first)

From repo root, run:

```bash
PYTHONPYCACHEPREFIX=./.pycache python3 business/tools/xlsx_to_llm.py \
  business/Gründungszuschuss/business-case-sheet.xlsx \
  --out business/Gründungszuschuss/llm_exports/business-case-sheet
```

#### Drafting steps

1. Use `workbook.json` to locate the relevant sheets (e.g. `umsatz`, `kosten`, `liquiditaet`, `rentabilitaet`) and their artifact files.
2. Extract the required tables/series into `financials.md` (prefer `cells.jsonl` when formulas/types matter; `grid.csv` for quick chart data).
3. Draft Section 6 using the template structure and extracted data.
4. Verify consistency between text (sections 1–5) and numbers (section 6).
5. Integrate into final `business_plan.md`.


---

## Output Rules

- Output must be in German
- Output a single, Businessplan document
- Follow the template structure exactly
- Do not include meta commentary, explanations, or notes
- Do not restate style or policy rules in the document

---

## Writing Quality Rules

- **Text over lists:** Where is helps understanding and readabilty, convert bullet-point input into flowing paragraphs. Use lists for genuinely enumerable items (e.g., product features, competitor tables).
- **Synthesize related facts:** If multiple input points address the same topic, combine them into a single coherent statement.
- **Avoid mechanical repetition:** Do not mirror the input structure. Reorganize information for readability and logical flow.
- **One idea, one sentence:** Each sentence should convey a complete thought. Avoid run-on sentences.
- **Context before detail:** Start paragraphs with the main point, then elaborate.
- When the input has sources (links) the sources must be presented in the document. Please validate that the link exists.
- Use all information from the input, don't omit details. The input is intentionally very concise, but everything is chosen deliberately there.

### Example Transformation

**Input (bullet points):**
```
- Nutzer sparen Zeit
- Erwartungen werden angepasst  
- Berührungsängste werden reduziert
- Risiko sinkt
```

**Bad output (enumeration):**
> Nutzer sparen Zeit. Erwartungen werden angepasst. Berührungsängste werden reduziert. Das Risiko sinkt.

**Good output (synthesis):**
> Durch die strukturierte Aufgabenerfassung sparen Nutzer Zeit und gewinnen Klarheit über die Möglichkeiten und Grenzen von Sprachmodellen. Das reduziert sowohl die Hemmschwelle bei der Nutzung als auch das Risiko fehlerhafter Ergebnisse.

---

## Output Format & Media Handling

### Primary Output Format
The Businessplan is generated as **Markdown (CommonMark)**.  
This file (`business_plan.md`) is the single source of truth and is intended for downstream conversion to formatted documents (e.g. DOCX, PDF). Creation of the docx is not in scope of this plan.

### Images
- Images may be included using standard Markdown syntax.
- Only images that support understanding (e.g. charts, diagrams) are permitted.
- Images must not replace required textual explanations.


---

## Completion Criteria

The task is complete when:
- All sections are filled
- No 'not_started' items in coverage_checklist.md
- The document passes the correction loop without further changes