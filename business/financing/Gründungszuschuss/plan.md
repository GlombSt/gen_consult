# plan.md — Cursor Execution Plan

## Goal
Generate a complete Businessplan for a **Gründungszuschuss** application that is suitable for review and confirmation by a fachkundige Stelle (IHK).

You are teaming up with me to write a business plan that I use to receive a German "Gründungszuschuss". This `plan.md` explains your tasks. The business has not started yet and is in the planning phase, i.e. the solution is still being developed. Official start is March 1st, 2026.


---

## Inputs (Authoritative Sources)

Use inputs in the following order of precedence:

1. `business_plan_template with requirements.md`  
   Defines the required structure, section order, headings and questions that must be answered in each section. Do not change structure.

2. `business_plan_input.md`  
   Provides factual content and bullet points per section. Treat as ground truth.  Do not change facts, logic, or figures from here. The text contains XML Tags with instructions about how to present the content in the respective section. Example: <Berechne und erkläre: Private Einlagen, monatlich aus Sheet Liquidität/> Follow these instructions precisely.

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

### Interpreting input markup (required)

`business_plan_input.md` contains inline control markup (e.g. `<...>`). Treat these as **instructions**, not as content.

- **Apply, but dont use in output**: apply the instruction, but the markup itself must **not** appear in `output/business_plan.md`.
- **“Take literally” blocks** (e.g. `<take literally>...</take literally>`): keep the meaning and wording as-is except for minimal, strictly necessary edits to comply with the template headings and the style policy.
- **Placeholders / tasks** (e.g. `<Tabelle .../>`, `<Berechne .../>`, `<Zusammenfassung .../>`): these are mandatory work items. If the required source data is missing or cannot be located, mark the corresponding checklist row as `information_missing` and add a concrete bullet to `open_questions.md` (do not leave placeholders in the final document).


## Outputs 

To be created or populated as part of the task. May be empty at start.

1. `./output/business_plan.md`
2. `open_questions.md`
3. `coverage_checklist.md`
4. `./output/financials.md` (optional working file used during Phase 2 extraction)

---

## Process

### Phase 1: Section 1-5

0. **Initialize Coverage Checklist (must be done first)**
   - **Always** (re-)generate `coverage_checklist.md` at the start of **every run** (overwrite file)
   - Populate it with **one row per template prompt** from `business_plan_template with requirements.md`
   - This checklist is the driver for completeness and must exist before drafting starts
   - **Always** (re-)initialize `open_questions.md` at the start of **every run** (overwrite file)
     - Keep only the document header/structure initially
     - Add concrete bullets during drafting for every `information_missing` checklist item

1. **Drafting**
   - Create a new file `business_plan.md` and apply the section structure from `business_plan_template with requirements.md` for each section write the text that answers the questions. 
   - Do not introduce new facts, estimates, or interpretations
   - **Synthesize, don't enumerate:** Treat input bullet points as raw material. Combine related points into coherent paragraphs. Avoid repeating the input structure verbatim. Write flowing prose that integrates multiple facts into single, well-constructed sentences.
   - Write the section 1, Executive Summary, when sections 2 + 5 and 6 are complete.
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

   **Definition: “one row per template prompt”**
   - A “template prompt” is each explicit question/lead sentence in `business_plan_template with requirements.md` (e.g. `**Was bietest du an?**`) and each bullet question directly below it.
   - Use a stable identifier for each row: `Template Section > Subheading > Prompt text`.

3. **Consistency Check**
   - all section must be consistent with each other in use of terms, style and semantic consistency
   - Ensure that each section has the information from the source, not more and not less

   **Traceability (numbers & claims)**
   - For any numeric claim used in `business_plan.md`, record its precise origin in `coverage_checklist.md` (file + (if financial) `sheet_slug` + cell/range/table identifier from `llm_exports/...`). Keep the business plan text clean (no inline citations or meta-notes).

   **Locked terminology**
   - Maintain a short “locked terms” list (product name, offer names, key labels) derived from the authoritative sources and use those terms consistently. If sources conflict, prefer `business_plan_input.md` and capture the conflict as an `open_questions.md` item.


