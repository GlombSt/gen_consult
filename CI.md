# CI/CD Configuration

This project uses **GitHub Actions** for continuous integration and continuous deployment.

## Configuration Location

Workflow files are located in `.github/workflows/`:
- **Backend CI:** `.github/workflows/backend-ci.yml`
- **Frontend CI:** `.github/workflows/frontend-ci.yml`

## Workflow Triggers

The CI/CD workflows are configured to run based on changed files:

**Backend CI runs when:**
- Files in `declaring/` change
- Backend workflow file changes
- Push to `main` or `develop`
- Pull request to `main` or `develop`

**Frontend CI runs when:**
- Files in `reacting/` change
- Frontend workflow file changes
- Push to `main` or `develop`
- Pull request to `main` or `develop`

