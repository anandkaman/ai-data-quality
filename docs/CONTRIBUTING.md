# Contributing to AI Data Quality Guardian

Thank you for your interest in contributing! This document provides guidelines and instructions for contributing to the project.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Development Setup](#development-setup)
3. [Project Structure](#project-structure)
4. [Making Changes](#making-changes)
5. [Coding Standards](#coding-standards)
6. [Testing](#testing)
7. [Submitting Changes](#submitting-changes)
8. [Areas for Contribution](#areas-for-contribution)

---
## Getting Started

### Prerequisites

- **Python 3.11+**
- **Node.js 18+**
- **Git**
- **Ollama** (for LLM features)
- **Basic knowledge** of React and FastAPI

### Fork the Repository

1. Visit [https://github.com/yourusername/ai-data-quality-guardian](https://github.com/yourusername/ai-data-quality-guardian)
2. Click "Fork" button (top right)
3. Clone your fork:

```
git clone https://github.com/YOUR_USERNAME/ai-data-quality-guardian.git
cd ai-data-quality-guardian
```

4. Add upstream remote:

```
git remote add upstream https://github.com/original/ai-data-quality-guardian.git
```

---

## Development Setup

### Backend Setup

```
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Edit .env with your settings

# Run migrations (if any)
python -m app.core.database

# Start development server
uvicorn app.main:app --reload
```

### Frontend Setup

```
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

### Ollama Setup

```
# Install Ollama from https://ollama.ai

# Pull model
ollama pull gemma2:2b

# Verify
ollama list
```

---

## Project Structure

```
ai-data-quality-guardian/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   ├── core/              # Configuration
│   │   ├── models/            # Database models
│   │   ├── services/          # Business logic
│   │   └── main.py            # Entry point
│   ├── requirements.txt       # Python dependencies
│   └── .env                   # Environment variables
├── frontend/                  # React frontend
│   ├── src/
│   │   ├── components/        # Reusable components
│   │   ├── features/          # Feature modules
│   │   ├── services/          # API clients
│   │   └── App.jsx            # Root component
│   ├── package.json           # Node dependencies
│   └── tailwind.config.js     # Tailwind config
├── docs/                      # Documentation
├── README.md                  # Project README
└── CONTRIBUTING.md            # This file
```

---

## Making Changes

### 1. Create a Branch

```
# Update your fork
git fetch upstream
git checkout main
git merge upstream/main

# Create feature branch
git checkout -b feature/your-feature-name

# Or for bug fixes
git checkout -b fix/bug-description
```

**Branch Naming:**
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation
- `refactor/` - Code refactoring
- `test/` - Adding tests

### 2. Make Your Changes

- Follow [Coding Standards](#coding-standards)
- Write meaningful commit messages
- Add tests for new features
- Update documentation

### 3. Test Your Changes

```
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Manual testing
# - Test all affected features
# - Check browser console for errors
# - Verify API responses
```

---

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8

```
# Good 
def calculate_quality_score(
    completeness: float,
    consistency: float,
    accuracy: float,
    uniqueness: float
) -> float:
    """
    Calculate overall quality score.
    
    Args:
        completeness: Completeness score (0-100)
        consistency: Consistency score (0-100)
        accuracy: Accuracy score (0-100)
        uniqueness: Uniqueness score (0-100)
    
    Returns:
        Overall quality score (0-100)
    """
    weights = [0.3, 0.3, 0.2, 0.2]
    scores = [completeness, consistency, accuracy, uniqueness]
    return sum(w * s for w, s in zip(weights, scores))

# Bad 
def calc(a,b,c,d):
    return (a*0.3+b*0.3+c*0.2+d*0.2)
```

**Key Points:**
- Use type hints
- Write docstrings for functions/classes
- Max line length: 120 characters
- Use meaningful variable names
- Follow existing patterns

### JavaScript/React (Frontend)

**Style Guide:** Airbnb JavaScript Style Guide

```
// Good 
const QualityMetricsCard = ({ metrics }) => {
  const [expanded, setExpanded] = useState(false);
  
  const toggleExpand = useCallback(() => {
    setExpanded(prev => !prev);
  }, []);
  
  return (
    <div className="card">
      <h3 className="text-xl font-bold">{metrics.title}</h3>
      <button onClick={toggleExpand}>
        {expanded ? 'Collapse' : 'Expand'}
      </button>
    </div>
  );
};

// Bad 
function Card(props) {
  var show = false;
  
  function toggle() {
    show = !show;
  }
  
  return <div onClick={toggle}>{props.title}</div>;
}
```

**Key Points:**
- Use functional components + hooks
- Use `const` and `let`, not `var`
- Destructure props
- Use meaningful component names (PascalCase)
- Follow Tailwind CSS for styling

---

## Testing

### Writing Tests

**Backend (pytest):**

```
# tests/test_quality_engine.py
import pytest
from app.services.quality_engine.completeness import CompletenessAnalyzer

def test_completeness_with_no_missing_values():
    """Test completeness analyzer with complete data"""
    df = pd.DataFrame({
        'col1': ,[1][2]
        'col2': ['a', 'b', 'c']
    })
    
    analyzer = CompletenessAnalyzer()
    result = analyzer.analyze(df)
    
    assert result['completeness_score'] == 100.0
    assert result['missing_count'] == 0

def test_completeness_with_missing_values():
    """Test completeness analyzer with missing data"""
    df = pd.DataFrame({
        'col1': [1, None, 3],
        'col2': ['a', 'b', None]
    })
    
    analyzer = CompletenessAnalyzer()
    result = analyzer.analyze(df)
    
    assert result['missing_count'] == 2
    assert result['completeness_score'] < 100.0
```

**Frontend (Jest + React Testing Library):**

```
// tests/QualityMetricsCard.test.jsx
import { render, screen } from '@testing-library/react';
import QualityMetricsCard from './QualityMetricsCard';

test('renders quality metrics', () => {
  const metrics = {
    overall_score: 85.5,
    completeness_score: 90,
    consistency_score: 85,
    accuracy_score: 82,
    uniqueness_score: 85
  };
  
  render(<QualityMetricsCard metrics={metrics} />);
  
  expect(screen.getByText('85.5')).toBeInTheDocument();
  expect(screen.getByText('Completeness')).toBeInTheDocument();
});
```

### Running Tests

```
# Backend
cd backend
pytest tests/

# With coverage
pytest --cov=app tests/

# Frontend
cd frontend
npm test

# Watch mode
npm test -- --watch
```

---

## Submitting Changes

### 1. Commit Your Changes

```
git add .
git commit -m "feat: add database connection pooling"
```

**Commit Message Format:**

```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat` - New feature
- `fix` - Bug fix
- `docs` - Documentation
- `style` - Formatting, missing semicolons, etc.
- `refactor` - Code refactoring
- `test` - Adding tests
- `chore` - Maintenance

**Examples:**

```
# Good 
git commit -m "feat: add chat session isolation"
git commit -m "fix: resolve memory leak in model manager"
git commit -m "docs: update API documentation for dashboard endpoint"

# Bad 
git commit -m "fixed stuff"
git commit -m "WIP"
git commit -m "asdf"
```

### 2. Push to Your Fork

```
git push origin feature/your-feature-name
```

### 3. Create Pull Request

1. Go to your fork on GitHub
2. Click "Pull Request" button
3. Select your branch
4. Fill in PR template:

```
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Manual testing completed
- [ ] No console errors

## Screenshots (if applicable)
[Add screenshots for UI changes]

## Checklist
- [ ] Code follows project style
- [ ] Documentation updated
- [ ] Tests added/updated
- [ ] No breaking changes (or documented)
```

### 4. Code Review Process

- Maintainers will review your PR
- Address any feedback
- Make requested changes:

```
# Make changes
git add .
git commit -m "refactor: address review comments"
git push origin feature/your-feature-name
```

- Once approved, your PR will be merged! 

---

## Areas for Contribution

###  Good First Issues

Perfect for newcomers:

- Add more chart types to dashboard
- Improve error messages
- Add loading indicators
- Update documentation
- Fix typos
- Add unit tests

###  Intermediate

Requires some familiarity:

- Implement data validation rules
- Add database migration system
- Create Excel export functionality
- Improve anomaly detection algorithms
- Add email notifications
- Implement pagination

###  Advanced

For experienced contributors:

- Real-time monitoring system
- Multi-model LLM ensemble
- Auto-repair engine
- Distributed caching with Redis
- Kubernetes deployment configs
- Performance optimizations

### Priority Areas

1. **Testing** - More test coverage needed
2. **Documentation** - API docs, tutorials
3. **Performance** - Optimization opportunities
4. **Features** - See GitHub Issues for feature requests

---

## Development Tips

### Hot Reloading

Both backend and frontend support hot reloading:

```
# Backend auto-reloads on file changes
uvicorn app.main:app --reload

# Frontend auto-reloads on file changes
npm run dev
```

### Debugging

**Backend:**
```
# Add breakpoints
import pdb; pdb.set_trace()

# Or use logging
import logging
logger = logging.getLogger(__name__)
logger.debug("Debug message")
```

**Frontend:**
```
// Use React DevTools
// Add console logs
console.log('Debug:', variable);

// Use debugger
debugger;
```

### Database Migrations

When changing database models:

```
# Create migration (future: Alembic)
# For now, manually update database_models.py
# and restart server
```

---

## Documentation

### Adding Documentation

- API changes → Update `docs/api_documentation.md`
- Configuration changes → Update `docs/model_config.md` or `docs/chat_config.md`
- Architecture changes → Update `docs/architecture.md`
- User-facing features → Update `README.md`

### Documentation Style

- Use clear, concise language
- Include code examples
- Add screenshots for UI features
- Update table of contents

---

## Questions?

- **Email:** kamananand98@gmail.com
- **Discord:** [Join our community](https://discord.gg/...)
- **Issues:** [GitHub Issues](https://github.com/anandkaman/ai-data-quality/issues)

---

## License

By contributing, you agree that your contributions will be licensed under the same MIT License that covers the project.

---

## Recognition

Contributors will be:
-  Listed in `CONTRIBUTORS.md`
-  Mentioned in release notes
-  Credited in documentation

Thank you for contributing! in advance.

---
