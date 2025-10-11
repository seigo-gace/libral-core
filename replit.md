# Overview

Libral Core is a privacy-first microkernel platform designed for enterprise-grade cryptographic operations and user data sovereignty. It features a unique architecture where user data is never centrally stored, instead leveraging Telegram personal log servers for complete user control. The platform includes enterprise-grade GPG encryption (Aegis-PGP), a hot-swappable plugin marketplace, a multi-transport communication system with intelligent failover, and an autonomous SelfEvolution system for self-healing and continuous improvement.

# User Preferences

Preferred communication style: Simple, everyday language.

# System Architecture

## Core Design Principles

- **Privacy-First Architecture**: Zero-central-storage model; user data is GPG-encrypted and stored in user-controlled Telegram personal log servers.
- **Microkernel Design Pattern**: Modular, hot-swappable components allowing runtime loading/unloading without downtime.
- **Hybrid Technology Stack**:
    - **Backend Core**: Node.js/Express (TypeScript) for REST APIs and WebSockets.
    - **Advanced Modules**: Python/FastAPI for cryptographic operations and AI.
    - **Frontend**: React (TypeScript) with Vite and Shadcn/UI.
    - **Database**: PostgreSQL with Drizzle ORM.
    - **Caching/PubSub**: Redis.

## Key Architectural Components

### User Interface & Experience
- **Global Aesthetic**: Neon Cyberpunk HUD with a cyan color scheme (`#00FFFF`), monospace typography (Courier New).
- **Design System**: Neon borders with cyan glow, black gradient background, mobile-first PWA with PC control split.
- **Three Operation Modes**:
    - **Monitor Mode (`/monitor`)**: Real-time system health dashboard (LPO Health Score, ZK Audit Status, Vaporization Metrics, Module Health).
    - **Control Mode (`/control`)**: Executive panel for critical operations (CRAD Trigger, Rate Limit Control, AMM Unblock) with confirmation.
    - **Creation Mode (`/creation`)**: ChatOps development with AI assistance ("月の光" copilot), model selection (Gemini/GPT/Dual), PR auto-generation, and KBE knowledge recommendations.

### AI Model Parallelization
- **Implementation Strategy**: Gemini for speed, GPT for complexity, Dual Verification Mode for parallel execution and hallucination detection.
- **Moonlight Enforcement Protocol**: AI persona ("月の光") that is ruthless, hyper-competent, addresses user as "兄弟", and provides unfiltered answers.

### Aegis-PGP Cryptography Module (Python/FastAPI)
- Enterprise-grade GPG with Modern Strong, Compatibility, and Backup Longterm policies.
- Features Context-Lock signatures, supports RSA-4096, ED25519, ECDSA-P256, and WKD integration.

### Multi-Transport Communication System
- Intelligent message routing with failover across Telegram, Email, and Webhook.
- Implements health checking, priority-based routing, and encrypted payload delivery.

### Personal Log Server System
- Users own and control personal Telegram Supergroups for GPG-encrypted activity logs.
- Features user-controlled data retention (1-365 days auto-delete) and hashtag filtering.
- Ensures zero central storage of user data by Libral servers.

### Module Registry & Hot-Swapping
- Dynamic management system for runtime registration, discovery, health monitoring, and independent lifecycle of modules.

### Database Schema Architecture
- Type-safe PostgreSQL schema (Drizzle ORM) for Users, Transactions, Events, Modules, Stamps, and System Metrics.

### Real-Time WebSocket System
- Event-driven updates via Redis pub/sub for live dashboards (metrics, module status, transactions, user activity).

### Payment Integration Layer
- Multi-provider payment processing including Telegram Stars, PayPal, and future Stripe integration.
- All transactions logged to personal log servers with GPG encryption.

