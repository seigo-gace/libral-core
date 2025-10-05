# Overview

Libral Core is a privacy-first microkernel platform designed for enterprise-grade cryptographic operations and user data sovereignty. The system implements a revolutionary architecture where user data is never centrally stored, instead utilizing Telegram personal log servers to give users complete control over their information. The platform features enterprise GPG encryption (Aegis-PGP), a hot-swappable plugin marketplace, and a sophisticated multi-transport communication system with intelligent failover capabilities.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Design Principles

### Privacy-First Architecture
The system is built on a zero-central-storage model where user data sovereignty is paramount. All user data is encrypted using enterprise-grade GPG and stored in user-controlled Telegram personal log servers, ensuring users maintain complete ownership and control of their information. No personal data is retained on central Libral servers.

### Microkernel Design Pattern
The platform implements a modular, hot-swappable component architecture where core functionality is isolated into independent modules. This allows runtime loading/unloading of components without system downtime, supporting continuous deployment and flexible feature evolution.

### Hybrid Technology Stack
- **Backend Core**: Node.js/Express with TypeScript for RESTful API services and WebSocket real-time communication
- **Advanced Modules**: Python/FastAPI for cryptographic operations, AI processing, and complex data workflows
- **Frontend**: React with TypeScript, Vite build system, and Shadcn/UI component library
- **Database**: PostgreSQL with Drizzle ORM for type-safe database operations
- **Caching/PubSub**: Redis for real-time event distribution and session management

## Key Architectural Components

### 1. Aegis-PGP Cryptography Module (Python/FastAPI)
Enterprise-grade GPG operations implementing three encryption policies:
- **Modern Strong**: SEIPDv2 + AES-256-OCB for maximum security
- **Compatibility**: Standard OpenPGP for broad interoperability
- **Backup Longterm**: Long-term archival with future-proof algorithms

Features Context-Lock signatures for privacy-aware cryptographic operations, supports RSA-4096, ED25519, and ECDSA-P256 key types, and includes WKD (Web Key Directory) integration for automated key discovery.

### 2. Multi-Transport Communication System
Intelligent message routing with automatic failover across multiple channels:
- **Telegram**: Primary transport with topic/hashtag support
- **Email**: SMTP-based delivery for external recipients
- **Webhook**: HTTP callbacks for third-party integrations

The transport layer implements health checking, priority-based routing, and encrypted payload delivery using the Aegis-PGP module.

### 3. Personal Log Server System
Revolutionary user data sovereignty implementation using Telegram Supergroups:
- Users create and own their personal Telegram groups where all their activity logs are stored
- All logs are GPG-encrypted before transmission
- Users control data retention policies (1-365 days auto-delete)
- Perfect topic organization with hashtag filtering for log categorization
- Zero central storage - Libral servers never retain decrypted user data

### 4. Module Registry & Hot-Swapping
Dynamic module management system allowing runtime registration and discovery:
- Module health monitoring and status reporting
- Capability-based routing for feature discovery
- Independent lifecycle management per module
- Version-aware API compatibility

### 5. Database Schema Architecture
Type-safe PostgreSQL schema using Drizzle ORM with the following core entities:
- **Users**: Telegram-based authentication with role management (user/creator/streamer/admin)
- **Transactions**: Payment processing with Telegram Stars integration
- **Events**: Comprehensive audit logging with type/source categorization
- **Modules**: Module registry with health check tracking
- **Stamps**: Creative asset management for sticker creation
- **System Metrics**: Performance monitoring and resource tracking

### 6. Real-Time WebSocket System
Event-driven updates using Redis pub/sub for live dashboard monitoring:
- System metrics broadcasting
- Module status changes
- Transaction updates
- User activity notifications

### 7. Payment Integration Layer
Multi-provider payment processing:
- **Telegram Stars**: Native Telegram in-app purchases
- **PayPal**: International payment support
- **Stripe**: Credit card processing (future expansion)

