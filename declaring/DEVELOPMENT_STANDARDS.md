# Development Standards

**Version:** 1.0  
**Last Updated:** January 2025  
**Status:** MANDATORY - All new features must follow TDD  
**Audience:** Developers

---

## Core Principles

1. **Test-Driven Development (TDD)** - Write tests first, then implement code
2. **Red-Green-Refactor** - Failing test → passing code → improvement
3. **Fast Feedback** - Run tests frequently during development


---
## 1. Understanding Before Acting
- Read and understand the existing codebase structure before making changes
- Review related files and dependencies
- Ask clarifying questions if requirements are ambiguous
- Identify potential impacts on other parts of the system


## 2. Code Organization
- Follow standards defined in [ARCHITECTURE_STANDARDS.md](./ARCHITECTURE_STANDARDS.md)


## 3. Development Steps
When implementing new features or fixes:

a. **Plan First**
   - Outline the approach
   - Identify files that need changes
   - Consider edge cases and error scenarios

b. **Write Tests First**
   - Write unit tests for business logic
   - Write integration tests for API endpoints
   - Use pytest and FastAPI's TestClient
   - Aim for meaningful test coverage, not just high percentages

c. **Implement Incrementally**
   - Make one logical change at a time
   - Run tests after each change
   - Keep tests passing (green)
   - Refactor only when tests pass

d. **Validate Before Commit**
   - Run `./lint.sh --fix` then `./lint.sh` (all checks pass)
   - Run `pytest` (all tests pass)
   - Code is properly formatted, no unused imports, no trailing whitespace
   - Type checking passes
   - No sensitive data in code
   - Documentation updated
   - Error handling is comprehensive
   - Logs are meaningful

