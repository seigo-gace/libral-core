# Overview

Libral Core is a microkernel-based platform for the G-ACE.inc TGAXIS Libral Platform, focusing on privacy-first architecture and user data sovereignty through Telegram personal log servers. Initially a Node.js prototype, it's being reconstructed in Python + FastAPI for optimal performance. The system features enterprise-grade GPG encryption, a plugin marketplace, a revolutionary authentication system, multi-protocol communication, real-time event management, multi-provider payment integration (including Telegram Stars, PayPay, PayPal for Japanese users), and an API hub. Its core ambition is to provide a robust, private, and user-centric digital ecosystem with advanced operational automation and autonomous governance.

# User Preferences

Preferred communication style: Simple, everyday language.
Technical design approach: Privacy-first microkernel architecture with event-driven design
Interface language: Japanese for dashboard and user-facing components
Development strategy: Zero-based reconstruction with Python + FastAPI (6-week roadmap)
Privacy model: User data sovereignty via Telegram personal log servers (no central storage)
Payment integration: Telegram collaborative provider payment options with user-friendly Japanese localization
Regional optimization: PayPay and PayPal integration for Japanese users with clear explanations and guidance

# System Architecture

## PCGP V1.0 Architecture (Professional Grooming Protocol)

### 4-Tier Module Structure
- **`src/library/components/`**: Component Layer for minimal, reusable parts (datetime, crypto, config, validators).
- **`src/modules/`**: Functional modules.
- **`src/governance/`**: Governance Layer including AMM (Autonomous Moderator Module) and CRAD (Context-Aware Auto Debugger).
- **`libral_core/integrated_modules/`**: Core integrated modules (LIC/LEB/LAS/LGL).
- **`libral_core/modules/`**: Payment/API Hub.
- **`libral_core/ops/`**: OPS automation.
- **`policies/`**: Policy definitions (JSON/YAML) for AMM and CRAD.
- **`infra/`**: Infrastructure settings.
- **`docs/`**: Documentation including `MASTER_REFERENCE.md`.
- **`archive/`**: For old configurations, reports, and legacy code.

### Component Layer (Tier 1)
- **datetime_utils**: UTC standardized datetime processing.
- **crypto_helpers**: Secure token generation, hashing, HMAC.
- **config_loader**: Policy loading, environment variable management.
- **validators**: Data validation and sanitization.

### Governance Layer (AMM/CRAD)
- **AMM**: KMS access control, GitOps enforcement.
- **CRAD**: Automated recovery with a 180-second MTTR target.

### OPS Automation Layer
- **SAL (Storage Abstraction Layer)**: Prometheus integration, dynamic routing, encrypted audit logs.
- **CCA (Context-Lock Audit)**: Audit certificate management, crypto module enforcement, KMS integration.
- **K8S Automation**: GitOps enforcement, chaos engineering, HA/DRP, vulnerability scanning.

## Library Module Architecture
- **Design**: Independent "toolbox" layer for core utilities.
- **Submodules**:
  - **utils**: String processing, datetime handling, validation.
  - **api_clients**: Unified external API communication.
  - **file_handlers**: Image and video processing (supporting TxT WORLD Creator's and LIVE VIDEO CHAT).

## Frontend Architecture
- **Framework**: React with TypeScript (Vite).
- **UI Components**: Radix UI primitives with shadcn/ui.
- **Styling**: Tailwind CSS (dark theme, custom colors).
- **State Management**: TanStack Query for server state.
- **Routing**: Wouter.
- **Real-time**: Custom WebSocket hook.

## Backend Architecture
- **Runtime**: Node.js with Express.js (TypeScript, ES modules).
- **Database ORM**: Drizzle ORM with PostgreSQL.
- **Real-time**: WebSocket server with Redis pub/sub.
- **Service Architecture**: Modular, microkernel with hot-swappable modules.
- **Transport Layer**: Platform-agnostic with failover (Telegram → Email → Webhook).
- **Cryptography**: Aegis-PGP Core with SEIPDv2, AES-256-OCB, OpenPGP v6.
- **Deployment**: Library mode (npm package) and standalone service mode.

## Database Design
- **Primary Database**: PostgreSQL (Neon Database serverless).
- **Schema Management**: Drizzle Kit.
- **Core Tables**: Users, Transactions, Events, Modules, System Metrics, API Endpoints, Plugins, Plugin Metadata, Plugin Dependencies, Audit Events.

## Real-time Event System
- **Event Bus**: Redis-based pub/sub.
- **Event Categories**: System, user, payment, API events.
- **WebSocket Broadcasting**: Real-time updates to dashboard.
- **Event Storage**: Persistent logging in PostgreSQL.

## Monitoring and Metrics
- **Metrics**: CPU, memory, active users, API request rates, module status, database/Redis metrics, Docker stats, API analytics.

# External Dependencies

## Database Services
- **Neon Database**: Serverless PostgreSQL hosting.
- **Redis**: In-memory data store for caching and pub/sub.

## Third-party Integrations
- **Telegram Bot API**: For bot interactions and payment notifications.
- **Telegram Payments**: Integration for Telegram Stars.

## Development Tools
- **Replit Integration**: Development environment.
- **Vite Plugins**: For React support and development.

## UI and Styling
- **Google Fonts**: Inter font family.
- **Radix UI**: Accessible component primitives.
- **Tailwind CSS**: Utility-first CSS framework.
- **Lucide Icons**: Icon library.

## Build and Deployment
- **esbuild**: JavaScript bundler.
- **TypeScript**: For type safety.
- **PostCSS**: CSS processing.