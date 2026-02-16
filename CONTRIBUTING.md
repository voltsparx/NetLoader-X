# Contributing to NetLoader-X

Thank you for your interest in contributing to NetLoader-X! This document outlines how to contribute to the project.

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- `pip` (Python package manager)
- Git

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/voltsparx/NetLoader-X.git
cd NetLoader-X

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

---

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 2. Make Your Changes

- Keep changes focused and atomic
- Follow existing code style
- Add docstrings to new functions
- Add type hints where possible

### 3. Write Tests

Add tests for new features in `tests/test_all.py`:

```bash
# Run tests locally
pytest tests/test_all.py -v

# Check coverage
pytest tests/test_all.py --cov=core --cov=ui --cov=utils
```

All tests must pass before submitting.

### 4. Commit Your Changes

```bash
git add .
git commit -m "Description of changes"
```

Use clear commit messages:
- ✅ "Add chaos engineering fault injection"
- ✅ "Fix queue depth calculation bug"
- ❌ "Update stuff"

### 5. Push and Create Pull Request

```bash
git push origin feature/your-feature-name
```

Then create a pull request on GitHub.

---

## Code Style Guidelines

### Python Style

- Follow PEP 8 conventions
- Use 4 spaces for indentation
- Maximum line length: 100 characters
- Use descriptive variable names

### Documentation

- Add docstrings to all functions
- Include type hints for parameters
- Document complex algorithms

Example:
```python
def calculate_latency(queue_depth: int, base_latency: float) -> float:
    """
    Calculate adjusted latency based on queue depth.
    
    Args:
        queue_depth: Current number of queued requests
        base_latency: Base latency in milliseconds
        
    Returns:
        Adjusted latency in milliseconds
    """
    return base_latency * (1 + queue_depth / 100)
```

### Comments

- Explain "why", not "what"
- Use clear, concise language
- Update comments when code changes

---

## Areas for Contribution

### 🐛 Bug Fixes

Found a bug? Please:
1. Check existing issues to avoid duplicates
2. Create an issue with:
   - Clear description
   - Steps to reproduce
   - Expected vs actual behavior
   - Python version and OS

### ✨ New Features

Feature ideas are welcome! Please:
1. Open an issue first to discuss
2. Explain the use case
3. Consider impact on security
4. Discuss implementation approach

### 📚 Documentation

Help improve documentation by:
- Fixing typos
- Clarifying explanations
- Adding examples
- Improving tutorials

### 🧪 Tests

Increase test coverage by:
- Adding tests for existing code
- Testing edge cases
- Testing error conditions
- Adding integration tests

---

## Security Considerations

All contributions must maintain security:

✅ **Required**
- No external network I/O
- No eval() or exec() usage
- Input validation for all user input
- Thread-safe concurrent access
- Hard safety caps on operations

❌ **Not Allowed**
- Code that bypasses safety limits
- External API calls
- Privileged operations
- Unsafe file operations

See [SECURITY.md](SECURITY.md) for detailed security guidelines.

---

## Testing Requirements

### Running Tests

```bash
# All tests
pytest tests/test_all.py -v

# Specific test class
pytest tests/test_all.py::TestMetricsCollector -v

# With coverage report
pytest tests/test_all.py --cov=core --cov=ui --cov=utils --cov-report=html
```

### Test Coverage Targets

- Core simulation: 95%+
- Safety limits: 100%
- Metrics: 100%
- Configuration: 95%
- CLI: 90%

---

## Documentation Updates

When making changes, update relevant documentation:

### README.md
- Adding new features? Update the feature table
- Adding new CLI commands? Document them in Usage Modes
- Changing behavior? Update examples

### SECURITY.md
- Changes to security model
- New safety limits
- Security improvements

### Docstrings
- Function docstrings
- Module docstrings
- Complex algorithm explanations

---

## Pull Request Process

1. **Before submitting:**
   - All tests pass (`pytest tests/test_all.py`)
   - Code follows style guidelines
   - Documentation is updated
   - No new security vulnerabilities introduced

2. **PR Description:**
   - What does this PR do?
   - Why is this change needed?
   - How does it work?
   - Any breaking changes?

3. **PR Template:**
   ```markdown
   ## Description
   Brief description of changes
   
   ## Type of Change
   - [ ] Bug fix
   - [ ] New feature
   - [ ] Documentation
   - [ ] Performance improvement
   
   ## Testing
   How to test these changes:
   - [ ] Test 1
   - [ ] Test 2
   
   ## Checklist
   - [ ] Tests pass
   - [ ] Documentation updated
   - [ ] No security issues
   - [ ] Code follows style guidelines
   ```

---

## Review Process

1. Code review will check:
   - Code quality and style
   - Test coverage
   - Documentation completeness
   - Security implications
   - Backward compatibility

2. Feedback will be provided as comments
3. Address feedback and push updates
4. Once approved, PR will be merged

---

## Release Process

Releases follow semantic versioning (MAJOR.MINOR.PATCH):

- **MAJOR**: Breaking changes
- **MINOR**: New features (backward compatible)
- **PATCH**: Bug fixes

Example: v1.0.0 → v1.1.0 (new feature) → v1.1.1 (bug fix)

---

## Community Guidelines

### Be Respectful
- Treat everyone with respect
- Constructive criticism only
- No harassment or discrimination

### Be Collaborative
- Help others understand your changes
- Review others' PRs fairly
- Share knowledge generously

### Ask Questions
- Unclear? Ask in the PR comments
- Need help? Open a discussion issue
- Provide context in your questions

---

## Getting Help

### Questions About Contributing
- Check existing issues and discussions
- Open a new discussion
- Comment on relevant issues

### Technical Questions
- Check [README.md](README.md) for usage
- Check [SECURITY.md](SECURITY.md) for security
- Review existing code for examples

### Reporting Issues
- Use GitHub Issues
- Include:
  - Python version
  - OS and version
  - Clear reproduction steps
  - Error messages/logs

---

## Acknowledgments

Contributors are listed in the project. All contributions, no matter how small, are appreciated!

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project (see LICENSE file).

---

Thank you for contributing to NetLoader-X! 🙏
