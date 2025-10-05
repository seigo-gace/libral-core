"""
Libral APP Module - Service Layer
Application management business logic with PostgreSQL and Redis integration
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

import asyncpg
import redis.asyncio as redis
import structlog

from .schemas import (
    App, AppAnalytics, AppConfig, AppCreate, AppHealth, AppModuleHealth,
    AppPermission, AppPermissionCreate, AppPermissionModel, AppStatus,
    AppType, AppUpdate
)

logger = structlog.get_logger(__name__)


class DatabaseManager:
    """PostgreSQL database management"""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
        logger.info("Database manager initialized", database_url=database_url.split('@')[0])
    
    async def connect(self):
        """Establish database connection pool"""
        try:
            self.pool = await asyncpg.create_pool(
                self.database_url,
                min_size=5,
                max_size=20,
                command_timeout=30
            )
            
            # Create tables if not exist
            await self._create_tables()
            
            logger.info("Database connection established")
            
        except Exception as e:
            logger.error("Database connection failed", error=str(e))
            raise
    
    async def disconnect(self):
        """Close database connection pool"""
        if self.pool:
            await self.pool.close()
            logger.info("Database connection closed")
    
    async def _create_tables(self):
        """Create application tables"""
        async with self.pool.acquire() as conn:
            # Applications table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    app_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    description TEXT,
                    app_type TEXT NOT NULL,
                    owner_id TEXT NOT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    metadata JSONB DEFAULT '{}',
                    tags TEXT[] DEFAULT '{}',
                    settings JSONB DEFAULT '{}',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW(),
                    last_accessed TIMESTAMP,
                    access_count INTEGER DEFAULT 0
                )
            """)
            
            # App permissions table
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS app_permissions (
                    permission_id TEXT PRIMARY KEY,
                    app_id TEXT NOT NULL REFERENCES applications(app_id) ON DELETE CASCADE,
                    user_id TEXT NOT NULL,
                    permission TEXT NOT NULL,
                    granted_at TIMESTAMP DEFAULT NOW(),
                    granted_by TEXT NOT NULL
                )
            """)
            
            # Create indexes
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_apps_owner ON applications(owner_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_apps_status ON applications(status)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_perms_app ON app_permissions(app_id)")
            await conn.execute("CREATE INDEX IF NOT EXISTS idx_perms_user ON app_permissions(user_id)")
            
            logger.info("Database tables created/verified")


class CacheManager:
    """Redis cache management"""
    
    def __init__(self, redis_url: str, cache_ttl_hours: int = 24):
        self.redis_url = redis_url
        self.cache_ttl_hours = cache_ttl_hours
        self.cache_ttl_seconds = cache_ttl_hours * 3600
        self.redis_client: Optional[redis.Redis] = None
        logger.info("Cache manager initialized", ttl_hours=cache_ttl_hours)
    
    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = await redis.from_url(
                self.redis_url,
                decode_responses=True,
                encoding="utf-8"
            )
            await self.redis_client.ping()
            logger.info("Redis connection established")
            
        except Exception as e:
            logger.error("Redis connection failed", error=str(e))
            # Continue without cache
            self.redis_client = None
    
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()
            logger.info("Redis connection closed")
    
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            return await self.redis_client.get(f"app:{key}")
        except Exception as e:
            logger.warning("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(self, key: str, value: str, ttl: Optional[int] = None):
        """Set value in cache"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.set(
                f"app:{key}",
                value,
                ex=ttl or self.cache_ttl_seconds
            )
        except Exception as e:
            logger.warning("Cache set failed", key=key, error=str(e))
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(f"app:{key}")
        except Exception as e:
            logger.warning("Cache delete failed", key=key, error=str(e))
    
    async def invalidate_pattern(self, pattern: str):
        """Invalidate cache keys matching pattern"""
        if not self.redis_client:
            return
        
        try:
            async for key in self.redis_client.scan_iter(match=f"app:{pattern}"):
                await self.redis_client.delete(key)
        except Exception as e:
            logger.warning("Cache invalidation failed", pattern=pattern, error=str(e))


