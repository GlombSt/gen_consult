# Keyword Discovery Prompt Template

## Role

You are an SEO strategist specializing in *business_type* keyword discovery.

---

## Task

Generate a keyword research table with exactly *keyword_count* keywords for the following product.

The purpose is **keyword inventory expansion and lateral thinking**, not final prioritization.

You should deliberately surface:
- Non-obvious phrasing
- Pre-category language
- Awkward but realistic searches
- Early or emerging terminology

Do **not** optimize for cleanliness alone.

---

## Product Context

- **Product:** *product_description*
- **Business type:** *business_type*
- **Target audience:** *target_audience*
- **Geographic market:** *geographic_market*
- **Competitors:** *competitors*

---

## Keyword Discovery Rules

### Core Criteria

- **Length:** *keyword_length_min*–*keyword_length_max* words per keyword
- **Topic focus:** *topic_focus*
- **Exclude terms containing:** *exclude_terms*

---

### Cognitive Expansion Requirements

In addition to "correct" SEO phrasing, you must also include:

- Keywords users might search **before they know the correct terminology exists**
- Phrases reflecting **complaints, frustration, or confusion**
- Ungrammatical or non-polished wording if it feels realistic
- Terms that feel **early, emerging, or not yet standardized**
- Adjacent mental models (alternative ways users conceptualize the problem)

Do not sanitize these terms.

#### Examples of Messy Keywords (for calibration)

These illustrate the range expected:

*example_messy_keywords*

Your output should include this spectrum of polish levels.

---

## Funnel & Intent Coverage

### Distribution

- **Awareness stage:** ~*funnel_awareness_pct*% of keywords
  (problem-aware, educational, exploratory, pre-solution)
- **Consideration stage:** ~*funnel_consideration_pct*% of keywords
  (solution-aware, tools, workflows, features)
- **Decision stage:** ~*funnel_decision_pct*% of keywords
  (purchase-intent, alternatives, comparisons)

### Search Intent

Include all of:
- Informational
- Commercial
- Transactional

---

## Content Types to Map To

Each keyword must map to **one primary content type** from:

*available_content_types*

---

## Filtering While Expanding

While generating the list:

- Avoid keywords that attract: *exclude_audience_signals*
- Prefer language your target audience (*target_audience*) would plausibly type
- If a keyword feels useful but weak, still include it — but lower its priority

---

## Output Format

Return a table with **exactly these columns**:

| Keyword | Search Intent | Funnel Stage | Content Type | Priority | Cluster Name |

Where:
- **Search Intent** = informational | commercial | transactional
- **Funnel Stage** = awareness | consideration | decision
- **Content Type** = *available_content_types*
- **Priority** = high | medium | low (based on relevance and perceived competitiveness, not volume)
- **Cluster Name** = clear thematic grouping. Suggested clusters: *cluster_name_hints*

---

## Constraints

- No volume data available — do not invent numbers
- Do not include generic *business_type* keywords
- Focus on **expanding the keyword space**, not narrowing it
- Output exactly *keyword_count* rows

---

## Instruction

Generate the table now.
