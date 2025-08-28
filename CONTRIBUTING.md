# Contributing to Libral Core

Thank you for your interest in contributing to Libral Core! This document provides guidelines for contributing to our privacy-first microkernel platform.

## 🔐 Security First

Libral Core implements enterprise-grade security and privacy features. All contributions must maintain our security standards:

- **No Sensitive Data**: Never commit API keys, passwords, or personal information
- **Privacy Compliance**: Follow GDPR principles and user data sovereignty
- **Cryptographic Standards**: Maintain enterprise-grade encryption (AES-256, SHA-256)
- **Security Review**: All cryptographic changes require security review

## 🏗️ Architecture Overview

### Component Structure
```
├── client/                 # React frontend with TypeScript
├── server/                 # Node.js Express API
├── shared/                 # Shared schemas and types
├── libral-core/           # Python FastAPI advanced features
│   ├── modules/           # GPG, Auth, Marketplace, etc.
│   └── library/           # Utility layer (string, datetime, API)
└── tests/                 # Test suites
```

### Key Principles
1. **Privacy-First**: User data sovereignty via Telegram personal servers
2. **Microkernel Design**: Hot-swappable, modular components
3. **Type Safety**: Full TypeScript/Python typing
4. **Real-time Updates**: WebSocket-based live monitoring
5. **Zero Central Storage**: No user data stored centrally

## 🚀 Development Setup

### Prerequisites
- Node.js 20+
- Python 3.11+
- PostgreSQL
- Git

### Local Development
```bash
# Clone the repository
git clone [repository-url]
cd libral-core-project

# Install dependencies
npm install
cd libral-core && pip install -e .

# Start development server
npm run dev
```

## 📝 Code Style Guidelines

### Frontend (React/TypeScript)
- Use functional components with hooks
- Implement proper error boundaries
- Follow shadcn/ui component patterns
- Maintain accessibility standards
- Add `data-testid` for testing

### Backend (Node.js/Express)
- Use TypeScript with strict typing
- Implement proper error handling
- Follow RESTful API conventions
- Use Drizzle ORM for database operations
- Add comprehensive logging

### Python Modules
- Follow PEP 8 style guidelines
- Use Pydantic V2 for data validation
- Implement async/await patterns
- Add comprehensive docstrings
- Use structured logging (structlog)

### GPG/Security Code
- Never expose private keys or sensitive data
- Use secure random generation
- Implement proper key management
- Add audit logging for all operations
- Follow FIPS 140-2 guidelines where applicable

## 🧪 Testing Requirements

### Test Coverage
- **Frontend**: Component tests with React Testing Library
- **Backend**: API endpoint tests with supertest
- **Python**: pytest with async support
- **GPG Module**: Mock-based testing (no real keys)

### Running Tests
```bash
# Frontend tests
npm test

# Backend tests
npm run test:backend

# Python module tests
cd libral-core && python -m pytest

# GPG module tests (mock environment)
cd libral-core && python -m pytest tests/test_gpg_module.py
```

## 🔄 Pull Request Process

### Before Submitting
1. **Test Coverage**: Ensure all new code has appropriate tests
2. **Type Safety**: Fix all TypeScript/Python type errors
3. **Security Review**: Check for sensitive data exposure
4. **Performance**: Verify no significant performance regression
5. **Documentation**: Update relevant documentation

### PR Requirements
- [ ] Clear description of changes
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Security implications addressed
- [ ] Performance impact assessed
- [ ] Breaking changes documented

### PR Template
```markdown
## Summary
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update
- [ ] Security enhancement

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Manual testing completed

## Security Checklist
- [ ] No sensitive data exposed
- [ ] Cryptographic standards maintained
- [ ] Privacy compliance verified
- [ ] Audit logging implemented
```

## 📊 Component-Specific Guidelines

### GPG Module
- All operations must support Context-Lock signatures
- Maintain 3 encryption policies (Modern Strong, Compat, Backup Longterm)
- Never log sensitive cryptographic data
- Use mock GPG for testing
- Implement proper key lifecycle management

### Library Module
- Utilities must be stateless and pure
- Performance critical: <20ms for 1000 operations
- Security focused: XSS protection, input sanitization
- Full test coverage required
- Comprehensive error handling

### Frontend Dashboard
- Real-time updates via WebSocket
- Responsive design (mobile-first)
- Accessibility compliance (WCAG 2.1)
- Dark/light theme support
- Error boundaries and loading states

### Backend API
- RESTful design with proper HTTP codes
- Comprehensive error handling
- Rate limiting for security
- Audit logging for all operations
- Database transactions for data integrity

## 🔒 Security Guidelines

### Cryptographic Operations
- Use only approved algorithms (AES-256, SHA-256, RSA4096, ED25519, ECDSA-P256)
- Implement proper key derivation (PBKDF2, scrypt, Argon2)
- Use secure random number generation
- Never store private keys unencrypted
- Implement proper session management

### Data Handling
- Minimize data collection
- Encrypt sensitive data at rest
- Use HTTPS for all communications
- Implement proper input validation
- Follow principle of least privilege

### Privacy Features
- Support user data portability
- Implement right to erasure
- Use privacy-by-design principles
- Support Telegram personal log servers
- Never track users without consent

## 🐛 Bug Reports

When reporting bugs, please include:
- **Component**: Which part of the system
- **Environment**: OS, browser, versions
- **Steps**: How to reproduce
- **Expected**: What should happen
- **Actual**: What actually happened
- **Privacy Impact**: Any data exposure concerns
- **Security Impact**: Any security implications

## 🌟 Feature Requests

For new features, consider:
- **Privacy Impact**: How does it affect user privacy?
- **Security**: Any new attack vectors?
- **Performance**: Impact on system performance
- **Complexity**: Implementation difficulty
- **User Value**: Benefit to end users

## 📚 Documentation Standards

### Code Documentation
- JSDoc for TypeScript functions
- Docstrings for Python functions
- README files for major components
- API documentation with examples
- Architecture decision records (ADRs)

### User Documentation
- Clear installation instructions
- Configuration examples
- API reference with examples
- Security best practices
- Privacy feature explanations

## ⚡ Performance Guidelines

### Frontend Performance
- Code splitting for large components
- Lazy loading for routes
- Optimized bundle sizes
- Efficient re-rendering patterns
- WebSocket connection management

### Backend Performance
- Database query optimization
- Proper indexing strategies
- Connection pooling
- Caching strategies
- Rate limiting implementation

### Python Module Performance
- Async/await for I/O operations
- Efficient data structures
- Memory management
- Connection reuse
- Background task processing

## 🤝 Community

### Communication
- Be respectful and inclusive
- Focus on technical merit
- Provide constructive feedback
- Help newcomers understand the codebase
- Maintain professional standards

### Code Review
- Review for security implications
- Check for privacy compliance
- Verify test coverage
- Ensure documentation updates
- Provide specific, actionable feedback

## 📄 License

By contributing to Libral Core, you agree that your contributions will be licensed under the same license as the project.

---

Thank you for contributing to Libral Core! Together, we're building the future of privacy-first computing. 🔐✨