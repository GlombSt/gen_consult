# Gen Consult - Repository Setup Guide

This guide walks you through setting up the `gen_consult` repository for the first time.

## ✅ What We've Created

The following files have been created:
- ✅ `.gitignore` - Ignores Python venv, Node modules, build artifacts
- ✅ `README.md` - Project overview and documentation
- ✅ `CLAUDE.md` - Architecture guidance for AI assistants
- ✅ `TODO.md` - Architecture alignment tasks
- ✅ `.github/workflows/backend-ci.yml` - Backend CI pipeline
- ✅ `.github/workflows/frontend-ci.yml` - Frontend CI pipeline

## 📋 Steps to Initialize Repository

### Step 1: Initialize Git

```bash
cd /Users/steffen.glomb/dev/gen_consult

# Initialize git repository
git init

# Check status
git status
```

You should see all your files listed as "Untracked".

### Step 2: Make Initial Commit

```bash
# Stage all files
git add .

# Create initial commit
git commit -m "Initial commit: Multi-project repository with hexagonal architecture

- Backend (declaring/): FastAPI with domain-driven design
- Frontend (reacting/): React with feature-based organization
- Architecture docs: CLAUDE.md, TODO.md
- CI/CD: GitHub Actions workflows for both projects"

# Verify commit
git log --oneline
```

### Step 3: Create GitHub Repository

**Option A: Using GitHub CLI (if installed)**

```bash
# Create repository on GitHub
gh repo create gen_consult --public --source=. --remote=origin

# Push to GitHub
git push -u origin main
```

**Option B: Using GitHub Web Interface**

1. Go to https://github.com/new
2. Repository name: `gen_consult`
3. Description: "Full-stack hexagonal architecture learning project"
4. Visibility: Public or Private (your choice)
5. **DO NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

Then connect your local repo:

```bash
# Replace YOUR_USERNAME with your GitHub username
git remote add origin https://github.com/YOUR_USERNAME/gen_consult.git

# Rename branch to main (if needed)
git branch -M main

# Push to GitHub
git push -u origin main
```

### Step 4: Verify GitHub Setup

```bash
# Check remote
git remote -v

# You should see:
# origin  https://github.com/YOUR_USERNAME/gen_consult.git (fetch)
# origin  https://github.com/YOUR_USERNAME/gen_consult.git (push)
```

Visit your repository on GitHub to verify everything is there.

### Step 5: Set Up Branch Protection (Optional but Recommended)

On GitHub:
1. Go to Settings → Branches
2. Add rule for `main` branch
3. Enable:
   - ✅ Require status checks to pass before merging
   - ✅ Require branches to be up to date before merging
   - ✅ Status checks: `Test Backend`, `Build and Test Frontend`
4. Save changes

## 🔧 Local Development Setup

### Backend Setup

```bash
cd declaring

# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # macOS/Linux
# Or on Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn main:app --reload
```

Visit: `http://localhost:8000/docs`

### Frontend Setup

```bash
cd reacting

# Install dependencies
npm install

# Run dev server
npm run dev
```

Visit: `http://localhost:5173`

## 🧪 Verify CI/CD Workflows

### Test Backend Workflow Locally

```bash
cd declaring

# Install test dependencies
pip install pytest pytest-cov pytest-asyncio flake8

# Run linting
flake8 app/ --count --max-line-length=100 --statistics

# Run tests with coverage
pytest --cov=app --cov-report=term-missing --cov-fail-under=80 -v
```

### Test Frontend Workflow Locally

```bash
cd reacting

# Build (this is what CI does)
npm run build

# Check build output
ls -la dist/
```

## 📝 Next Steps

### 1. Make Your First Change

```bash
# Create a new branch
git checkout -b feature/your-feature-name

# Make changes to code
# ...

# Commit and push
git add .
git commit -m "Add feature: description"
git push origin feature/your-feature-name
```

### 2. Create Pull Request

On GitHub:
1. Click "Pull requests" → "New pull request"
2. Select your branch
3. Create PR
4. Watch CI/CD workflows run automatically

### 3. Review Architecture Tasks

Check `TODO.md` for pending architectural decisions:
- TypeScript migration?
- Testing framework choice?
- Real-time updates strategy?
- Type synchronization approach?

## 🎯 Workflow Triggers

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

**Example:**
```bash
# Change only backend
git add declaring/app/items/service.py
git commit -m "Update item service"
git push
# ✅ Backend CI runs
# ⏭️  Frontend CI skips

# Change only frontend
git add reacting/src/components/ItemList.jsx
git commit -m "Update item list"
git push
# ⏭️  Backend CI skips
# ✅ Frontend CI runs

# Change both
git add declaring/ reacting/
git commit -m "Add orders feature"
git push
# ✅ Backend CI runs
# ✅ Frontend CI runs
```

## 🐛 Troubleshooting

### Git Issues

**Problem: Already has a .git directory**
```bash
# If declaring/ or reacting/ have their own .git
rm -rf declaring/.git reacting/.git
git add .
git commit -m "Consolidate into single repo"
```

**Problem: Wrong remote URL**
```bash
git remote remove origin
git remote add origin https://github.com/YOUR_USERNAME/gen_consult.git
git push -u origin main
```

### GitHub Actions Issues

**Problem: Workflows not running**
- Check that you've pushed to `main` or `develop` branch
- Check that you've changed files in the right directories
- Go to Actions tab on GitHub to see workflow status

**Problem: Tests failing in CI**
- Run tests locally first
- Check Python/Node versions match
- Verify all dependencies are in requirements.txt / package.json

## ✨ You're All Set!

Your repository is now:
- ✅ Initialized with git
- ✅ Pushed to GitHub
- ✅ CI/CD configured
- ✅ Documentation complete
- ✅ Ready for development

**Next:** Read `CLAUDE.md` for architecture guidance and start building!

## 📚 Reference

- Main docs: `README.md`
- Architecture: `CLAUDE.md`
- Tasks: `TODO.md`
- Backend: `declaring/README.md`
- Frontend: `reacting/README.md`
