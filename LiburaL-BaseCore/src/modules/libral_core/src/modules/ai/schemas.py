"""
Libral AI Module - Schemas
Privacy-First Dual-AI System Data Models
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional, Any, Union

from pydantic import BaseModel, Field


# AI Types and Enums
class AIType(str, Enum):
    """AI system types"""
    INTERNAL = "internal"  # 自社AI
    EXTERNAL = "external"  # 外部AI（判定役）


class AIProvider(str, Enum):
    """External AI providers"""
    OPENAI = "openai"
    GEMINI = "gemini"
    ANTHROPIC = "anthropic"
    LOCAL = "local"


class QueryCategory(str, Enum):
    """AI query categories"""
    GENERAL = "general"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    ANALYSIS = "analysis"
    EVALUATION = "evaluation"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"


class EvaluationCriteria(str, Enum):
    """AI evaluation criteria"""
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"
    COMPLETENESS = "completeness"
    PRIVACY_COMPLIANCE = "privacy_compliance"
    TONE = "tone"
    HELPFULNESS = "helpfulness"


class UsageStatus(str, Enum):
    """Usage quota status"""
    AVAILABLE = "available"
    LIMITED = "limited"
    EXCEEDED = "exceeded"
    RESET_PENDING = "reset_pending"


# Core AI Schemas
class AIQuery(BaseModel):
    """AI query request"""
    query_id: str = Field(..., description="Unique query identifier")
    
    # Query content
    text: str = Field(..., min_length=1, max_length=10000)
    category: QueryCategory = Field(default=QueryCategory.GENERAL)
    context: Optional[str] = Field(default=None, max_length=5000)
    
    # Privacy and security
    user_id: Optional[str] = None
    session_id: Optional[str] = None
    encryption_required: bool = Field(default=True)
    log_to_personal_server: bool = Field(default=True)
    
    # Processing options
    max_tokens: Optional[int] = Field(default=1000, ge=1, le=4000)
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    timeout_seconds: int = Field(default=30, ge=1, le=300)
    
    # Metadata
    priority: str = Field(default="normal")
    tags: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class AIResponse(BaseModel):
    """AI response"""
    query_id: str
    response_id: str = Field(..., description="Unique response identifier")
    
    # Response content
    text: str
    category: QueryCategory
    ai_type: AIType
    provider: Optional[AIProvider] = None
    
    # Quality metrics
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    processing_time_ms: float
    tokens_used: Optional[int] = None
    
    # Privacy and security
    encrypted: bool = Field(default=False)
    personally_identifiable_info_removed: bool = Field(default=True)
    
    # Timestamps
    created_at: datetime = Field(default_factory=datetime.utcnow)
    expires_at: Optional[datetime] = None
    
    # Metadata
    model_version: Optional[str] = None
    cost_estimate: Optional[float] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvaluationRequest(BaseModel):
    """External AI evaluation request"""
    evaluation_id: str = Field(..., description="Unique evaluation identifier")
    
    # Content to evaluate
    original_query: AIQuery
    ai_response: AIResponse
    
    # Evaluation parameters
    criteria: List[EvaluationCriteria] = Field(default_factory=lambda: [
        EvaluationCriteria.ACCURACY,
        EvaluationCriteria.RELEVANCE,
        EvaluationCriteria.PRIVACY_COMPLIANCE
    ])
    
    # Options
    provide_suggestions: bool = Field(default=True)
    include_alternative_response: bool = Field(default=False)
    evaluation_depth: str = Field(default="standard")  # quick, standard, comprehensive
    
    # Context
    user_feedback: Optional[str] = None
    domain_context: Optional[str] = None


class EvaluationResponse(BaseModel):
    """External AI evaluation response"""
    evaluation_id: str
    
    # Evaluation results
    overall_score: float = Field(..., ge=0.0, le=1.0)
    criteria_scores: Dict[EvaluationCriteria, float] = Field(default_factory=dict)
    
    # Detailed feedback
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    suggestions: List[str] = Field(default_factory=list)
    
    # Alternative response
    alternative_response: Optional[str] = None
    improvement_recommendations: List[str] = Field(default_factory=list)
    
    # Metadata
    evaluator_model: str
    evaluation_time_ms: float
    evaluation_cost: Optional[float] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


# Usage Management Schemas
class UsageQuota(BaseModel):
    """AI usage quota management"""
    quota_id: str
    ai_type: AIType
    provider: Optional[AIProvider] = None
    
    # Quota limits
    daily_limit: int = Field(..., ge=0)
    hourly_limit: Optional[int] = Field(default=None, ge=0)
    monthly_limit: Optional[int] = Field(default=None, ge=0)
    
    # Current usage
    daily_used: int = Field(default=0, ge=0)
    hourly_used: int = Field(default=0, ge=0)
    monthly_used: int = Field(default=0, ge=0)
    
    # Reset times
    last_daily_reset: datetime = Field(default_factory=datetime.utcnow)
    last_hourly_reset: datetime = Field(default_factory=datetime.utcnow)
    last_monthly_reset: datetime = Field(default_factory=datetime.utcnow)
    
    # Status
    status: UsageStatus = Field(default=UsageStatus.AVAILABLE)
    next_reset: datetime
    
    # Cost tracking
    estimated_daily_cost: float = Field(default=0.0, ge=0.0)
    estimated_monthly_cost: float = Field(default=0.0, ge=0.0)
    cost_limit_daily: Optional[float] = Field(default=None, ge=0.0)
    cost_limit_monthly: Optional[float] = Field(default=None, ge=0.0)


class UsageStatistics(BaseModel):
    """AI usage statistics"""
    period_start: datetime
    period_end: datetime
    
    # Query statistics
    total_queries: int = Field(default=0, ge=0)
    internal_ai_queries: int = Field(default=0, ge=0)
    external_ai_evaluations: int = Field(default=0, ge=0)
    
    # Performance metrics
    average_response_time_ms: float = Field(default=0.0, ge=0.0)
    average_confidence_score: float = Field(default=0.0, ge=0.0, le=1.0)
    success_rate: float = Field(default=0.0, ge=0.0, le=1.0)
    
    # Cost metrics
    total_cost: float = Field(default=0.0, ge=0.0)
    cost_per_query: float = Field(default=0.0, ge=0.0)
    cost_breakdown: Dict[str, float] = Field(default_factory=dict)
    
    # Category breakdown
    queries_by_category: Dict[QueryCategory, int] = Field(default_factory=dict)
    
    # Quality metrics
    evaluation_scores: Dict[EvaluationCriteria, float] = Field(default_factory=dict)
    user_satisfaction_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)


# Configuration Schemas
class AIConfig(BaseModel):
    """AI module configuration"""
    
    # Provider settings
    openai_api_key: Optional[str] = None
    gemini_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    
    # Default settings
    default_internal_model: str = Field(default="libral-internal-v1")
    default_external_provider: AIProvider = Field(default=AIProvider.OPENAI)
    default_external_model: str = Field(default="gpt-4")
    
    # Usage limits
    external_ai_daily_limit: int = Field(default=2, ge=1)
    external_ai_hourly_limit: int = Field(default=1, ge=1)
    internal_ai_daily_limit: int = Field(default=1000, ge=1)
    
    # Cost limits
    daily_cost_limit: float = Field(default=10.0, ge=0.0)
    monthly_cost_limit: float = Field(default=200.0, ge=0.0)
    
    # Security settings
    require_context_lock: bool = Field(default=True)
    encrypt_responses: bool = Field(default=True)
    log_to_personal_servers: bool = Field(default=True)
    remove_pii: bool = Field(default=True)
    
    # Performance settings
    default_timeout_seconds: int = Field(default=30, ge=1, le=300)
    max_concurrent_requests: int = Field(default=10, ge=1, le=100)
    cache_responses: bool = Field(default=True)
    cache_ttl_hours: int = Field(default=24, ge=1)
    
    # Redis settings
    redis_key_prefix: str = Field(default="libral_ai:")
    redis_quota_key: str = Field(default="quota")
    redis_cache_key: str = Field(default="cache")


# Health and Monitoring
class AIHealthResponse(BaseModel):
    """AI module health status"""
    status: str
    version: str
    components: Dict[str, Dict[str, Any]] = Field(default_factory=lambda: {
        "internal_ai": {"status": "unknown", "response_time_ms": 0, "queries_processed": 0},
        "external_ai": {"status": "unknown", "evaluations_performed": 0, "quota_remaining": 0},
        "usage_manager": {"status": "unknown", "quotas_active": 0, "cost_tracking": True},
        "redis_cache": {"status": "unknown", "cache_hit_rate": 0.0, "cached_items": 0},
        "context_lock": {"status": "unknown", "verifications_performed": 0}
    })
    uptime_seconds: float
    last_health_check: datetime


class AIMetrics(BaseModel):
    """AI module metrics"""
    period_start: datetime
    period_end: datetime
    
    # Core metrics
    total_queries: int
    successful_queries: int
    failed_queries: int
    average_response_time_ms: float
    
    # AI-specific metrics
    internal_ai_queries: int
    external_ai_evaluations: int
    context_lock_verifications: int
    quota_exceeded_rejections: int
    
    # Quality metrics
    average_confidence_score: float
    average_evaluation_score: float
    user_satisfaction_rate: float
    
    # Cost metrics
    total_cost_usd: float
    cost_per_query_usd: float
    quota_utilization_rate: float
    
    # Performance metrics
    cache_hit_rate: float
    concurrent_request_peak: int
    timeout_rate: float


# Error Schema
class AIError(BaseModel):
    """AI module error response"""
    error_code: str
    error_message: str
    component: str = Field(..., description="internal_ai|external_ai|usage_manager|context_lock")
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    request_id: str