## Security & Privacy Controls
- **Cryptographic Standards**: AES-256-OCB, SHA-256/SHA-512, RSA-4096, ED25519, ECDSA-P256, HMAC-SHA256.
- **Input Validation & Sanitization**: XSS protection, SQL injection prevention, rate limiting, CSP headers.
- **Audit & Compliance**: Event logging, GDPR-compliant design, encrypted audit trails, user data export/deletion.

## SelfEvolution Autonomous System
- **LPO (Libral Protocol Optimizer)**: Autonomous monitoring, health scoring, ZK Audit, Self-Healing AI, Finance Optimizer, RBAC abstraction, predictive monitoring.
- **KBE (Knowledge Booster Engine)**: Privacy-first collective intelligence with federated learning, homomorphic aggregation, and anonymous knowledge submission.
- **AEG (Auto Evolution Gateway)**: Autonomous platform evolution with AI-driven development prioritization, GitHub PR generation, and task management.
- **Vaporization Protocol**: Privacy-first cache management with Redis TTL enforcement, KBE flush hooks, and pattern protection for personal data.
- **Integration Layer**: Unified dashboard, orchestrated execution cycles, module health checks, and manifest documentation.

## Development & Deployment Structure
- **PCGP V1.0 Organization**: Standardized folder structure (`src/`, `docs/`, `infra/`, `policies/`, `archive/`).
- **CI/CD Pipeline**: GitHub Actions for testing, security scanning (Semgrep), automated deployment to Replit, type checking, and linting.
- **Environment Configuration**: Managed via Pydantic Settings (Python) and environment variables (Node.js); sensitive credentials GPG-encrypted.

# External Dependencies

## Third-Party Services
- **Telegram Bot API**: Primary communication, OAuth, personal log servers, Telegram Stars payments, message delivery.
- **Database: PostgreSQL (Neon)**: Serverless persistent storage.
- **Cache & Message Queue: Redis**: Real-time pub/sub, session management, WebSocket event broadcasting.
- **Payment Providers**:
    - Telegram Stars
    - PayPal Server SDK (`@paypal/paypal-server-sdk`)

## Core NPM Dependencies
- **Backend**: `express`, `drizzle-orm`, `ws`, `connect-pg-simple`.
- **Frontend**: `react`, `react-dom`, `@tanstack/react-query`, `wouter`, `vite`.
- **UI Component Library**: Radix UI primitives, `shadcn/ui`, `class-variance-authority`, `tailwindcss`.
- **Validation & Forms**: `zod`, `drizzle-zod`, `react-hook-form`, `@hookform/resolvers`.

## Python Dependencies (libral-core)
- **Framework**: `fastapi`, `uvicorn`, `pydantic`, `structlog`.
- **Cryptography**: `python-gnupg`, `cryptography`.
- **Utilities**: `httpx`, `redis[asyncio]`.

# Current Implementation Status (2025-10-11)

## ✅ Completed Features

### Backend API Endpoints (23 endpoints across 6 modules)
1. **LPO (Libral Protocol Optimizer)**
   - `/api/lpo/metrics/health-score` - System health score
   - `/api/lpo/metrics/zk-audit` - Zero-knowledge audit status
   - `/api/lpo/monitor/vaporization` - Cache vaporization metrics
   - `/api/lpo/monitor/modules` - Module health monitoring
   - `/api/lpo/self-healing/trigger` - Trigger self-healing

2. **Governance Module**
   - `/api/governance/rbac/roles` - Role management
   - `/api/governance/rbac/permissions` - Permission management
   - `/api/governance/crad/trigger` - Critical action triggers

3. **AEG (Auto Evolution Gateway)**
   - `/api/aeg/tasks` - Task management
   - `/api/aeg/github/pr` - GitHub PR generation
   - `/api/aeg/priorities` - Development priorities

4. **AI Module**
   - `/api/ai/chat` - AI chat with Moonlight enforcement
   - `/api/ai/models` - Model selection (Gemini/GPT/Dual)
   - `/api/ai/dual-verify` - Dual model verification

