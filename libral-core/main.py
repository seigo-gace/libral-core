"""
Libral Core FastAPI Application Entry Point
Week 1: GPG Module Implementation
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import structlog
import uvicorn

from libral_core.config import settings
from libral_core.modules.gpg.router import router as gpg_router

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    
    # Startup
    logger.info(
        "Libral Core starting up",
        version="1.0.0",
        phase="Week 1 - GPG Module",
        privacy_model="Telegram Personal Log Servers"
    )
    
    # Validate critical configuration
    if not settings.secret_key:
        logger.error("SECRET_KEY not configured - application cannot start")
        raise ValueError("SECRET_KEY is required")
    
    if not settings.gpg_system_key_id:
        logger.warning("GPG_SYSTEM_KEY_ID not configured - some features may be limited")
    
    logger.info("Libral Core startup completed")
    
    yield
    
    # Shutdown
    logger.info("Libral Core shutting down")

# Create FastAPI application
app = FastAPI(
    title="Libral Core - Privacy-First Platform",
    description="""
    G-ACE.inc TGAXIS Libral Platform Core
    
    ## Week 1-3: Foundation Modules Complete
    
    ### GPG Cryptographic Module (Week 1)
    - **GPG Encryption/Decryption** with modern policies (SEIPDv2/AES-256-OCB)
    - **Context-Lock Signatures** for operational security
    - **OpenPGP v6** key support with Ed25519/RSA-4096
    - **Web Key Directory (WKD)** for automated key discovery
    - **.env.gpg** encrypted configuration management
    
    ### Plugin Marketplace (Week 2)
    - **Secure Plugin Discovery** with privacy protection
    - **GPG-Verified Installation** with signature validation
    - **Sandboxed Execution** environment with permission control
    - **Revenue Sharing** framework for plugin developers
    - **Anonymous Operations** with local plugin registry
    
    ### Authentication System (Week 3)
    - **Telegram OAuth Integration** with privacy-first design
    - **Personal Log Servers** in user-owned Telegram groups
    - **GPG-Encrypted Sessions** with Context-Lock tokens
    - **Zero Personal Data Storage** on central servers
    - **Complete User Data Sovereignty** and GDPR compliance
    
    ### Communication Gateway (Week 4)
    - **Multi-Protocol Messaging** with Telegram, Email, and Webhook support
    - **Authenticated Routing** using Week 3 authentication system
    - **Topic & Hashtag Organization** in personal log servers
    - **GPG-Encrypted Transport** for sensitive communications
    - **Privacy-First Notifications** with user preference controls
    - **Personal Log Integration** for complete message audit trails
    
    ## Privacy-First Architecture
    
    - 🔐 **No Personal Data Storage**: All user data encrypted to personal Telegram groups
    - 🔒 **GPG Everything**: All sensitive data is GPG-encrypted at rest
    - ⏰ **24h Auto-Delete**: Temporary cache automatically purged
    - 🏠 **Data Sovereignty**: Users control their own data completely
    
    ## Development Roadmap
    
    - **Week 1-4**: GPG, Marketplace, Authentication & Communication ✅ (Current)
    - **Week 5**: Event Management & Real-time Systems  
    - **Week 6-7**: Payments & API Hub integration
    - **Week 8**: Libral AI Agent initial connection
    """,
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# Security Middleware
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["*"] if settings.debug else ["localhost", "*.libral.app"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.debug else ["https://*.libral.app"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Log all HTTP requests for audit trail"""
    
    start_time = structlog.get_logger().info
    
    # Log request
    logger.info(
        "HTTP request",
        method=request.method,
        url=str(request.url),
        client_ip=request.client.host if request.client else "unknown",
        user_agent=request.headers.get("user-agent", "unknown")
    )
    
    # Process request
    response = await call_next(request)
    
    # Log response  
    logger.info(
        "HTTP response",
        method=request.method,
        url=str(request.url),
        status_code=response.status_code,
        content_length=response.headers.get("content-length", "0")
    )
    
    return response

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected errors with privacy-conscious logging"""
    
    logger.error(
        "Unhandled exception",
        error_type=type(exc).__name__,
        error_message=str(exc),
        url=str(request.url),
        method=request.method
    )
    
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred",
            "request_id": "N/A",  # TODO: Add request ID middleware
            "timestamp": "2024-01-01T00:00:00Z"  # TODO: Add proper timestamp
        }
    )

# Health check endpoint
@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy", 
        "module": "GPG Core",
        "version": "1.0.0",
        "phase": "Week 1 - GPG Implementation",
        "timestamp": "2024-01-01T00:00:00Z"  # TODO: Add proper timestamp
    }

# Include routers
app.include_router(gpg_router)

# Include marketplace router
from libral_core.modules.marketplace.router import router as marketplace_router
app.include_router(marketplace_router)

# Include authentication router
from libral_core.modules.auth.router import router as auth_router
app.include_router(auth_router)

# Include communication router
from libral_core.modules.communication.router import router as communication_router
app.include_router(communication_router)

# Development server
if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )