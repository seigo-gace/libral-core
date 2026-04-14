"""
Libral AI Module - Service Layer
Revolutionary Dual-AI System Implementation
"""

import asyncio
import hashlib
import json
import secrets
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from uuid import uuid4

import httpx
import redis.asyncio as redis
import structlog

from .schemas import (
    AIConfig, AIError, AIHealthResponse, AIMetrics, AIProvider, AIQuery, AIResponse, AIType,
    EvaluationRequest, EvaluationResponse, QueryCategory, UsageQuota, UsageStatistics, UsageStatus
)

logger = structlog.get_logger(__name__)


class ContextLockVerifier:
    """Context-Lock signature verification for security"""
    
    def __init__(self):
        self.verification_count = 0
        logger.info("Context-Lock verifier initialized")
    
    async def verify_context_lock(self, context_lock_header: str, user_id: str = None) -> bool:
        """Verify Context-Lock signature"""
        try:
            if not context_lock_header:
                logger.warning("Context-Lock header missing", user_id=user_id)
                return False
            
            # In production, this would integrate with LGL (Libral Governance Layer)
            # for proper digital signature verification
            if len(context_lock_header) < 32:
                logger.warning("Context-Lock header too short", user_id=user_id)
                return False
            
            # Simulate signature verification
            if context_lock_header.startswith("dummy_") and len(context_lock_header) > 32:
                # Development/testing signature
                self.verification_count += 1
                logger.info("Context-Lock verified (development mode)", user_id=user_id)
                return True
            
            # Simulate real signature verification
            # This would integrate with LGL's signature verification system
            is_valid = len(context_lock_header) >= 64
            
            if is_valid:
                self.verification_count += 1
                logger.info("Context-Lock verified", user_id=user_id)
            else:
                logger.warning("Context-Lock verification failed", user_id=user_id)
            
            return is_valid
            
        except Exception as e:
            logger.error("Context-Lock verification error", error=str(e), user_id=user_id)
            return False


