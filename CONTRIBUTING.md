# Contributing to Harambee DAO Backend

Thank you for your interest in contributing to Harambee DAO! This document provides guidelines and information for contributors.

## 🎯 **Mission**

Harambee DAO aims to stop embezzlement in community savings groups by releasing funds only after verifiable, AI-verified project milestones — with accessible SMS voting for all members.

## 🤝 **How to Contribute**

### 1. **Getting Started**

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Harambee-Dao-Backend.git
   cd Harambee-Dao-Backend
   ```
3. **Set up development environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   pip install -e .[dev]
   ```
4. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

### 2. **Development Guidelines**

#### Code Style
- Follow **PEP 8** Python style guidelines
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public functions and classes
- Keep line length under **100 characters**
- Use **meaningful variable and function names**

#### Code Quality
- **100% test coverage** is required for all new code
- Write **comprehensive tests** for new features
- Include **integration tests** for API endpoints
- Use **pytest** for all testing
- Run **linting** before submitting: `ruff check app/`

#### Commit Messages
Use **conventional commit** format:
```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Examples:
```
feat(sms): add vote parsing for SMS webhooks
fix(kyc): resolve document verification bug
docs(api): update endpoint documentation
test(user): add member registration tests
```

### 3. **Testing Requirements**

#### Running Tests
```bash
# Run all tests
pytest -v

# Run specific test file
pytest tests/test_user_management.py -v

# Run with coverage
pytest --cov=app --cov-report term-missing --cov-report html
```

#### Test Coverage
- **100% coverage** is enforced for all new code
- Tests must cover **happy path** and **error cases**
- Include **edge cases** and **boundary conditions**
- Mock external dependencies (Twilio, IPFS, etc.)

#### Test Categories
1. **Unit Tests**: Test individual functions and classes
2. **Integration Tests**: Test API endpoints end-to-end
3. **Service Tests**: Test business logic in service layer
4. **Utility Tests**: Test utility functions and helpers

### 4. **Pull Request Process**

#### Before Submitting
1. **Run all tests** and ensure they pass
2. **Check test coverage** meets 100% requirement
3. **Run linting** and fix any issues
4. **Update documentation** if needed
5. **Test manually** with the development server

#### PR Requirements
- **Clear title** describing the change
- **Detailed description** of what was changed and why
- **Link to related issues** if applicable
- **Screenshots** for UI changes (if any)
- **Breaking changes** clearly documented

#### PR Template
```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Test coverage maintained at 100%

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] No breaking changes (or clearly documented)
```

## 🏗️ **Architecture Guidelines**

### Service Layer Pattern
- **Services** contain business logic
- **API routes** handle HTTP concerns only
- **Models** define data structures
- **Utils** provide reusable utilities

### Error Handling
- Use **HTTPException** for API errors
- Include **meaningful error messages**
- Log errors appropriately
- Handle **edge cases** gracefully

### Security Considerations
- **Validate all inputs** using Pydantic
- **Rate limit** sensitive endpoints
- **Sanitize** user-provided data
- **Never log** sensitive information

## 📚 **Documentation**

### API Documentation
- Use **FastAPI automatic docs** (`/docs` endpoint)
- Include **example requests/responses**
- Document **error codes** and messages
- Keep **schemas** up to date

### Code Documentation
- Write **clear docstrings** for all public functions
- Include **parameter descriptions** and **return types**
- Document **complex algorithms** and **business logic**
- Update **README** for significant changes

## 🐛 **Bug Reports**

### Before Reporting
1. **Search existing issues** to avoid duplicates
2. **Test with latest version** of the code
3. **Reproduce the bug** consistently
4. **Gather relevant information** (logs, environment, etc.)

### Bug Report Template
```markdown
## Bug Description
Clear description of the bug

## Steps to Reproduce
1. Step one
2. Step two
3. Step three

## Expected Behavior
What should happen

## Actual Behavior
What actually happens

## Environment
- Python version:
- FastAPI version:
- OS:
- Other relevant info:

## Additional Context
Any other relevant information
```

## 💡 **Feature Requests**

### Before Requesting
1. **Check existing issues** and discussions
2. **Consider the scope** and alignment with project goals
3. **Think about implementation** complexity
4. **Consider backwards compatibility**

### Feature Request Template
```markdown
## Feature Description
Clear description of the proposed feature

## Problem Statement
What problem does this solve?

## Proposed Solution
How should this be implemented?

## Alternatives Considered
Other approaches considered

## Additional Context
Any other relevant information
```

## 🔒 **Security**

### Reporting Security Issues
- **Do not** create public issues for security vulnerabilities
- **Email** security concerns to the maintainers
- **Include** detailed information about the vulnerability
- **Allow time** for the issue to be addressed before disclosure

### Security Guidelines
- **Never commit** secrets or API keys
- **Use environment variables** for sensitive configuration
- **Validate and sanitize** all user inputs
- **Follow security best practices** for authentication and authorization

## 📞 **Getting Help**

### Resources
- **Documentation**: [User Management Guide](USER_MANAGEMENT_README.md)
- **API Reference**: Available at `/docs` when running the server
- **Issues**: [GitHub Issues](https://github.com/Harambee-Dao/Harambee-Dao-Backend/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Harambee-Dao/Harambee-Dao-Backend/discussions)

### Community Guidelines
- **Be respectful** and inclusive
- **Help others** learn and contribute
- **Share knowledge** and best practices
- **Collaborate** constructively

## 🙏 **Recognition**

Contributors will be recognized in:
- **README** acknowledgments
- **Release notes** for significant contributions
- **Project documentation**

Thank you for contributing to Harambee DAO and helping build financial inclusion tools for communities worldwide! 🌍
