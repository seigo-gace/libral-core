# Libral Core - Privacy-First Microkernel Platform

**G-ACE.inc TGAXIS Libral Platform Core System**

## 🎯 Current Status: Week 1 - GPG Module Implementation

Complete zero-based reconstruction using Python + FastAPI for optimal privacy-first architecture.

### ✅ Implemented Features (Week 1)

#### GPG Cryptographic Module
- **Modern Encryption**: SEIPDv2 + AES-256-OCB support
- **Context-Lock Signatures**: Operational security with audit context
- **Multi-Key Support**: RSA-4096, Ed25519, ECDSA-P256
- **WKD Integration**: Web Key Directory for automated key discovery
- **Encrypted Configuration**: .env.gpg support for secure secrets management
- **Privacy Compliance**: No personal data logging, 24h auto-deletion

#### API Endpoints
```
GET  /health                    - System health check
GET  /api/v1/gpg/health        - GPG module status
POST /api/v1/gpg/encrypt       - Encrypt data with policy
POST /api/v1/gpg/decrypt       - Decrypt with context extraction  
POST /api/v1/gpg/sign          - Create Context-Lock signatures
POST /api/v1/gpg/verify        - Verify signatures and extract context
POST /api/v1/gpg/keys/generate - Generate key pairs
GET  /api/v1/gpg/wkd-path      - Generate WKD paths
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

### ✅ Phase 1: Foundation (Week 1-2)
- **Week 1**: GPG Module ✅ **COMPLETED**
- **Week 2**: Authentication & User Management (Next)

### Phase 2: Communication (Week 3-4)  
- **Week 3**: Communication Gateway & Routing
- **Week 4**: Notification & Event Management

### Phase 3: Business Logic (Week 5-6)
- **Week 5**: Payments & Billing
- **Week 6**: API Hub & Module Integration

### Phase 4: AI Integration (Week 7-8)
- **Week 7-8**: Libral AI Agent Connection

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

**Next Milestone**: Week 2 Authentication Module with Telegram OAuth integration and user personal log server setup.