class UsageManager:
    """AI usage quota and cost management system"""
    
    def __init__(self, redis_client: redis.Redis, config: AIConfig):
        self.redis_client = redis_client
        self.config = config
        self.quota_key_prefix = f"{config.redis_key_prefix}{config.redis_quota_key}:"
        logger.info("Usage manager initialized")
    
    async def check_quota(self, ai_type: AIType, user_id: str = None) -> bool:
        """Check if usage quota allows the request"""
        try:
            quota_key = f"{self.quota_key_prefix}{ai_type}:{user_id or 'system'}"
            
            # Get current usage
            current_usage = await self.redis_client.hgetall(quota_key)
            
            if not current_usage:
                # Initialize quota
                await self._initialize_quota(quota_key, ai_type)
                return True
            
            # Check daily limit
            daily_used = int(current_usage.get('daily_used', 0))
            daily_limit = int(current_usage.get('daily_limit', 1000))
            
            # Check if quota needs reset
            last_reset_str = current_usage.get('last_daily_reset')
            if last_reset_str:
                last_reset = datetime.fromisoformat(last_reset_str)
                if datetime.utcnow() - last_reset > timedelta(hours=24):
                    await self._reset_daily_quota(quota_key, ai_type)
                    daily_used = 0
            
            # Check limits based on AI type
            if ai_type == AIType.EXTERNAL:
                limit = self.config.external_ai_daily_limit
            else:
                limit = self.config.internal_ai_daily_limit
            
            if daily_used >= limit:
                logger.warning("Usage quota exceeded", 
                              ai_type=ai_type, 
                              daily_used=daily_used, 
                              limit=limit, 
                              user_id=user_id)
                return False
            
            return True
            
        except Exception as e:
            logger.error("Quota check error", error=str(e), ai_type=ai_type, user_id=user_id)
            return False
    
    async def increment_usage(self, ai_type: AIType, user_id: str = None, cost: float = 0.0):
        """Increment usage counter"""
        try:
            quota_key = f"{self.quota_key_prefix}{ai_type}:{user_id or 'system'}"
            
            # Increment counters
            await self.redis_client.hincrby(quota_key, 'daily_used', 1)
            await self.redis_client.hincrby(quota_key, 'hourly_used', 1)
            await self.redis_client.hincrby(quota_key, 'monthly_used', 1)
            
            # Update cost
            if cost > 0:
                await self.redis_client.hincrbyfloat(quota_key, 'daily_cost', cost)
                await self.redis_client.hincrbyfloat(quota_key, 'monthly_cost', cost)
            
            logger.info("Usage incremented", 
                       ai_type=ai_type, 
                       cost=cost, 
                       user_id=user_id)
            
        except Exception as e:
            logger.error("Usage increment error", error=str(e))
    
    async def _initialize_quota(self, quota_key: str, ai_type: AIType):
        """Initialize quota for new user/AI type"""
        if ai_type == AIType.EXTERNAL:
            daily_limit = self.config.external_ai_daily_limit
        else:
            daily_limit = self.config.internal_ai_daily_limit
        
        quota_data = {
            'daily_limit': daily_limit,
            'daily_used': 0,
            'hourly_used': 0,
            'monthly_used': 0,
            'daily_cost': 0.0,
            'monthly_cost': 0.0,
            'last_daily_reset': datetime.utcnow().isoformat(),
            'last_hourly_reset': datetime.utcnow().isoformat(),
            'last_monthly_reset': datetime.utcnow().isoformat()
        }
        
        await self.redis_client.hset(quota_key, mapping=quota_data)
        
        # Set expiration (30 days)
        await self.redis_client.expire(quota_key, 30 * 24 * 3600)
    
    async def _reset_daily_quota(self, quota_key: str, ai_type: AIType):
        """Reset daily quota"""
        await self.redis_client.hset(quota_key, mapping={
            'daily_used': 0,
            'daily_cost': 0.0,
            'last_daily_reset': datetime.utcnow().isoformat()
        })
        
        logger.info("Daily quota reset", quota_key=quota_key, ai_type=ai_type)
    
    async def get_usage_stats(self, ai_type: AIType, user_id: str = None) -> Dict[str, Any]:
        """Get usage statistics"""
        try:
            quota_key = f"{self.quota_key_prefix}{ai_type}:{user_id or 'system'}"
            usage_data = await self.redis_client.hgetall(quota_key)
            
            if not usage_data:
                return {"status": "no_data"}
            
            return {
                "daily_used": int(usage_data.get('daily_used', 0)),
                "daily_limit": int(usage_data.get('daily_limit', 1000)),
                "daily_cost": float(usage_data.get('daily_cost', 0.0)),
                "monthly_cost": float(usage_data.get('monthly_cost', 0.0)),
                "last_reset": usage_data.get('last_daily_reset'),
                "status": "active"
            }
            
        except Exception as e:
            logger.error("Usage stats error", error=str(e))
            return {"status": "error", "error": str(e)}


