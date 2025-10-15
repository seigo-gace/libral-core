# Libral Core - Project Structure

## 📂 Active Files (Production)

All active code is located in the **root directory** of this project:

### Frontend
- **Path**: `./client/`
- **Entry Point**: `./client/src/main.tsx`
- **Pages**:
  - `./client/src/pages/Monitor.tsx` - LPO Health Dashboard
  - `./client/src/pages/Control.tsx` - Executive Control Panel
  - `./client/src/pages/Creation.tsx` - AI Development ChatOps
  - `./client/src/pages/kb-editor.tsx` - **NEW** Knowledge Base Editor

### Backend
- **Path**: `./server/`
- **Entry Point**: `./server/index.ts`
- **Routes**: `./server/routes.ts`

#### Core Modules
- `./server/core/transport/` - Multi-transport messaging system
- `./server/core/ai-bridge/` - **NEW** AI Bridge Layer (async queue, fallback)
- `./server/core/ai-router.ts` - **NEW** Enhanced AI Router

#### AI & KB Modules
- `./server/modules/kb-system.ts` - **NEW** Independent Knowledge Base System
- `./server/modules/evaluator.ts` - **NEW** Evaluator 2.0 (AI quality scoring)
- `./server/modules/oss-manager.ts` - **NEW** OSS AI Model Manager
- `./server/modules/embedding.ts` - **NEW** Vector Embedding Layer
- `./server/modules/aegis-pgp.ts` - GPG Encryption Module
- `./server/modules/stamp-creator.ts` - Stamp Creator Module
- `./server/modules/registry.ts` - Module Registry

#### Services
- `./server/services/` - Redis, WebSocket, Event Bus, Telegram

### Shared Types
- **Path**: `./shared/`
- **Schema**: `./shared/schema.ts` - Database models and Zod validators

## 🆕 New Features (v2.1)

### KB System Independence
- Separated from KBE, now fully independent module
- Direct KB management via Web UI (`/kb-editor`)
- RESTful API for KB operations

### AI Module Evolution
- **AI Bridge Layer**: Async queue control, auto-retry, fallback chain
- **Evaluator 2.0**: AI output quality scoring (90+ threshold)
- **OSS Manager**: Dynamic model loading (LLaMA3, Mistral, Falcon, Whisper, CLIP)
- **AI Router**: Intelligent routing between Gemini, GPT5-mini, OSS models
- **Embedding Layer**: Vector similarity search (FAISS + ChromaDB foundation)

### New API Endpoints
- `/api/kb/entries` - KB CRUD operations
- `/api/evaluator/*` - AI evaluation endpoints
- `/api/oss/*` - OSS model management
- `/api/ai-router/route` - Intelligent AI routing
- `/api/embedding/*` - Embedding operations

## 🗑️ Removed Directories (Were Duplicates)
- `.config/LiburaL-BaseCore/` ❌ Deleted
- `LiburaL-BaseCore/` ❌ Deleted

## 🚀 Running the Application

### Development Mode
```bash
npm run dev
```

### Build & Production
```bash
npm run build
npm start
```

## 📝 Important Files
- `vite.config.ts` - Vite configuration
- `package.json` - Dependencies and scripts
- `.replit` - Replit run configuration (run = "npm run dev")
- `replit.md` - System architecture documentation
- `PROJECT_STRUCTURE.md` - This file

---

**Note**: All files in the root `./client/`, `./server/`, and `./shared/` directories are the ONLY active files. Any other copies are backups or templates and should be ignored.
- **Category Management**: Organized knowledge taxonomy
- **Independent Operation**: Fully separated from main system

#### AI Bridge Layer
- **Async Queue Controller**: Non-blocking request processing
- **Auto Fallback Chain**: Gemini → GPT5-mini → OSS Model
- **Retry Logic**: Configurable retry with exponential backoff
- **Priority-Based Routing**: Handle requests by priority

#### Evaluator 2.0
- **Multi-Criteria Evaluation**: Accuracy, Coherence, Relevance, Ethics, Completeness
- **90-Point Threshold**: Auto-regeneration for low scores
- **KB Integration**: Learn from evaluations
- **Hallucination Detection**: Dual verification mode

#### OSS Manager
- **Dynamic Model Loading**: LLaMA3, Mistral, Falcon, Whisper, CLIP
- **Memory-Efficient**: Auto-unload based on usage
- **Category-Based Management**: Organize by model type
- **Priority Control**: Load models by priority

#### AI Router
- **Intelligent Routing**: Task-type based model selection
- **Load Balancing**: Distribute requests efficiently
- **Performance Monitoring**: Track response times
- **Evaluation Integration**: Quality-aware routing

