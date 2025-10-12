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
