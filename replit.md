# Overview

Libral Core is a privacy-first microkernel platform for enterprise-grade cryptographic operations and user data sovereignty. It uniquely leverages Telegram personal log servers for user-controlled, non-centrally stored data. The platform features enterprise-grade GPG encryption (Aegis-PGP), a hot-swappable plugin marketplace, a multi-transport communication system with intelligent failover, and an autonomous SelfEvolution system for self-healing and continuous improvement.

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
- **Global Aesthetic**: Neon Cyberpunk HUD with a cyan color scheme (`#00FFD1`), monospace typography (Major Mono Display/Share Tech Mono), neon borders with cyan glow, dark slate background (#080A0F).
- **Design System**: Mobile-first PWA with PC control split.
- **Three Operation Modes**:
    - **Monitor Mode (`/monitor`)**: Real-time system health dashboard.
    - **Control Mode (`/control`)**: Executive panel for critical operations.
    - **Creation Mode (`/creation`)**: ChatOps development with AI assistance ("月の光" copilot).
- **C3 Console (Context Command Center)** (`/c3`):
    - **Main Dashboard**: Geometric door animation entrance, dual navigation (Apps & Console Menu).
    - **Apps & Features** (`/c3/apps`): Auto-generated module management UI with real-time status.
    - **Console Menu** (`/c3/console`): System monitoring, critical operations with double-confirmation logic.
    - **Module Detail Pages** (`/c3/apps/:moduleId`): Dynamically generated detail pages for each connected module.

### AI Model Parallelization
- **Implementation Strategy**: Gemini for speed, GPT for complexity, Dual Verification Mode for parallel execution and hallucination detection.
- **Moonlight Enforcement Protocol**: AI persona ("月の光") that is ruthless, hyper-competent, addresses user as "兄弟", and provides unfiltered answers.
- **AI Bridge Layer**: Async queue controller with retry, fallback (Gemini → GPT5-mini → OSS Model), and priority-based request handling.
- **Evaluator**: Multi-criteria evaluation (accuracy, coherence, relevance, ethics, completeness) with automatic regeneration for low scores and KB integration.
- **OSS Manager**: Dynamic loading/unloading of OSS models (LLaMA3, Mistral, Falcon, Whisper, CLIP) based on category, with memory-efficient auto-unload.
- **AI Router**: Intelligent routing between Gemini, GPT5-mini, and OSS models based on task type, with load balancing and performance monitoring.
- **Embedding Layer**: Vector embedding generation (384 dimensions) and similarity search with cosine similarity, foundational for FAISS + ChromaDB.

### Aegis-PGP Cryptography Module (Python/FastAPI)
- Enterprise-grade GPG with Modern Strong, Compatibility, and Backup Longterm policies.
- Supports Context-Lock signatures, RSA-4096, ED25519, ECDSA-P256, and WKD integration.

### Multi-Transport Communication System
- Intelligent message routing with failover across Telegram, Email, and Webhook.
- Features health checking, priority-based routing, and encrypted payload delivery.

### Personal Log Server System
- Users control personal Telegram Supergroups for GPG-encrypted activity logs.
- Enables user-controlled data retention and hashtag filtering, ensuring zero central data storage.

### Module Registry & Hot-Swapping
- Dynamic management for runtime registration, discovery, health monitoring, and independent lifecycle of modules.

### Database Schema Architecture
- Type-safe PostgreSQL schema (Drizzle ORM) for Users, Transactions, Events, Modules, Stamps, and System Metrics.

### Real-Time WebSocket System
- Event-driven updates via Redis pub/sub for live dashboards.

### Payment Integration Layer
- Multi-provider payment processing including Telegram Stars and PayPal.
- All transactions are logged to personal log servers with GPG encryption.

## Security & Privacy Controls
- **Cryptographic Standards**: AES-256-OCB, SHA-256/SHA-512, RSA-4096, ED25519, ECDSA-P256, HMAC-SHA256.
- **Input Validation & Sanitization**: XSS protection, SQL injection prevention, rate limiting, CSP headers.
- **Audit & Compliance**: Event logging, GDPR-compliant design, encrypted audit trails, user data export/deletion.

## SelfEvolution Autonomous System
- **LPO (Libral Protocol Optimizer)**: Autonomous monitoring, health scoring, ZK Audit, Self-Healing AI, Finance Optimizer, RBAC abstraction, predictive monitoring.
- **KBE (Knowledge Booster Engine)**: Privacy-first collective intelligence with federated learning, homomorphic aggregation, and anonymous knowledge submission. Includes a fully independent KB system with a web UI (`/kb-editor`) for CRUD operations and multi-language support.
- **AEG (Auto Evolution Gateway)**: Autonomous platform evolution with AI-driven development prioritization, GitHub PR generation, and task management.
- **Vaporization Protocol**: Privacy-first cache management with Redis TTL enforcement, KBE flush hooks, and pattern protection for personal data.
- **Integration Layer**: Unified dashboard, orchestrated execution cycles, module health checks, and manifest documentation.

## Development & Deployment Structure
- **PCGP V1.0 Organization**: Standardized folder structure (`client/`, `server/`, `shared/`).
- **CI/CD Pipeline**: GitHub Actions for testing, security scanning, automated deployment to Replit, type checking, and linting.
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