#### Embedding Layer
- **384-Dimensional Vectors**: Rich semantic representation
- **Cosine Similarity Search**: Efficient similarity matching
- **Language-Specific**: Per-language embeddings
- **FAISS/ChromaDB Ready**: Foundation for vector databases

### C3 Console (Context Command Center)

#### Main Dashboard (`/c3`)
- **Geometric Door Animation**: Sci-fi HUD entrance with 400ms cubic-bezier transitions
- **System Status Display**: Real-time module health monitoring
- **Dual Navigation**: Apps & Features + Console Menu access

#### Apps & Features (`/c3/apps`)
- **Auto-Generated Module Cards**: Dynamic UI based on connected modules
- **Status Indicators**: Real-time online/offline/maintenance status
- **Module Details**: Detailed view with features and actions
- **Statistics Display**: Live module statistics

#### Console Menu (`/c3/console`)
- **System Metrics**: CPU, Memory, Active Users monitoring
- **Critical Operations**: Restart, Emergency Stop with double confirmation
- **Double Confirmation Logic**: CONFIRM code input required
- **System Logs**: Real-time log display

#### Module Detail Pages (`/c3/apps/:moduleId`)
- **Auto-Generated UI**: Dynamically created for each module
- **Feature Overview**: Comprehensive capability listing
- **Action Buttons**: Direct access to module operations
- **Live Statistics**: Real-time module stats display

## 🎨 Design System

### Neon Cyberpunk HUD

**Color Palette**
```css
--base-background: #080A0F (Dark Slate)
--primary-accent: #00FFD1 (Cyber Teal)
--secondary-text: #FFFFFF (White)
--critical-alert: #FF3A5B (Warning Red)
--warning-status: #FFC400 (Amber)
```

**Typography**
- Font Family: 'Major Mono Display' / 'Share Tech Mono' (Monospace)
- Style: All caps for tech emphasis
- Letter Spacing: Wide tracking (0.2em - 0.4em)

**Visual Effects**
- Grid background with neon glow
- Noise/grain texture overlay
- Geometric clip-paths for futuristic panels
- Scanning line animations on active elements
- Border glow effects on hover

## 🚀 Getting Started

### Prerequisites

```bash
Node.js >= 18
PostgreSQL (Neon)
Redis
```

### Installation

```bash
# Install dependencies
npm install

# Set up environment variables
cp .env.example .env

# Initialize database
npm run db:push

# Start development server
npm run dev
```

### Environment Variables

```env
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
TELEGRAM_BOT_TOKEN=...
TELEGRAM_WEBHOOK_SECRET=...
```

## 📡 API Endpoints

### Knowledge Base
- `GET /api/kb/stats` - KB system statistics
- `POST /api/kb/entries` - Create KB entry
- `GET /api/kb/entries` - List KB entries
- `GET /api/kb/entries/:id` - Get specific entry
- `PUT /api/kb/entries/:id` - Update entry
- `DELETE /api/kb/entries/:id` - Delete entry
- `POST /api/kb/search` - Search KB

### AI Modules
- `POST /api/evaluator/evaluate` - Evaluate AI output
- `GET /api/evaluator/stats` - Evaluator statistics
- `GET /api/oss/models` - List OSS models
- `POST /api/oss/models/:id/load` - Load model
- `POST /api/ai-router/route` - Route AI request
- `POST /api/embedding/generate` - Generate embeddings
- `POST /api/embedding/search` - Search similar embeddings

### System
- `GET /api/system/metrics` - System metrics
- `POST /api/telegram/webhook` - Telegram webhook
- `GET /api/transport/status` - Transport system status

## 🎯 Key Features

### Privacy-First Architecture
- **Zero Central Storage**: All user data encrypted and stored in user-controlled Telegram personal log servers
- **GPG Encryption**: Enterprise-grade encryption for all sensitive data
- **User Data Sovereignty**: Users control their own data retention and access

### Aegis-PGP Cryptography
- **Multiple Key Types**: RSA-4096, ED25519, ECDSA-P256
- **Security Policies**: Modern Strong, Compatibility, Backup Longterm
- **Context-Lock Signatures**: Enhanced signature verification
- **WKD Integration**: Web Key Directory support

### Multi-Transport Communication
- **Intelligent Failover**: Automatic fallback across transports
- **Health Checking**: Continuous transport status monitoring
- **Priority Routing**: Route messages by importance
- **Encrypted Payloads**: End-to-end encryption

### Hot-Swappable Modules
- **Runtime Registration**: Add modules without restart
- **Health Monitoring**: Continuous module status tracking
- **Independent Lifecycle**: Modules operate independently
- **Dynamic Discovery**: Auto-discover available modules

