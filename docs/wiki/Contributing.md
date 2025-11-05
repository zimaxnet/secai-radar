# Contributing to SecAI Radar

Thank you for your interest in contributing to SecAI Radar! This guide will help you get started.

---

## How to Contribute

### Reporting Bugs

1. **Check Existing Issues**: Search existing issues first
2. **Create New Issue**: Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Screenshots (if applicable)
   - Environment details (browser, OS, etc.)

### Requesting Features

1. **Check Existing Issues**: Search for similar feature requests
2. **Create Feature Request**: Include:
   - Clear description of the feature
   - Use case / problem it solves
   - Proposed solution (if any)
   - Examples (if applicable)

### Contributing Code

1. **Fork Repository**: Fork the repository on GitHub
2. **Create Branch**: Create a feature branch
3. **Make Changes**: Follow coding standards
4. **Test Changes**: Ensure all tests pass
5. **Submit PR**: Create pull request with description

---

## Development Setup

### Prerequisites

- Node.js 20+ (for web UI)
- Python 3.12+ (for API)
- Docker (optional, for containerized deployment)
- Git

### Local Development

1. **Clone Repository**:
   ```bash
   git clone https://github.com/your-org/secai-radar.git
   cd secai-radar
   ```

2. **Set Up Web UI**:
   ```bash
   cd web
   npm install
   npm run dev
   ```

3. **Set Up API**:
   ```bash
   cd api
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   func start
   ```

4. **Set Up Configuration**:
   - Copy `config/models.yaml.example` to `config/models.yaml`
   - Configure environment variables
   - Set up Azure credentials (if needed)

---

## Coding Standards

### Code Style

- **Python**: Follow PEP 8
- **TypeScript**: Follow ESLint rules
- **Markdown**: Follow standard markdown conventions

### Documentation

- Document all public APIs
- Include docstrings for functions/classes
- Update README files as needed
- Keep documentation up to date

### Testing

- Write tests for new features
- Ensure all tests pass
- Maintain test coverage
- Test edge cases

### Git Conventions

- **Commit Messages**: Clear, descriptive commit messages
- **Branch Names**: `feature/description` or `fix/description`
- **PR Titles**: Clear description of changes

---

## Project Structure

```
secai-radar/
  api/              # Azure Functions API
  web/              # React web UI
  src/              # Source code
    models/         # Model layer
    orchestrator/   # Orchestration layer
    collectors/     # Collectors
    normalizers/    # Normalizers
    rag/            # RAG layer
    report/         # Report generation
  config/           # Configuration files
  docs/             # Documentation
    wiki/           # Wiki documentation
  seeds/            # Seed data
```

---

## Architecture Principles

### Vendor-Agnostic

- **No hardcoded customer names**
- **No hardcoded vendor names**
- **No hardcoded consulting firm names**
- Use generic identifiers (e.g., `tenant-alpha`, `subscription-001`)

### Role-Based Models

- Models defined by **role**, not brand
- Configuration via `config/models.yaml`
- Swappable model providers

### Data Layer Separation

- **Bronze**: Raw evidence (immutable)
- **Silver**: Normalized data (queryable)
- **Gold/RAG**: Embedded chunks (searchable)

See [Architecture](/wiki/Architecture) for details.

---

## Areas for Contribution

### Features

- **Collectors**: Implement new cloud collectors
- **Normalizers**: Add normalizers for new resource types
- **UI Components**: Improve UI/UX
- **Report Templates**: Add new report formats
- **API Endpoints**: Add new API endpoints

### Documentation

- **User Guides**: Improve user documentation
- **API Docs**: Enhance API documentation
- **Examples**: Add code examples
- **Tutorials**: Create tutorials

### Testing

- **Unit Tests**: Add unit tests
- **Integration Tests**: Add integration tests
- **E2E Tests**: Add end-to-end tests
- **Test Coverage**: Improve test coverage

### Bug Fixes

- **UI Bugs**: Fix UI issues
- **API Bugs**: Fix API issues
- **Data Issues**: Fix data processing issues
- **Performance**: Improve performance

---

## Pull Request Process

### Before Submitting

1. **Update Documentation**: Update relevant docs
2. **Add Tests**: Include tests for new features
3. **Run Tests**: Ensure all tests pass
4. **Check Linting**: Fix linting errors
5. **Update Changelog**: Add entry to changelog (if applicable)

### PR Description

Include:
- **Summary**: Brief description of changes
- **Motivation**: Why this change is needed
- **Changes**: What changed
- **Testing**: How to test
- **Screenshots**: If UI changes

### Review Process

1. **Automated Checks**: CI/CD checks must pass
2. **Code Review**: At least one reviewer approval
3. **Discussion**: Address review comments
4. **Merge**: Maintainer merges PR

---

## Code of Conduct

### Be Respectful

- Be respectful to all contributors
- Accept constructive criticism
- Help others learn and grow

### Be Professional

- Keep discussions professional
- Focus on code, not people
- Be open to different perspectives

### Be Inclusive

- Welcome newcomers
- Encourage questions
- Provide helpful feedback

---

## Getting Help

### Questions

- **Documentation**: Check wiki and docs
- **Issues**: Search existing issues
- **Discussions**: Use GitHub Discussions
- **Community**: Engage with community

### Stuck?

- **Read Docs**: Start with documentation
- **Ask Questions**: Don't hesitate to ask
- **Get Feedback**: Share your work early

---

## Recognition

Contributors will be:
- Listed in CONTRIBUTORS.md
- Acknowledged in release notes
- Thanked in project documentation

---

## License

By contributing, you agree that your contributions will be licensed under the same license as the project.

---

**Thank you for contributing to SecAI Radar!** 🎉

---

**Related**: [Architecture](/wiki/Architecture) | [Getting Started](/wiki/Getting-Started)