All payment transactions are logged to user personal log servers with GPG encryption.

## Security & Privacy Controls

### Cryptographic Standards
- AES-256-OCB for symmetric encryption
- SHA-256/SHA-512 for cryptographic hashing
- RSA-4096, ED25519, ECDSA-P256 for asymmetric operations
- HMAC-SHA256 for webhook signature verification

### Input Validation & Sanitization
- Comprehensive XSS protection using string processing utilities
- SQL injection prevention through parameterized queries
- Rate limiting on API endpoints
- Content-Security-Policy headers enforcement

### Audit & Compliance
- Complete operation tracking via event logging
- GDPR-compliant privacy-by-design implementation
- Encrypted audit trails for sensitive operations
- User data export/deletion capabilities

## SelfEvolution Autonomous System (Implemented: 2025-10-05)

### Libral SelfEvolution Final Manifest V1

Revolutionary autonomous system with 4 integrated modules enabling self-healing, collective intelligence, and autonomous evolution:

#### LPO (Libral Protocol Optimizer) - Port 8000
Single autonomous monitoring system integrating AMM/CRAD:
- **Health Score Calculator**: 0-100 system health metrics with weighted scoring
- **ZK Audit Gateway**: Zero-knowledge proof-based security auditing
- **Self-Healing AI**: CRAD recovery analysis with dynamic remediation suggestions
- **Finance Optimizer**: External AI cost tracking, plugin revenue auditing, predictive cost limits
- **RBAC Abstraction**: Role-based access control with IRBACProvider interface
- **Predictive Monitor**: Z-score based anomaly detection with 30-sample moving average

API Endpoints: `/lpo/dashboard`, `/lpo/metrics/health-score`, `/lpo/zk-audit/*`, `/lpo/self-healing/*`, `/lpo/finance/*`, `/lpo/rbac/*`, `/lpo/predictive/*`

#### KBE (Knowledge Booster Engine) - Port 8000
Privacy-first collective intelligence system:
- **Federated Learning Interface**: Local AI training with parameter-only sharing
- **Homomorphic Aggregator**: Encrypted model aggregation without decryption
- **Knowledge Collection**: Privacy-preserving knowledge submission with anonymization

API Endpoints: `/kbe/dashboard`, `/kbe/submit-knowledge`, `/kbe/federated/*`, `/kbe/homomorphic/*`

#### AEG (Auto Evolution Gateway) - Port 8000
Autonomous platform evolution system:
- **Development Prioritization AI**: Health score + MTTR statistics-based priority scoring
- **GitHub PR Generator**: Automated pull request creation for code improvements
- **Evolution Task Management**: Automatic task creation and tracking

API Endpoints: `/aeg/dashboard`, `/aeg/analyze-and-prioritize`, `/aeg/top-priorities`, `/aeg/pr/*`

#### Vaporization Protocol - Port 8000
Privacy-first cache management with guaranteed data deletion:
- **Redis TTL Enforcer**: Automatic 24-hour maximum retention for all personal data patterns
- **KBE Flush Hook**: Immediate cache deletion after knowledge extraction
- **Pattern Protection**: `user:*`, `session:*`, `personal:*`, `telegram:*:data`, `kbe:knowledge:*`

API Endpoints: `/vaporization/dashboard`, `/vaporization/ttl/*`, `/vaporization/flush/*`

#### Integration Layer
Unified coordination across all SelfEvolution modules:
- **Unified Dashboard**: `/selfevolution/dashboard` - Real-time status of all modules
- **Execution Cycle**: `/selfevolution/execute-cycle` - Orchestrated self-evolution workflow
- **Module Health**: `/selfevolution/module-health` - Individual module status checks
- **Manifest**: `/selfevolution/manifest` - Complete SelfEvolution capabilities documentation

**Privacy Guarantees:**
1. Zero central storage of personal data
2. Maximum 24-hour cache retention enforced
3. Immediate flush after knowledge extraction
4. Federated learning with local AI training only
5. Homomorphic encryption for model aggregation
6. Zero-knowledge proofs for privacy-preserving verification

