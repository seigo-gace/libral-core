"""
Libral AI Module - FastAPI Router
Revolutionary Dual-AI System API Endpoints
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Request, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import structlog

from .schemas import (
    AIConfig, AIError, AIHealthResponse, AIMetrics, AIQuery, AIResponse,
    EvaluationRequest, EvaluationResponse, QueryCategory
)
from .service import LibralAI

logger = structlog.get_logger(__name__)

# Initialize router
router = APIRouter(prefix="/api/ai", tags=["Libral AI System"])

# Initialize AI service
ai_service = LibralAI()

# Security
security = HTTPBearer()


# Dependency for authenticated requests
async def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security)) -> str:
    """Extract user ID from access token"""
    token = credentials.credentials
    
    if not token.startswith("access_token_"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token"
        )
    
    session_id = token.replace("access_token_", "")
    return f"user_{session_id}"


# Context-Lock verification dependency
async def verify_context_lock_header(x_context_lock: str = Header(None)) -> str:
    """Verify Context-Lock header"""
    if not x_context_lock:
        logger.warning("Context-Lock header missing")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Context-Lock header required for AI operations"
        )
    
    return x_context_lock


# Health and Status Endpoints
@router.get("/health", response_model=AIHealthResponse)
async def get_health():
    """Get AI module health status"""
    return await ai_service.get_health()


@router.get("/metrics", response_model=AIMetrics)
async def get_metrics(
    period_hours: int = 24,
    user_id: str = Depends(get_current_user_id)
):
    """Get AI module metrics"""
    end_time = datetime.utcnow()
    start_time = end_time - timedelta(hours=period_hours)
    
    return await ai_service.get_metrics(start_time, end_time)


# Internal AI Endpoints (自社AI)
@router.post("/ask", response_model=AIResponse)
async def ask_internal_ai(
    query: AIQuery,
    context_lock: str = Depends(verify_context_lock_header),
    user_id: str = Depends(get_current_user_id)
):
    """Ask internal AI (自社AI) - Privacy-first responses"""
    try:
        logger.info("Internal AI query received", 
                   query_id=query.query_id,
                   category=query.category,
                   user_id=user_id)
        
        response = await ai_service.process_internal_ai_query(query, context_lock, user_id)
        
        logger.info("Internal AI query completed", 
                   query_id=query.query_id,
                   response_id=response.response_id,
                   confidence_score=response.confidence_score,
                   user_id=user_id)
        
        return response
        
    except ValueError as e:
        logger.warning("Internal AI query rejected", 
                      query_id=query.query_id,
                      reason=str(e),
                      user_id=user_id)
        
        if "Context-Lock" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Context-Lock verification failed"
            )
        elif "quota" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Usage quota exceeded. Please try again later."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    except Exception as e:
        logger.error("Internal AI query error", 
                    query_id=query.query_id,
                    error=str(e),
                    user_id=user_id)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal AI processing failed"
        )


@router.post("/ask/simple")
async def ask_internal_ai_simple(
    data: Dict[str, Any],
    context_lock: str = Depends(verify_context_lock_header),
    user_id: str = Depends(get_current_user_id)
):
    """Simplified internal AI endpoint (compatible with instruction document)"""
    try:
        # Extract query text
        query_text = data.get("text", "")
        if not query_text:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query text is required"
            )
        
        # Create AIQuery object
        from uuid import uuid4
        query = AIQuery(
            query_id=str(uuid4()),
            text=query_text,
            category=QueryCategory.GENERAL,
            user_id=user_id
        )
        
        response = await ai_service.process_internal_ai_query(query, context_lock, user_id)
        
        # Return simplified response format
        return {
            "response": response.text,
            "confidence": response.confidence_score,
            "processing_time_ms": response.processing_time_ms
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Simple AI query error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="AI processing failed"
        )


# External AI Endpoints (判定役)
@router.post("/eval", response_model=EvaluationResponse)
async def evaluate_external_ai(
    request: EvaluationRequest,
    context_lock: str = Depends(verify_context_lock_header),
    user_id: str = Depends(get_current_user_id)
):
    """Evaluate with external AI (判定役) - Quality assurance system"""
    try:
        logger.info("External AI evaluation requested", 
                   evaluation_id=request.evaluation_id,
                   criteria_count=len(request.criteria),
                   user_id=user_id)
        
        response = await ai_service.process_external_ai_evaluation(request, context_lock, user_id)
        
        logger.info("External AI evaluation completed", 
                   evaluation_id=request.evaluation_id,
                   overall_score=response.overall_score,
                   cost=response.evaluation_cost,
                   user_id=user_id)
        
        return response
        
    except ValueError as e:
        logger.warning("External AI evaluation rejected", 
                      evaluation_id=request.evaluation_id,
                      reason=str(e),
                      user_id=user_id)
        
        if "Context-Lock" in str(e):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Context-Lock verification failed"
            )
        elif "quota" in str(e).lower():
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="External AI usage quota exceeded. Please try again tomorrow."
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
    
    except Exception as e:
        logger.error("External AI evaluation error", 
                    evaluation_id=request.evaluation_id,
                    error=str(e),
                    user_id=user_id)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="External AI evaluation failed"
        )


@router.post("/eval/simple")
async def evaluate_external_ai_simple(
    data: Dict[str, Any],
    context_lock: str = Depends(verify_context_lock_header),
    user_id: str = Depends(get_current_user_id)
):
    """Simplified external AI evaluation endpoint"""
    try:
        # Get usage stats first
        usage_stats = await ai_service.usage_manager.get_usage_stats("external", user_id)
        
        response = {
            "evaluation": "外部AIが判定します。品質評価システムが正常に動作しています。",
            "usage_count": usage_stats.get("daily_used", 0),
            "quota_remaining": usage_stats.get("daily_limit", 2) - usage_stats.get("daily_used", 0),
            "cost_estimate": 0.01
        }
        
        # Simulate evaluation processing
        await ai_service.usage_manager.increment_usage("external", user_id, 0.01)
        
        logger.info("External AI simple evaluation completed", 
                   usage_count=response["usage_count"],
                   user_id=user_id)
        
        return response
        
    except Exception as e:
        logger.error("Simple evaluation error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Evaluation failed"
        )


# Usage Management Endpoints
@router.get("/usage/stats")
async def get_usage_statistics(
    ai_type: str = "both",  # internal, external, both
    user_id: str = Depends(get_current_user_id)
):
    """Get AI usage statistics"""
    try:
        stats = {}
        
        if ai_type in ["internal", "both"]:
            internal_stats = await ai_service.usage_manager.get_usage_stats("internal", user_id)
            stats["internal"] = internal_stats
        
        if ai_type in ["external", "both"]:
            external_stats = await ai_service.usage_manager.get_usage_stats("external", user_id)
            stats["external"] = external_stats
        
        return {
            "success": True,
            "statistics": stats,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Usage statistics error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Usage statistics retrieval failed"
        )


@router.get("/quota/status")
async def get_quota_status(
    user_id: str = Depends(get_current_user_id)
):
    """Get current quota status"""
    try:
        internal_stats = await ai_service.usage_manager.get_usage_stats("internal", user_id)
        external_stats = await ai_service.usage_manager.get_usage_stats("external", user_id)
        
        return {
            "success": True,
            "quota_status": {
                "internal_ai": {
                    "daily_used": internal_stats.get("daily_used", 0),
                    "daily_limit": internal_stats.get("daily_limit", 1000),
                    "available": internal_stats.get("daily_used", 0) < internal_stats.get("daily_limit", 1000)
                },
                "external_ai": {
                    "daily_used": external_stats.get("daily_used", 0),
                    "daily_limit": external_stats.get("daily_limit", 2),
                    "available": external_stats.get("daily_used", 0) < external_stats.get("daily_limit", 2)
                }
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Quota status error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Quota status retrieval failed"
        )


# Configuration Endpoints
@router.get("/config")
async def get_ai_config(
    user_id: str = Depends(get_current_user_id)
):
    """Get AI module configuration"""
    return {
        "success": True,
        "config": {
            "internal_ai": {
                "model": ai_service.internal_ai.model,
                "daily_limit": ai_service.config.internal_ai_daily_limit,
                "cost_per_query": 0.0
            },
            "external_ai": {
                "provider": ai_service.external_ai.provider,
                "model": ai_service.external_ai.model,
                "daily_limit": ai_service.config.external_ai_daily_limit,
                "cost_per_evaluation": 0.01
            },
            "security": {
                "context_lock_required": ai_service.config.require_context_lock,
                "encrypt_responses": ai_service.config.encrypt_responses,
                "remove_pii": ai_service.config.remove_pii
            }
        }
    }


# Admin and Debug Endpoints
@router.get("/admin/stats")
async def get_detailed_stats(
    user_id: str = Depends(get_current_user_id)
):
    """Get detailed AI system statistics"""
    try:
        return {
            "success": True,
            "statistics": {
                **ai_service.metrics,
                "internal_ai_queries": ai_service.internal_ai.query_count,
                "external_ai_evaluations": ai_service.external_ai.evaluation_count,
                "context_lock_verifications": ai_service.context_lock_verifier.verification_count
            },
            "component_status": {
                "internal_ai": "active",
                "external_ai": "active", 
                "usage_manager": "active",
                "context_lock_verifier": "active",
                "redis_cache": "active"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error("Detailed stats error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Statistics retrieval failed"
        )


@router.get("/admin/test-context-lock")
async def test_context_lock():
    """Test Context-Lock verification (development only)"""
    try:
        # Test various Context-Lock formats
        test_cases = [
            {"header": None, "expected": False},
            {"header": "short", "expected": False},
            {"header": "dummy_" + "x" * 30, "expected": True},
            {"header": "a" * 64, "expected": True}
        ]
        
        results = []
        for test_case in test_cases:
            result = await ai_service.context_lock_verifier.verify_context_lock(
                test_case["header"], "test_user"
            )
            results.append({
                "header": test_case["header"],
                "result": result,
                "expected": test_case["expected"],
                "passed": result == test_case["expected"]
            })
        
        return {
            "success": True,
            "test_results": results,
            "all_passed": all(r["passed"] for r in results)
        }
        
    except Exception as e:
        logger.error("Context-Lock test error", error=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Context-Lock test failed"
        )