## 🔒 Security

### Cryptographic Standards
- **Encryption**: AES-256-OCB
- **Hashing**: SHA-256, SHA-512
- **Key Exchange**: RSA-4096, ED25519, ECDSA-P256
- **MAC**: HMAC-SHA256

### Security Controls
- **Input Validation**: XSS and SQL injection prevention
- **Rate Limiting**: DDoS protection
- **CSP Headers**: Content Security Policy
- **Audit Logging**: Comprehensive event tracking

## 📊 Development Progress

### ✅ Completed (v1.0)

**Core Infrastructure**
- [x] Microkernel architecture setup
- [x] PostgreSQL database schema (Drizzle ORM)
- [x] Redis pub/sub system
- [x] WebSocket real-time updates
- [x] Multi-transport communication system

**AI Module Ascension**
- [x] KB System independence (80+ languages)
- [x] AI Bridge Layer with fallback chain
- [x] Evaluator 2.0 with 90-point threshold
- [x] OSS Manager for dynamic model loading
- [x] AI Router for intelligent routing
- [x] Embedding Layer (384-dim vectors)

**User Interfaces**
- [x] Neon Cyberpunk HUD design system
- [x] Monitor/Control/Creation modes
- [x] KB Editor web UI (`/kb-editor`)
- [x] C3 Console Dashboard (`/c3`)
- [x] Auto-generated module management

**Security & Privacy**
- [x] Aegis-PGP cryptography module
- [x] GPG encryption integration
- [x] Personal log server system
- [x] Zero-central-storage architecture

### 🔄 In Progress

**SelfEvolution System**
- [ ] LPO (Libral Protocol Optimizer)
- [ ] KBE (Knowledge Booster Engine) - Federated learning
- [ ] AEG (Auto Evolution Gateway) - AI-driven development
- [ ] Vaporization Protocol - Privacy cache management

**Vector Database Integration**
- [ ] FAISS integration for similarity search
- [ ] ChromaDB for persistent vector storage
- [ ] Migration from simulated to real embeddings

**Payment Integration**
- [ ] Telegram Stars payment flow
- [ ] PayPal Server SDK integration
- [ ] Transaction GPG encryption

### 📋 Roadmap

**Q1 2025**
- [ ] Complete SelfEvolution system
- [ ] FAISS/ChromaDB integration
- [ ] Payment system completion
- [ ] Production deployment preparation

**Q2 2025**
- [ ] Advanced AI model integration
- [ ] Enhanced privacy features
- [ ] Multi-region deployment
- [ ] Performance optimization

## 🧪 Testing

```bash
# Run all tests
npm test

# Run specific test suite
npm test -- --grep "KB System"

# E2E tests
npm run test:e2e
```

## 📦 Project Structure

```
libral-core/
├── client/               # Frontend (React + Vite)
│   ├── src/
│   │   ├── pages/       # Page components
│   │   │   ├── c3-dashboard.tsx
│   │   │   ├── c3-apps.tsx
│   │   │   ├── c3-console.tsx
│   │   │   └── c3-module-detail.tsx
│   │   ├── components/  # Reusable components
│   │   └── lib/         # Utilities
│   └── index.html
├── server/              # Backend (Node.js + Express)
│   ├── core/           # Core systems
│   │   ├── ai-bridge/  # AI Bridge Layer
│   │   ├── ai-router.ts # AI Router
│   │   └── transport/  # Multi-transport system
│   ├── modules/        # Hot-swappable modules
│   │   ├── kb-system.ts
│   │   ├── evaluator.ts
│   │   ├── oss-manager.ts
│   │   └── embedding.ts
│   ├── routes/         # API routes
│   └── services/       # Business logic
├── shared/             # Shared types & schemas
└── libral-core/       # Python microservices
    ├── aegis_pgp/     # Aegis-PGP module
    └── utils/         # Shared utilities
```

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Workflow

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Neon Database** - Serverless PostgreSQL
- **Replit** - Development and deployment platform
- **Telegram** - Bot API and personal log servers
- **OpenAI & Google** - AI model access

## 📞 Support

For support, please:
- Open an issue on GitHub
- Join our community Discord
- Email: support@libralcore.dev

## 🔗 Links

- **Documentation**: [docs.libralcore.dev](https://docs.libralcore.dev)
- **Demo**: [demo.libralcore.dev](https://demo.libralcore.dev)
- **Status Page**: [status.libralcore.dev](https://status.libralcore.dev)

---

**Built with ❤️ by the Libral Core Team**

*Empowering users with privacy, sovereignty, and AI-driven automation*