class LibralApp:
    """Main Libral APP service"""
    
    def __init__(self, config: AppConfig = None):
        self.config = config or AppConfig()
        
        # Initialize managers
        self.db = DatabaseManager(self.config.database_url)
        self.cache = CacheManager(self.config.redis_url, self.config.cache_ttl_hours)
        
        # Statistics
        self.stats = {
            "total_operations": 0,
            "successful_operations": 0,
            "failed_operations": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        logger.info("Libral APP service initialized")
    
    async def startup(self):
        """Service startup"""
        await self.db.connect()
        await self.cache.connect()
        logger.info("APP module startup completed")
    
    async def shutdown(self):
        """Service shutdown"""
        await self.db.disconnect()
        await self.cache.disconnect()
        logger.info("APP module shutdown completed")
    
    # Application CRUD Operations
    async def create_app(self, app_data: AppCreate) -> App:
        """Create new application"""
        try:
            self.stats["total_operations"] += 1
            
            app = App(
                app_id=str(uuid4()),
                name=app_data.name,
                description=app_data.description,
                app_type=app_data.app_type,
                owner_id=app_data.owner_id,
                metadata=app_data.metadata,
                tags=app_data.tags,
                settings=app_data.settings,
                status=AppStatus.DRAFT
            )
            
            # Insert into database
            async with self.db.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO applications 
                    (app_id, name, description, app_type, owner_id, status, metadata, tags, settings)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
                """, app.app_id, app.name, app.description, app.app_type.value,
                   app.owner_id, app.status.value, json.dumps(app.metadata),
                   app.tags, json.dumps(app.settings))
            
            # Cache the app
            await self.cache.set(
                f"app:{app.app_id}",
                app.model_dump_json()
            )
            
            self.stats["successful_operations"] += 1
            logger.info("Application created", app_id=app.app_id, name=app.name)
            
            return app
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error("Application creation failed", error=str(e))
            raise
    
    async def get_app(self, app_id: str) -> Optional[App]:
        """Get application by ID"""
        try:
            # Try cache first
            cached = await self.cache.get(f"app:{app_id}")
            if cached:
                self.stats["cache_hits"] += 1
                return App.model_validate_json(cached)
            
            self.stats["cache_misses"] += 1
            
            # Get from database
            async with self.db.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM applications WHERE app_id = $1",
                    app_id
                )
            
            if not row:
                return None
            
            app = App(
                app_id=row["app_id"],
                name=row["name"],
                description=row["description"],
                app_type=AppType(row["app_type"]),
                owner_id=row["owner_id"],
                status=AppStatus(row["status"]),
                metadata=row["metadata"] or {},
                tags=row["tags"] or [],
                settings=row["settings"] or {},
                created_at=row["created_at"],
                updated_at=row["updated_at"],
                last_accessed=row["last_accessed"],
                access_count=row["access_count"]
            )
            
            # Cache it
            await self.cache.set(f"app:{app_id}", app.model_dump_json())
            
            return app
            
        except Exception as e:
            logger.error("Failed to get application", app_id=app_id, error=str(e))
            return None
    
    async def update_app(self, app_id: str, update_data: AppUpdate) -> Optional[App]:
        """Update application"""
        try:
            self.stats["total_operations"] += 1
            
            # Build update query
            update_fields = []
            values = []
            idx = 1
            
            for field, value in update_data.model_dump(exclude_unset=True).items():
                if value is not None:
                    if field in ["metadata", "settings"]:
                        update_fields.append(f"{field} = ${idx}::jsonb")
                        values.append(json.dumps(value))
                    elif field == "app_type" or field == "status":
                        update_fields.append(f"{field} = ${idx}")
                        values.append(value.value if hasattr(value, 'value') else value)
                    else:
                        update_fields.append(f"{field} = ${idx}")
                        values.append(value)
                    idx += 1
            
            if not update_fields:
                return await self.get_app(app_id)
            
            update_fields.append(f"updated_at = ${idx}")
            values.append(datetime.utcnow())
            idx += 1
            
            values.append(app_id)
            
            query = f"""
                UPDATE applications 
                SET {', '.join(update_fields)}
                WHERE app_id = ${idx}
                RETURNING *
            """
            
            async with self.db.pool.acquire() as conn:
                row = await conn.fetchrow(query, *values)
            
            if not row:
                self.stats["failed_operations"] += 1
                return None
            
            # Invalidate cache
            await self.cache.delete(f"app:{app_id}")
            
            self.stats["successful_operations"] += 1
            logger.info("Application updated", app_id=app_id)
            
            return await self.get_app(app_id)
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error("Application update failed", app_id=app_id, error=str(e))
            raise
    
    async def delete_app(self, app_id: str) -> bool:
        """Delete application"""
        try:
            self.stats["total_operations"] += 1
            
            async with self.db.pool.acquire() as conn:
                result = await conn.execute(
                    "DELETE FROM applications WHERE app_id = $1",
                    app_id
                )
            
            # Invalidate cache
            await self.cache.delete(f"app:{app_id}")
            await self.cache.invalidate_pattern(f"list:*")
            
            self.stats["successful_operations"] += 1
            logger.info("Application deleted", app_id=app_id)
            
            return True
            
        except Exception as e:
            self.stats["failed_operations"] += 1
            logger.error("Application deletion failed", app_id=app_id, error=str(e))
            return False
    
    async def list_apps(self, owner_id: Optional[str] = None, status: Optional[AppStatus] = None,
                       page: int = 1, page_size: int = 50) -> Dict[str, Any]:
        """List applications with pagination"""
        try:
            offset = (page - 1) * page_size
            
            # Build query
            conditions = []
            values = []
            idx = 1
            
            if owner_id:
                conditions.append(f"owner_id = ${idx}")
                values.append(owner_id)
                idx += 1
            
            if status:
                conditions.append(f"status = ${idx}")
                values.append(status.value)
                idx += 1
            
            where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
            
            async with self.db.pool.acquire() as conn:
                # Get total count
                count_query = f"SELECT COUNT(*) FROM applications {where_clause}"
                total = await conn.fetchval(count_query, *values)
                
                # Get apps
                values.extend([page_size, offset])
                query = f"""
                    SELECT * FROM applications {where_clause}
                    ORDER BY created_at DESC
                    LIMIT ${idx} OFFSET ${idx + 1}
                """
                
                rows = await conn.fetch(query, *values)
            
            apps = [
                App(
                    app_id=row["app_id"],
                    name=row["name"],
                    description=row["description"],
                    app_type=AppType(row["app_type"]),
                    owner_id=row["owner_id"],
                    status=AppStatus(row["status"]),
                    metadata=row["metadata"] or {},
                    tags=row["tags"] or [],
                    settings=row["settings"] or {},
                    created_at=row["created_at"],
                    updated_at=row["updated_at"],
                    last_accessed=row["last_accessed"],
                    access_count=row["access_count"]
                )
                for row in rows
            ]
            
            return {
                "apps": apps,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size
            }
            
        except Exception as e:
            logger.error("Failed to list applications", error=str(e))
            return {"apps": [], "total": 0, "page": page, "page_size": page_size}
    
    async def get_health(self) -> AppModuleHealth:
        """Get module health status"""
        try:
            # Get app counts
            async with self.db.pool.acquire() as conn:
                total_apps = await conn.fetchval("SELECT COUNT(*) FROM applications")
                active_apps = await conn.fetchval(
                    "SELECT COUNT(*) FROM applications WHERE status = 'active'"
                )
            
            return AppModuleHealth(
                status="healthy",
                version="1.0.0",
                components={
                    "database": {
                        "status": "healthy" if self.db.pool else "disconnected",
                        "pool_size": self.db.pool._holders.__len__() if self.db.pool else 0
                    },
                    "cache": {
                        "status": "healthy" if self.cache.redis_client else "disconnected",
                        "hit_rate": self.stats["cache_hits"] / max(1, self.stats["cache_hits"] + self.stats["cache_misses"])
                    }
                },
                total_apps=total_apps,
                active_apps=active_apps,
                uptime_seconds=0.0
            )
            
        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return AppModuleHealth(
                status="unhealthy",
                components={"error": str(e)}
            )
