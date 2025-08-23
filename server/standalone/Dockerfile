# server/standalone/Dockerfile
FROM node:20-slim

WORKDIR /app

# Copy built files
COPY server/standalone/dist ./dist
COPY config/routing.yaml ./config/routing.yaml

# Environment
ENV PORT=8787
ENV NODE_ENV=production

# Expose port
EXPOSE 8787

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8787/v1/health || exit 1

# Start service
CMD ["node", "dist/server.js"]