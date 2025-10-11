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

### Backend
- **Path**: `./server/`
- **Entry Point**: `./server/index.ts`
- **Routes**: `./server/routes.ts`
- **Core Modules**:
  - `./server/core/transport/` - Multi-transport messaging system
  - `./server/modules/` - Plugin registry (Aegis-PGP, Stamp Creator)
  - `./server/services/` - Redis, WebSocket, Event Bus, Telegram

### Shared Types
- **Path**: `./shared/`
- **Schema**: `./shared/schema.ts` - Database models and Zod validators

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
- `.replit` - Replit run configuration
- `replit.md` - System architecture documentation

---

**Note**: All files in the root `./client/`, `./server/`, and `./shared/` directories are the ONLY active files. Any other copies are backups or templates and should be ignored.
