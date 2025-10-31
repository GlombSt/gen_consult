# Documentation Organization

**Purpose:** How project documentation is organized and where to create new documentation files.

## Organization Principles

### Standards vs. Guides

- **`*_STANDARDS.md`** - Mandatory rules, concise, expert-focused ("what must be done")
  - Example: `EXCEPTION_HANDLING_STANDARDS.md`

- **`*_GUIDE.md`** - Detailed explanations with examples, tutorial-focused ("how to do it")
  - Example: `EXCEPTION_HANDLING_GUIDE.md`

**Rule:** When creating a `*_STANDARDS.md` file, consider a companion `*_GUIDE.md` for detailed explanations.

### Location Structure

Documentation lives where the code lives:

```
gen_consult/
├── [root]/                    # Project-wide docs (README.md, SETUP.md, TODO.md, CLAUDE.md)
├── declaring/                 # Backend docs
│   ├── *_STANDARDS.md         # Mandatory rules
│   ├── *_GUIDE.md             # Detailed explanations
│   ├── *_REFERENCE.md         # Quick lookup
│   ├── *_EXAMPLES.md          # Examples
│   ├── *_ARCHITECTURE.md      # Architecture docs
│   └── app/[domain]/
│       └── *_DOMAIN.md        # Domain-specific documentation
└── reacting/                  # Frontend docs (README.md, ARCHITECTURE.md)
```

## Naming Conventions

All documentation files use a consistent suffix pattern based on purpose:

- **`[TOPIC]_STANDARDS.md`** - Mandatory rules (e.g., `TESTING_STANDARDS.md`)
- **`[TOPIC]_GUIDE.md`** - Tutorials and detailed explanations (e.g., `EXCEPTION_HANDLING_GUIDE.md`)
- **`[TOPIC]_REFERENCE.md`** - Quick lookup/cheat sheets (e.g., `QUICK_REFERENCE.md`)
- **`[TOPIC]_EXAMPLES.md`** - Code/output examples (e.g., `LOGGING_EXAMPLES.md`)
- **`[TOPIC]_ARCHITECTURE.md`** - System/component architecture (e.g., `LOGGING_ARCHITECTURE.md`)
- **`[TOPIC].md`** - Special cases (e.g., `README.md`, `DEBUGGING.md`)

**Domain-specific documentation:** Use `[DOMAIN]_DOMAIN.md` in domain folders (e.g., `INTENTS_DOMAIN.md` instead of `INTENTS.MD`)

**Rule:** Always use descriptive suffixes. Avoid bare topic names without a suffix unless it's a special case (README, DEBUGGING).

### Document Header Template

```markdown
# [Title]

**Version:** [optional]
**Last Updated:** [date]
**Status:** [optional: MANDATORY, DRAFT, DEPRECATED]
**Audience:** [target audience]

[Brief description]

**Related Documentation:**
- [Link to related standards](./RELATED_STANDARDS.md)
- [Link to related guide](./RELATED_GUIDE.md)
```

## Adding New Documentation

### Decision Tree

1. **Where?**
   - Project-wide → root directory
   - Backend-specific → `declaring/`
   - Frontend-specific → `reacting/`
   - Domain-specific → `declaring/app/[domain]/`

2. **What type?**
   - Mandatory rules → `*_STANDARDS.md` (+ consider companion `*_GUIDE.md`)
   - Tutorials/explanations → `*_GUIDE.md`
   - Quick lookup/cheat sheet → `*_REFERENCE.md`
   - Code/output examples → `*_EXAMPLES.md`
   - System architecture → `*_ARCHITECTURE.md`
   - Domain model → `*_DOMAIN.md` (in domain folder)

### Checklist

- [ ] Correct location (root, `declaring/`, `reacting/`, or domain folder)
- [ ] Proper naming (`*_STANDARDS.md`, `*_GUIDE.md`, etc.)
- [ ] Document header with audience and related docs
- [ ] Cross-reference related documentation
- [ ] If creating Standard, consider companion Guide

## Maintenance

- **Cross-reference:** Standards link to Guides, Guides link to Standards
- **Update:** When standards change, update version/date; link new related docs