4. **Take-literally Integrity Check (must be done before rewrite)**
   - Purpose: enforce that all `<take literally>...</take literally>` blocks from `business_plan_input.md` are carried into `output/business_plan.md` without omissions or paraphrasing.
   - Treat each `<take literally>...</take literally>` block as a **must-include** text block. The markup itself must not appear in `output/business_plan.md`, but the block content must.

   **Verification procedure (mandatory)**
   - Extract all `<take literally>...</take literally>` blocks from `business_plan_input.md` in document order.
   - Normalize for comparison: collapse repeated whitespace and normalize line breaks in both source blocks and `output/business_plan.md`.
   - For each block: verify that the normalized block text occurs as a contiguous substring in `output/business_plan.md`.

   **Failure handling (hard fail)**
   - If any block is missing or shortened:
     - Add a bullet to `open_questions.md` that includes: section context + the exact missing block (verbatim) + where it should appear.
     - Mark the corresponding `coverage_checklist.md` row(s) as `information_missing` with a note `take literally missing`.
     - The run is **not complete**. Do not proceed to the rewrite loop until all missing blocks are present in `output/business_plan.md`.

5. **Rewrite / Correction Loop**
   - Apply `writing-correction-loop_policy.txt`
   - Revise only wording and phrasing

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
2. Extract the required tables/series into `./output/financials.md` (prefer `cells.jsonl` when formulas/types matter; `grid.csv` for quick chart data).
3. Draft Section 6 using the template structure and extracted data.
4. Verify consistency between text (sections 1–5) and numbers (section 6).
5. Integrate into final `business_plan.md`.


---

## Output Rules

- Output must be in German
- Output a single, Businessplan document
- Follow the template structure exactly; apply page breaks per the rules in **Export-friendly Markdown Rules (Pandoc-safe subset)** below.
- Do not include meta commentary, explanations, or notes
- Do not restate style or policy rules in the document

---

## Writing Quality Rules

- **Text over lists:** Where is helps understanding and readabilty, convert bullet-point input into flowing paragraphs. Use lists for genuinely enumerable items (e.g., product features, competitor tables).
- **Avoid mechanical repetition:** Do not mirror the input structure. Reorganize information for readability and logical flow.
- **One idea, one sentence:** Each sentence should convey a complete thought. Avoid run-on sentences. Be concise
- **Context before detail:** Start paragraphs with the main point, then elaborate.
- **Paragraph structure:** Structure content into distinct paragraphs, each covering one main topic. This is especially important for the Executive Summary, which should be divided into logical paragraphs (e.g., business idea, target customers, founder qualifications, financial projections, financing). Each paragraph should be 3-5 sentences maximum. Avoid creating single long paragraphs that are difficult to read.
- When the input has sources (links) the sources must be presented in the document. Please validate that the link exists.
- Use all information from the input, don't omit details. The input is intentionally very concise, but everything is chosen deliberately there, *so stick to the exact meaning that is conveyed in the input*
- follow the instructions in XML Tags precisely.
- if a paragraph from the input is already of high quality, only make minimal changes to it.
- Don't state common knowledge, Bad: "Die Liquiditätsplanung stellt Ein- und Auszahlungen sowie die Entwicklung der Liquidität auf Monatsbasis dar."
- Prefer term "Generative KI" over "Sprachmodelle"

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
This file (`business_plan.md`) is the single source of truth and is intended for downstream conversion to formatted documents (DOCX, PDF).

**Canonical path:** `business/Gründungszuschuss/output/business_plan.md`  
**Canonical Word template path:** `business/Gründungszuschuss/output/reference.docx`  

### Export-friendly Markdown Rules (Pandoc-safe subset)
Goal: keep `business_plan.md` convertible to **auditor-ready** DOCX/PDF with stable tables, headings, and page breaks.

