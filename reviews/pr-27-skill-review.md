# PR #27 Review: "Add agent skill: Pydantic models as source of truth"

## Summary

The skill at `.agent/skills/models-as-source-of-truth.md` is **not properly anchored** in the project's agent configuration and is **largely redundant** with existing mandatory standards in `ARCHITECTURE_STANDARDS.md`. It also introduces a **source-of-truth conflict**. The PR bundles unrelated changes that should be separated.

---

## 1. Skill Anchoring — Not Rooted

- **No `agents.md` or `AGENTS.md`** exists in the repository. The skill has no registry or index.
- **`CLAUDE.md` has no reference** to `.agent/skills/` or this skill. Agents won't discover it.
- **`.cursorrules`** references `CLAUDE.md` as the entry file but does not reference `.agent/skills/`.

**Result:** The skill is orphaned — no agent configuration knows it exists.

**Fix:** Register in `CLAUDE.md` (new "Skills" section) or create `.agent/agents.md` index.

---

## 2. Redundancy with Existing Standards

The skill's core claims are already covered in `intentions/ARCHITECTURE_STANDARDS.md` (lines 142–237):

| Skill Claim | Already Documented? | Location |
|---|---|---|
| Pydantic Field descriptions are normative | Yes (MANDATORY) | `ARCHITECTURE_STANDARDS.md:142-161` |
| schemas.py is single source of truth for API/MCP | Yes (MANDATORY) | `ARCHITECTURE_STANDARDS.md:163-237` |
| APIs/OpenAPI follow schema definitions | Yes | `ARCHITECTURE_STANDARDS.md:169-180` |
| MCP tools derive from Pydantic models | Yes | `ARCHITECTURE_STANDARDS.md:173` |
| Clients must not contradict model descriptions | Partially | `CLAUDE.md:100` |
| service.py docstrings as operation source | Yes | `ARCHITECTURE_STANDARDS.md:196-237` |

**Result:** The skill adds no new actionable guidance beyond what's already mandatory.

---

## 3. Source-of-Truth Conflict

**Skill says:** Pydantic models (schemas.py) are the **single source of truth** — implying schemas.py is the origin of semantics.

**Existing standards say:** `*_DOMAIN.md` is the source of truth → schemas.py must match domain docs (`ARCHITECTURE_STANDARDS.md:144-146`).

```
Existing hierarchy:
  *_DOMAIN.md (authoritative semantics)
    → schemas.py (must match domain docs)
      → OpenAPI / MCP / clients (auto-derived)

Skill's hierarchy:
  schemas.py (authoritative)
    → everything else
```

**Result:** Conflicting direction of authority. Agents would not know which to update first.

---

## 4. PR Hygiene

- **Scope creep:** 23 files changed (3542+, 2902-) but only 35 lines are the skill. Rest is intents domain refactor + business directory restructuring.
- **Temp file committed:** `~$siness_plan.docx` (Word lock file) should never be in VCS.
- **Binary files:** `.docx` and `.pdf` being moved/added.
- **Recommendation:** Split into separate PRs (skill definition vs. domain refactor vs. business file reorg).

---

## 5. Recommendations

1. **Don't merge skill as-is** — redundant and conflicting.
2. **Split the PR** — skill, domain refactor, and business reorg should be separate.
3. **If keeping the skill:**
   - Align with existing `*_DOMAIN.md` → `schemas.py` hierarchy, OR
   - Update `ARCHITECTURE_STANDARDS.md` to remove `*_DOMAIN.md` as source of truth.
4. **Root the skill** — reference in `CLAUDE.md` or new `.agent/agents.md`.
5. **Remove temp file** — `~$siness_plan.docx`.
6. **Update `.gitignore`** — add `~$*` pattern.
