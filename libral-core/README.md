# Libral Core - Privacy-First Microkernel Platform

**G-ACE.inc TGAXIS Libral Platform Core System**

## 🎯 Current Status: Week 1-2 Complete - Foundation Modules

Complete zero-based reconstruction using Python + FastAPI for optimal privacy-first architecture.

### ✅ Implemented Features (Week 1-2)

#### GPG Cryptographic Module (Week 1)
- **Modern Encryption**: SEIPDv2 + AES-256-OCB support
- **Context-Lock Signatures**: Operational security with audit context
- **Multi-Key Support**: RSA-4096, Ed25519, ECDSA-P256
- **WKD Integration**: Web Key Directory for automated key discovery
- **Encrypted Configuration**: .env.gpg support for secure secrets management
- **Privacy Compliance**: No personal data logging, 24h auto-deletion

#### Plugin Marketplace Module (Week 2)
- **Secure Plugin Discovery**: Multi-criteria search with privacy protection
- **GPG-Verified Installation**: Plugin signature verification using Week 1 GPG module
- **Sandboxed Execution**: Secure plugin environment with permission validation
- **Revenue Sharing**: Complete monetization framework for plugin developers
- **Plugin Lifecycle**: Install, enable, disable, uninstall with dependency management
- **Privacy-First**: Anonymous marketplace operations, local plugin registry

#### Authentication System (Week 3)
- **Telegram OAuth Integration**: Privacy-first authentication with HMAC verification
- **Personal Log Servers**: Revolutionary user data sovereignty in user-owned Telegram groups
- **GPG-Encrypted Sessions**: All tokens encrypted with Context-Lock signatures
- **Zero Personal Data Storage**: No PII stored on central servers
- **Complete User Control**: Users own 100% of their data with instant deletion capability
- **GDPR Compliance**: Full right to erasure, portability, and rectification

#### API Endpoints

**GPG Module (Week 1)**
```
GET  /health                       - System health check
GET  /api/v1/gpg/health           - GPG module status
POST /api/v1/gpg/encrypt          - Encrypt data with policy
POST /api/v1/gpg/decrypt          - Decrypt with context extraction  
POST /api/v1/gpg/sign             - Create Context-Lock signatures
POST /api/v1/gpg/verify           - Verify signatures and extract context
POST /api/v1/gpg/keys/generate    - Generate key pairs
GET  /api/v1/gpg/wkd-path         - Generate WKD paths
```

**Plugin Marketplace (Week 2)**
```
GET  /api/v1/marketplace/health              - Marketplace service status
GET  /api/v1/marketplace/search              - Search plugins with filtering
GET  /api/v1/marketplace/plugins/{id}        - Get plugin details
POST /api/v1/marketplace/plugins/{id}/install - Install plugin securely
DELETE /api/v1/marketplace/plugins/{id}      - Uninstall plugin
GET  /api/v1/marketplace/plugins/installed   - List installed plugins
POST /api/v1/marketplace/plugins/{id}/enable - Enable plugin
POST /api/v1/marketplace/plugins/{id}/disable - Disable plugin
GET  /api/v1/marketplace/categories          - List plugin categories
```

**Authentication System (Week 3)**
```
GET  /api/v1/auth/health                        - Service health & privacy compliance
POST /api/v1/auth/telegram                      - Telegram OAuth authentication
POST /api/v1/auth/personal-log-server/setup     - Personal log server creation
POST /api/v1/auth/token/refresh                 - GPG-encrypted token refresh
GET  /api/v1/auth/preferences                   - User preferences from personal server
POST /api/v1/auth/logout                        - Complete session invalidation
GET  /api/v1/auth/telegram/login-url            - Telegram OAuth URL generation
DELETE /api/v1/auth/user/data                   - GDPR Right to Erasure
```

## 🏗️ Architecture Overview

### Privacy-First Design Principles
1. **Data Sovereignty**: User data stored only in user-owned Telegram groups
2. **Zero Central Storage**: No personal information on central servers
3. **GPG Everything**: All sensitive data encrypted with GPG
4. **24h Auto-Delete**: Temporary cache automatically purged
5. **Audit Transparency**: Complete operation logging without personal data