5. **KBE (Knowledge Booster Engine)**
   - `/api/kbe/knowledge/submit` - Anonymous knowledge submission
   - `/api/kbe/knowledge/query` - Knowledge query
   - `/api/kbe/collective/insights` - Collective insights

6. **Vaporization Protocol**
   - `/api/vaporization/status` - Cache status
   - `/api/vaporization/flush` - Manual cache flush
   - `/api/vaporization/patterns` - Protected patterns

7. **SelfEvolution Orchestrator**
   - `/api/selfevolution/status` - Overall status
   - `/api/selfevolution/cycle` - Execution cycle
   - `/api/selfevolution/manifest` - System manifest

### Frontend Implementation
- **3 Operation Modes**:
  - Monitor Mode (`/monitor`) - LPO Health Dashboard with real-time metrics
  - Control Mode (`/control`) - Executive control panel with critical actions
  - Creation Mode (`/creation`) - AI ChatOps development interface

- **7 API Client Modules** in `client/src/api/`:
  - `lpo.ts`, `governance.ts`, `aeg.ts`, `ai.ts`, `kbe.ts`, `vaporization.ts`, `selfevolution.ts`

- **Neon Cyberpunk HUD Design**:
  - Cyan (#00FFFF) color scheme
  - Monospace typography (Courier New)
  - Neon borders with glow effects
  - Dark gradient backgrounds

### Core Infrastructure
- Multi-transport communication system (Telegram, Email, Webhook)
- Module registry with hot-swapping capability
- WebSocket real-time event system
- Redis pub/sub for event broadcasting
- GPG encryption integration (Aegis-PGP)

## 📂 Active File Structure

**All production code is in the root directory:**

```
/home/runner/workspace/
├── client/              # Frontend (React + Vite)
│   ├── src/
│   │   ├── pages/      # Monitor, Control, Creation
│   │   ├── api/        # API client modules
│   │   └── components/ # UI components
│   └── index.html
├── server/              # Backend (Node.js + Express)
│   ├── index.ts        # Entry point
│   ├── routes.ts       # API routes
│   ├── core/           # Transport system
│   ├── modules/        # Plugin registry
│   └── services/       # Redis, WebSocket, Events
├── shared/              # Shared types
│   └── schema.ts       # Database schema + Zod validators
├── vite.config.ts      # Vite configuration
├── package.json        # Dependencies
└── .replit             # Run configuration
```

## 🚀 How to Run

### Prerequisites
1. Fix `.replit` file structure:
   ```toml
   modules = ["nodejs-20"]
   run = "npm run dev"
   
   [[ports]]
   localPort = 5000
   externalPort = 5000
   
   [[ports]]
   localPort = 36543
   externalPort = 80
   ```
   **Note**: `run` command must be OUTSIDE (above) the `[[ports]]` sections.

### Development Mode
```bash
npm run dev
```

### Build & Production
```bash
npm run build  # Builds client to dist/public
npm start      # Runs production server
```

### Port Configuration
- **Port 5000**: Main application (frontend + backend API)
- **Port 36543**: Alternative external port

## 🔧 Recent Changes (2025-10-11)

1. ✅ Fixed vite.config.ts - Removed async top-level await
2. ✅ Removed duplicate directories (.config/LiburaL-BaseCore, LiburaL-BaseCore)
3. ✅ Implemented all 23 SelfEvolution API endpoints
4. ✅ Created 7 frontend API client modules
5. ✅ Built 3 operational mode UIs (Monitor/Control/Creation)
6. ✅ Generated production build (dist/public)
7. ✅ Created PROJECT_STRUCTURE.md for clarity

## 📝 Next Steps

1. **Fix .replit file** - Move `run` command outside `[[ports]]` section
2. **Test workflow restart** - Use `restart_workflow` tool
3. **Verify all endpoints** - Test all 23 API endpoints
4. **E2E testing** - Test Monitor/Control/Creation modes