**Autonomous Capabilities:**
1. Self-healing based on CRAD recovery analysis
2. Automatic priority determination from health metrics
3. AI-driven code improvement suggestions
4. GitHub PR generation for evolution tasks
5. Finance optimization with cost tracking
6. Predictive anomaly detection with z-score analysis

## Development & Deployment Structure

### PCGP V1.0 Organization (Professional Grooming Protocol)
- `src/`: Source code for all components
- `docs/`: Documentation including deployment and security policies
- `infra/`: Infrastructure configuration (Docker, Vite, Tailwind, Drizzle)
- `policies/`: Governance rules and compliance definitions
- `archive/`: Legacy code and completion reports

### CI/CD Pipeline
GitHub Actions workflow implementing:
- Frontend/backend/Python module testing
- Security scanning with Semgrep
- Automated deployment to Replit
- Type checking and linting

### Environment Configuration
Configuration managed through Pydantic Settings (Python) and environment variables (Node.js):
- Database connection strings
- Redis URLs
- Telegram Bot tokens
- GPG key management
- Payment provider credentials

All sensitive credentials are GPG-encrypted and never committed to version control.

# External Dependencies

## Third-Party Services

### Telegram Bot API
Primary communication platform and authentication provider. Used for:
- OAuth 2.0 user authentication
- Personal log server implementation (Telegram Supergroups)
- In-app payments via Telegram Stars
- Message delivery and webhook processing

Configuration: `TELEGRAM_BOT_TOKEN`, `TELEGRAM_WEBHOOK_SECRET`

### Database: PostgreSQL (Neon)
Serverless PostgreSQL via `@neondatabase/serverless` with WebSocket connection support. Used for persistent storage of users, transactions, events, modules, and system metrics.

Configuration: `DATABASE_URL`

### Cache & Message Queue: Redis
Real-time pub/sub messaging and session management. Implements WebSocket event broadcasting and module health coordination.

Configuration: Redis URL (default: `redis://localhost:6379/0`)

### Payment Providers
- **Telegram Stars**: Native in-app payment processing
- **PayPal Server SDK** (`@paypal/paypal-server-sdk`): International payment support

Configuration: `STRIPE_SECRET_KEY`, `PAYPAL_CLIENT_ID`, `PAYPAL_CLIENT_SECRET`

## Core NPM Dependencies

### Backend Framework
- `express`: RESTful API server
- `drizzle-orm`: Type-safe database ORM
- `ws`: WebSocket server implementation
- `connect-pg-simple`: PostgreSQL session store

### Frontend Framework
- `react`, `react-dom`: UI framework
- `@tanstack/react-query`: Server state management
- `wouter`: Lightweight routing
- `vite`: Frontend build system

### UI Component Library
Radix UI primitives (`@radix-ui/*`) with Tailwind CSS:
- Accordion, Dialog, Dropdown, Toast, Tooltip, and 15+ other accessible components
- `shadcn/ui`: Pre-built component patterns
- `class-variance-authority`: Type-safe styling variants
- `tailwindcss`: Utility-first CSS framework

### Validation & Forms
- `zod`: Runtime type validation
- `drizzle-zod`: Database schema to Zod conversion
- `react-hook-form`: Form state management
- `@hookform/resolvers`: Zod resolver integration

## Python Dependencies (libral-core)

### Framework
- `fastapi`: Async Python web framework for advanced modules
- `uvicorn`: ASGI server
- `pydantic`: Data validation and settings management
- `structlog`: Structured logging

### Cryptography
- `python-gnupg`: GPG operations wrapper
- `cryptography`: Low-level cryptographic primitives

### Utilities
- `httpx`: Async HTTP client for external API communication
- `redis[asyncio]`: Async Redis client

All Python dependencies managed via Poetry (`pyproject.toml`).