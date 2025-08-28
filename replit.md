# Overview

This is Libral Core, a sophisticated microkernel-based platform designed for complete privacy-first architecture. The system serves as the foundation for G-ACE.inc TGAXIS Libral Platform, featuring revolutionary user data sovereignty through Telegram personal log servers. Currently implemented as a Node.js prototype, the system will undergo complete reconstruction using Python + FastAPI to eliminate legacy constraints and achieve optimal performance.

## Current Status (Python + FastAPI Implementation)
- ✅ Week 1: GPG Module - Complete cryptographic foundation 
- ✅ Week 2: Plugin Marketplace - Third-party extension system
- ✅ Week 3: Authentication System - Revolutionary personal log servers
- ✅ Week 4: Communication Gateway - Multi-protocol messaging with topic support
- ✅ Week 5: Event Management - Real-time processing with personal server admin buttons
- ✅ Week 6: Payment & Billing - Telegram Stars integration with encrypted billing logs
- ✅ Week 7: API Hub & External Integration - Encrypted API credentials with usage tracking
- ✅ Privacy-first architecture with Telegram personal log servers
- ✅ Context-Lock signatures for operational security
- ✅ Enterprise-grade GPG encryption (SEIPDv2/AES-256-OCB)
- ✅ Complete user data sovereignty implementation
- ✅ Perfect Telegram topics and hashtag organization
- ✅ One-click personal server admin registration with minimal permissions
- ✅ Plugin developer revenue sharing with automatic distribution
- ✅ Multi-provider API integration with cost management

## Development Progress (8-Week Roadmap)
- Week 1-7: GPG, Marketplace, Authentication, Communication, Events, Payments & API Hub ✅ **COMPLETED**
- Week 8: Libral AI Agent initial connection (Final)

# User Preferences

Preferred communication style: Simple, everyday language.
Technical design approach: Privacy-first microkernel architecture with event-driven design
Interface language: Japanese for dashboard and user-facing components
Development strategy: Zero-based reconstruction with Python + FastAPI (6-week roadmap)
Privacy model: User data sovereignty via Telegram personal log servers (no central storage)

# System Architecture

## Frontend Architecture
- **Framework**: React with TypeScript using Vite as the build tool
- **UI Components**: Radix UI primitives with shadcn/ui component library for consistent design
- **Styling**: Tailwind CSS with a dark theme configuration and custom color variables
- **State Management**: TanStack Query (React Query) for server state management and caching
- **Routing**: Wouter for lightweight client-side routing
- **Real-time Updates**: Custom WebSocket hook for live data streaming from backend services

## Backend Architecture
- **Runtime**: Node.js with Express.js framework
- **Language**: TypeScript with ES modules
- **Database ORM**: Drizzle ORM with PostgreSQL dialect
- **Real-time Communication**: WebSocket server integration with Redis pub/sub pattern
- **Service Architecture**: Modular service pattern with dedicated services for events, Redis, Telegram, and WebSocket management
- **Transport Layer**: Platform-agnostic transport system with automatic failover (Telegram → Email → Webhook)
- **Module System**: Microkernel architecture with hot-swappable modules and registry pattern
- **API Design**: RESTful endpoints with structured error handling and request logging middleware
- **Cryptography**: Aegis-PGP Core integration with SEIPDv2, AES-256-OCB, and OpenPGP v6 standards
- **Dual Deployment**: Library mode (npm package) and standalone service mode for flexibility

## Database Design
- **Primary Database**: PostgreSQL accessed via Neon Database serverless connection
- **Schema Management**: Drizzle Kit for migrations and schema management
- **Core Tables**: 
  - Users (with Telegram integration)
  - Transactions (payment processing)
  - Events (system logging and audit trail)
  - Modules (microservice status tracking)
  - System Metrics (performance monitoring)
  - API Endpoints (request analytics)
  - Plugins (installed marketplace extensions)
  - Plugin Metadata (version, permissions, status)
  - Plugin Dependencies (installation requirements)
  - Audit Events (GPG operations and plugin installations)

## Real-time Event System
- **Event Bus**: Redis-based pub/sub messaging system with mock implementation for development
- **Event Categories**: System events, user events, payment events, API events
- **WebSocket Broadcasting**: Real-time updates pushed to dashboard clients for live monitoring
- **Event Storage**: Persistent event logging in PostgreSQL for audit and analysis

## Monitoring and Metrics
- **System Health**: CPU usage, memory usage, active users, API request rates
- **Module Status**: Individual microservice health checks and status tracking
- **Infrastructure Monitoring**: Database connections, Redis metrics, Docker container stats
- **API Analytics**: Endpoint usage statistics, response times, request patterns

# External Dependencies

## Database Services
- **Neon Database**: Serverless PostgreSQL hosting with connection pooling
- **Redis**: In-memory data store for caching and pub/sub messaging (currently mocked for development)

## Third-party Integrations
- **Telegram Bot API**: Webhook processing for bot interactions and payment notifications
- **Telegram Payments**: Integration with Telegram Stars and payment processing

## Development Tools
- **Replit Integration**: Development environment with cartographer plugin and error overlay
- **Vite Plugins**: React support, runtime error handling, and development tooling

## UI and Styling
- **Google Fonts**: Inter font family for consistent typography
- **Radix UI**: Accessible component primitives for form controls, dialogs, and navigation
- **Tailwind CSS**: Utility-first CSS framework with custom design tokens
- **Lucide Icons**: Icon library for consistent iconography throughout the interface

## Build and Deployment
- **esbuild**: Fast JavaScript bundler for production builds
- **TypeScript**: Type safety across frontend and backend with path mapping
- **PostCSS**: CSS processing with Tailwind and Autoprefixer plugins