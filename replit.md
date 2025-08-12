# Overview

This is Libral Core, a microservices management dashboard built as a full-stack web application. The system serves as a centralized monitoring and management platform for various microservices including payment processing, user management, Telegram bot integrations, and system metrics tracking. It features real-time monitoring capabilities with WebSocket connections, comprehensive system health tracking, and a modern React-based dashboard interface.

# User Preferences

Preferred communication style: Simple, everyday language.
Technical design approach: Microkernel architecture with event-driven design
Interface language: Japanese for dashboard and user-facing components

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
- **API Design**: RESTful endpoints with structured error handling and request logging middleware

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