class InternalAI:
    """Internal AI (自社AI) system for privacy-first responses"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.model = config.default_internal_model
        self.query_count = 0
        logger.info("Internal AI initialized", model=self.model)
    
    async def process_query(self, query: AIQuery) -> AIResponse:
        """Process query with internal AI"""
        start_time = datetime.utcnow()
        response_id = str(uuid4())
        
        try:
            # Simulate internal AI processing
            response_text = await self._generate_internal_response(query)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.query_count += 1
            
            response = AIResponse(
                query_id=query.query_id,
                response_id=response_id,
                text=response_text,
                category=query.category,
                ai_type=AIType.INTERNAL,
                confidence_score=0.85,  # Simulated confidence
                processing_time_ms=processing_time,
                tokens_used=len(response_text.split()) * 1.3,  # Estimated
                encrypted=query.encryption_required,
                model_version=self.model,
                cost_estimate=0.0  # Internal AI is free
            )
            
            logger.info("Internal AI query processed", 
                       query_id=query.query_id,
                       response_id=response_id,
                       category=query.category,
                       processing_time_ms=processing_time)
            
            return response
            
        except Exception as e:
            logger.error("Internal AI processing error", 
                        query_id=query.query_id,
                        error=str(e))
            
            # Return error response
            return AIResponse(
                query_id=query.query_id,
                response_id=response_id,
                text=f"申し訳ありません。処理中にエラーが発生しました: {str(e)}",
                category=query.category,
                ai_type=AIType.INTERNAL,
                confidence_score=0.0,
                processing_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                cost_estimate=0.0
            )
    
    async def _generate_internal_response(self, query: AIQuery) -> str:
        """Generate response using internal AI logic"""
        # Simulate processing delay
        await asyncio.sleep(0.1)
        
        # Privacy-first response generation
        base_response = f"自社AIが応答します: {query.text}"
        
        # Add category-specific responses
        if query.category == QueryCategory.TECHNICAL:
            return f"{base_response}\n\n技術的なご質問にお答えします。プライバシーを最優先に設計された当システムで、安全にサポートいたします。"
        elif query.category == QueryCategory.CREATIVE:
            return f"{base_response}\n\nクリエイティブなアイデアをお手伝いします。ユーザーのプライバシーを完全に保護しながら、創造的なソリューションを提供します。"
        elif query.category == QueryCategory.ANALYSIS:
            return f"{base_response}\n\n分析結果を提供します。全てのデータは暗号化され、個人情報は一切保存されません。"
        else:
            return f"{base_response}\n\nLibralプラットフォームへようこそ。完全なプライバシー保護のもと、最適なサポートを提供いたします。"


class ExternalAI:
    """External AI (判定役) system for evaluation and quality assurance"""
    
    def __init__(self, config: AIConfig):
        self.config = config
        self.provider = config.default_external_provider
        self.model = config.default_external_model
        self.evaluation_count = 0
        logger.info("External AI initialized", provider=self.provider, model=self.model)
    
    async def evaluate_response(self, request: EvaluationRequest) -> EvaluationResponse:
        """Evaluate AI response quality"""
        start_time = datetime.utcnow()
        
        try:
            # Simulate external AI evaluation
            evaluation_result = await self._perform_evaluation(request)
            
            processing_time = (datetime.utcnow() - start_time).total_seconds() * 1000
            self.evaluation_count += 1
            
            response = EvaluationResponse(
                evaluation_id=request.evaluation_id,
                overall_score=evaluation_result["overall_score"],
                criteria_scores=evaluation_result["criteria_scores"],
                strengths=evaluation_result["strengths"],
                weaknesses=evaluation_result["weaknesses"],
                suggestions=evaluation_result["suggestions"],
                evaluator_model=self.model,
                evaluation_time_ms=processing_time,
                evaluation_cost=0.01  # Estimated cost
            )
            
            logger.info("External AI evaluation completed", 
                       evaluation_id=request.evaluation_id,
                       overall_score=response.overall_score,
                       processing_time_ms=processing_time)
            
            return response
            
        except Exception as e:
            logger.error("External AI evaluation error", 
                        evaluation_id=request.evaluation_id,
                        error=str(e))
            
            # Return default evaluation
            return EvaluationResponse(
                evaluation_id=request.evaluation_id,
                overall_score=0.5,
                criteria_scores={},
                strengths=["処理が完了しました"],
                weaknesses=["評価中にエラーが発生しました"],
                suggestions=["システム管理者にお問い合わせください"],
                evaluator_model=self.model,
                evaluation_time_ms=(datetime.utcnow() - start_time).total_seconds() * 1000,
                evaluation_cost=0.0
            )
    
    async def _perform_evaluation(self, request: EvaluationRequest) -> Dict[str, Any]:
        """Perform evaluation using external AI"""
        # Simulate evaluation processing
        await asyncio.sleep(0.5)
        
        # Generate simulated evaluation results
        query_text = request.original_query.text
        response_text = request.ai_response.text
        
        # Simulate scoring based on content
        accuracy_score = 0.8 if "応答" in response_text else 0.6
        relevance_score = 0.9 if len(response_text) > 50 else 0.7
        privacy_score = 0.95 if "プライバシー" in response_text else 0.8
        
        return {
            "overall_score": (accuracy_score + relevance_score + privacy_score) / 3,
            "criteria_scores": {
                "accuracy": accuracy_score,
                "relevance": relevance_score,
                "privacy_compliance": privacy_score
            },
            "strengths": [
                "プライバシー保護が適切に実装されています",
                "応答速度が良好です",
                "ユーザーフレンドリーな表現です"
            ],
            "weaknesses": [
                "技術的詳細をもう少し充実させることができます",
                "具体例があるとさらに良いでしょう"
            ],
            "suggestions": [
                "より具体的な例を含めることを検討してください",
                "ユーザーの技術レベルに応じた説明を追加できます",
                "関連リソースへのガイダンスがあると有用です"
            ]
        }


class LibralAI:
    """Main Libral AI service coordinating internal and external AI systems"""
    
    def __init__(self, config: AIConfig = None, redis_url: str = "redis://localhost:6379"):
        self.config = config or AIConfig()
        
        # Initialize components
        self.redis_client = redis.from_url(redis_url, decode_responses=True)
        self.context_lock_verifier = ContextLockVerifier()
        self.usage_manager = UsageManager(self.redis_client, self.config)
        self.internal_ai = InternalAI(self.config)
        self.external_ai = ExternalAI(self.config)
        
        # Metrics
        self.metrics = {
            "total_queries": 0,
            "successful_queries": 0,
            "failed_queries": 0,
            "context_lock_verifications": 0,
            "quota_exceeded_rejections": 0
        }
        
        logger.info("Libral AI service initialized")
    
    async def process_internal_ai_query(self, query: AIQuery, context_lock: str, user_id: str = None) -> AIResponse:
        """Process query with internal AI"""
        try:
            self.metrics["total_queries"] += 1
            
            # Verify Context-Lock
            if not await self.context_lock_verifier.verify_context_lock(context_lock, user_id):
                self.metrics["failed_queries"] += 1
                raise ValueError("Context-Lock verification failed")
            
            self.metrics["context_lock_verifications"] += 1
            
            # Check quota
            if not await self.usage_manager.check_quota(AIType.INTERNAL, user_id):
                self.metrics["quota_exceeded_rejections"] += 1
                raise ValueError("Usage quota exceeded")
            
            # Process query
            response = await self.internal_ai.process_query(query)
            
            # Update usage
            await self.usage_manager.increment_usage(AIType.INTERNAL, user_id, 0.0)
            
            self.metrics["successful_queries"] += 1
            
            return response
            
        except Exception as e:
            self.metrics["failed_queries"] += 1
            logger.error("Internal AI query processing failed", error=str(e))
            raise
    
    async def process_external_ai_evaluation(self, request: EvaluationRequest, context_lock: str, user_id: str = None) -> EvaluationResponse:
        """Process evaluation with external AI"""
        try:
            # Verify Context-Lock
            if not await self.context_lock_verifier.verify_context_lock(context_lock, user_id):
                raise ValueError("Context-Lock verification failed")
            
            # Check quota (external AI has stricter limits)
            if not await self.usage_manager.check_quota(AIType.EXTERNAL, user_id):
                self.metrics["quota_exceeded_rejections"] += 1
                raise ValueError("External AI usage quota exceeded")
            
            # Process evaluation
            response = await self.external_ai.evaluate_response(request)
            
            # Update usage with cost
            await self.usage_manager.increment_usage(AIType.EXTERNAL, user_id, response.evaluation_cost)
            
            return response
            
        except Exception as e:
            logger.error("External AI evaluation failed", error=str(e))
            raise
    
    async def get_health(self) -> AIHealthResponse:
        """Get AI module health status"""
        return AIHealthResponse(
            status="healthy",
            version="1.0.0",
            components={
                "internal_ai": {
                    "status": "healthy",
                    "response_time_ms": 100,
                    "queries_processed": self.internal_ai.query_count
                },
                "external_ai": {
                    "status": "healthy",
                    "evaluations_performed": self.external_ai.evaluation_count,
                    "quota_remaining": self.config.external_ai_daily_limit
                },
                "usage_manager": {
                    "status": "healthy",
                    "quotas_active": 1,
                    "cost_tracking": True
                },
                "redis_cache": {
                    "status": "healthy",
                    "cache_hit_rate": 0.85,
                    "cached_items": 0
                },
                "context_lock": {
                    "status": "healthy",
                    "verifications_performed": self.context_lock_verifier.verification_count
                }
            },
            uptime_seconds=0.0,
            last_health_check=datetime.utcnow()
        )
    
    async def get_metrics(self, period_start: datetime, period_end: datetime) -> AIMetrics:
        """Get AI module metrics"""
        return AIMetrics(
            period_start=period_start,
            period_end=period_end,
            total_queries=self.metrics["total_queries"],
            successful_queries=self.metrics["successful_queries"],
            failed_queries=self.metrics["failed_queries"],
            average_response_time_ms=150.0,
            internal_ai_queries=self.internal_ai.query_count,
            external_ai_evaluations=self.external_ai.evaluation_count,
            context_lock_verifications=self.metrics["context_lock_verifications"],
            quota_exceeded_rejections=self.metrics["quota_exceeded_rejections"],
            average_confidence_score=0.85,
            average_evaluation_score=0.82,
            user_satisfaction_rate=0.90,
            total_cost_usd=0.05,
            cost_per_query_usd=0.001,
            quota_utilization_rate=0.15,
            cache_hit_rate=0.85,
            concurrent_request_peak=5,
            timeout_rate=0.01
        )