#### Headings & Structure
- Use **Variante B**: document metadata via **YAML frontmatter** (Pandoc), and the content structure starts with chapter headings.
- Chapters must be **H1** (e.g. `# Executive Summary`, `# Geschäftsidee`, ...), sub-sections **H2**, sub-sub-sections **H3**.
- If numbering is desired, include it **in the heading text** consistently (e.g. `# 1. Executive Summary`, `# 2. Geschäftsidee`, ...).
- Do not “jump” heading levels (e.g. H2 → H4)
- Do not use horizontal rules (`---`) in the generated output (`output/business_plan.md`) to simulate structure. Exception: the YAML frontmatter delimiters (`---`) at the very top of the file are allowed.

#### Tables (most important for audit)
Grid tables only. Caption required above each table (`Table: Caption text`), blank line before table. 

**Alignment** (colons in `=====` header separator):
- Right: `+========:+` — use for numbers/currency
- Left: `+:========+` — default for labels
- Centered: `+:=======:+`

**Rules:**
- No leading spaces in cells (causes font issues), BAD: "|  2 |", Good: "|2   |"
- No indentation
- German numbers: `7.004,00`
- Escape pipes: `\|`
- Keep `n. Z.` and `-` verbatim
- Table caption text names unit of values

**Example:**
```
Table: Beispiel (2026–2028)

+----------+=========:+=========:+=========:+
| Position |     2026 |     2027 |     2028 |
+==========+=========:+=========:+=========:+
| Summe    | 7.004,00 | 7.004,00 | 304,00   |
+----------+----------+----------+----------+
```

#### Citations

Never inline URLs in prose. Use footnotes.

**Syntax:**
```
Statement with source.[^id]

[^id]: Source Name: https://example.com/path
```

**Rules:**
- Short unique IDs: `[^fbi]`, `[^mck1]`
- Footnote format: `Name: URL`
- Multiple sources: `[^1][^2]`
- Collect all footnote definitions at document end
- No bare URLs in text

#### Lists & paragraphs
- Keep one blank line between block elements (headings, lists, tables, paragraphs).
- Lists must not “run into” tables and vice versa.

#### Inline formatting
- Use `**bold**`, `*italic*`, and `` `code` `` only (no raw HTML).
- Avoid exotic Markdown extensions unless explicitly required.

#### Placeholders
- Avoid placeholders like `TBD` in final export artifacts. If information is missing, it must be captured in `open_questions.md`.

### Export workflow (Docker, reproducible)
From repo root, run:

```bash
./business/Gründungszuschuss/export.sh
```

This generates:
- `business/Gründungszuschuss/output/business_plan.docx`
Optional styling template:
- `business/Gründungszuschuss/output/reference.docx`

PDF should be exported manually from the generated DOCX (Word/LibreOffice), to keep the pipeline minimal.

### Images
- Images may be included using standard Markdown syntax.
- Only images that support understanding (e.g. charts, diagrams) are permitted.
- Images must not replace required textual explanations.


---

## Phrasing preferences

- In examples like this "Ich baue unter dem Namen „SharpIntent“" don't use the word "baue", other option "entwickle"
- The output should not be a summary of the input, but a better version: it must read like the final business plan not like a recap of input notes.
- Avoid "input-referencing" phrasing like: ".. laut Input ...". 
- Do not replace specific terms from input with broader synonyms.
- Quick examples:
  - Bad: "Als Zielgruppen sind genannt: Startups, KMU."
  - Good: "Zielgruppen sind Startups und KMU." / "Zielgruppen: Startups, KMU."
  - Bad: "(Angaben aus dem Input)"
  - Bad: "Der Input bewertet ..."

---

## Completion Criteria

The task is complete when:
- All sections are filled
- No 'not_started' items in coverage_checklist.md
- The document passes the correction loop without further changes
- No instruction markup or placeholders from inputs remain in `output/business_plan.md`