### Technology Stack
- **Framework**: FastAPI (Python 3.11+)
- **Database**: PostgreSQL 15+ with SQLAlchemy 2.0
- **Cache**: Redis 7+ for sessions and temporary data
- **Cryptography**: python-gnupg with OpenPGP v6 support
- **Deployment**: Docker + Docker Compose
- **Logging**: Structured logging with privacy compliance

## 🚀 Quick Start

### Development Setup
```bash
# Clone and setup
git clone <repository>
cd libral-core

# Install dependencies (Python 3.11+ required)
pip install -r requirements.txt

# Copy configuration template
cp .env.example .env
# Edit .env with your configuration

# Run development server
python main.py
```

### Docker Deployment
```bash
# Full stack with PostgreSQL + Redis
docker-compose up -d

# Check health
curl http://localhost:8000/health
```

### GPG Setup
```bash
# Initialize GPG environment
mkdir -p ~/.gnupg
chmod 700 ~/.gnupg

# Generate system key (for development)
gpg --full-generate-key

# Set GPG_SYSTEM_KEY_ID in .env
```

## 📋 6-Week Development Roadmap

### ✅ Phase 1: Foundation (Week 1-3)
- **Week 1**: GPG Module ✅ **COMPLETED**
- **Week 2**: Plugin Marketplace ✅ **COMPLETED**  
- **Week 3**: Authentication System ✅ **COMPLETED**

### Phase 2: Communication & Integration (Week 4-5)  
- **Week 4**: Communication Gateway & Routing (Next)
- **Week 5**: Event Management & Real-time Systems

### Phase 3: Business Logic (Week 6-7)
- **Week 6**: Payments & Billing
- **Week 7**: API Hub & Module Integration

### Phase 4: AI Integration (Week 8)
- **Week 8**: Libral AI Agent Connection

## 🔐 Privacy Features

### Telegram Personal Log Servers
Revolutionary privacy model where user data is stored exclusively in user-owned Telegram supergroups:

1. **User Onboarding**: Guided setup for personal log group creation
2. **GPG Encryption**: All data encrypted before sending to user groups  
3. **Zero Access**: G-ACE.inc cannot access user's decrypted data
4. **User Control**: Complete data ownership and deletion rights

### Context-Lock Signatures
Advanced signature system with operational context:
```json
{
  "context_lock_version": "1.0",
  "labels": {
    "operation": "user_data_export",
    "timestamp": "2024-01-01T00:00:00Z",
    "user_consent": "explicit"
  }
}
```

## 🧪 Testing

```bash
# Run test suite
python -m pytest tests/ -v

# Test GPG operations
python -m pytest tests/test_gpg_module.py -v

# Privacy compliance tests
python -m pytest tests/ -k privacy -v
```

## 📚 API Documentation

Interactive API documentation available at:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`
- **OpenAPI JSON**: `http://localhost:8000/openapi.json`

## 🛡️ Security Considerations

### Development Environment
- Uses development keys and simplified configuration
- Mock implementations for external services
- Verbose logging for debugging

### Production Requirements
- GPG key management with secure passphrases
- Encrypted .env.gpg configuration files
- TLS/SSL for all communications
- Rate limiting and DDoS protection
- Regular security audits

## 📝 Configuration Reference

### Core Settings
```env
# Application
APP_NAME="Libral Core"
DEBUG=false
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql+asyncpg://user:pass@host/db

# GPG
GPG_HOME=/path/to/gpg/keyring
GPG_SYSTEM_KEY_ID=your-key-fingerprint

# Privacy
TEMP_CACHE_RETENTION_HOURS=24
USER_DATA_ENCRYPTION_REQUIRED=true
CENTRAL_LOGGING_DISABLED=true
```

## 🤝 Contributing

This is a private G-ACE.inc project implementing revolutionary privacy-first architecture. Contributions follow strict privacy compliance and zero-trust security principles.

## 📄 License

Proprietary - G-ACE.inc TGAXIS Libral Platform
All rights reserved.

---

**Latest Achievement**: Week 3 Authentication System with revolutionary personal log servers and complete user data sovereignty  
**Next Milestone**: Week 4 Communication Gateway with authenticated messaging and privacy-first routing.