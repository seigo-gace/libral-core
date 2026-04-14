"""
KBE API Router
Knowledge Booster Engine APIエンドポイント
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from .core import kbe_core
from .federated import federated_learning
from .homomorphic import homomorphic_aggregator

router = APIRouter(prefix="/kbe", tags=["kbe"])


# === Request/Response Models ===

class KnowledgeSubmitRequest(BaseModel):
    """知識提出リクエスト"""
    user_id: str
    knowledge_type: str
    encrypted_data: str


class LearningTaskRequest(BaseModel):
    """学習タスクリクエスト"""
    model_type: str
    parameters: Dict[str, Any]


class LocalModelRequest(BaseModel):
    """ローカルモデル提出リクエスト"""
    user_id: str
    model_type: str
    weights: List[float]
    accuracy: float


class EncryptedModelRequest(BaseModel):
    """暗号化モデル提出リクエスト"""
    user_id: str
    encrypted_weights: str
    encryption_scheme: str = "mock_homomorphic"


# === Core Endpoints ===

@router.post("/submit-knowledge")
async def submit_knowledge(request: KnowledgeSubmitRequest):
    """知識提出"""
    try:
        record_id = kbe_core.submit_knowledge(
            request.user_id,
            request.knowledge_type,
            request.encrypted_data
        )
        return {"record_id": record_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_kbe_summary():
    """KBEサマリー"""
    try:
        return kbe_core.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Federated Learning Endpoints ===

@router.post("/federated/create-task")
async def create_learning_task(request: LearningTaskRequest):
    """学習タスク作成"""
    try:
        task_id = federated_learning.create_learning_task(
            request.model_type,
            request.parameters
        )
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/federated/submit-model")
async def submit_local_model(request: LocalModelRequest):
    """ローカルモデル提出"""
    try:
        model_id = federated_learning.submit_local_model(
            request.user_id,
            request.model_type,
            request.weights,
            request.accuracy
        )
        return {"model_id": model_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/federated/aggregated-weights/{model_type}")
async def get_aggregated_weights(model_type: str):
    """集約モデル重み取得"""
    try:
        weights = federated_learning.get_aggregated_weights(model_type)
        if weights is None:
            raise HTTPException(status_code=404, detail="No models found for this type")
        return {"model_type": model_type, "weights": weights}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/federated/summary")
async def get_federated_summary():
    """フェデレーテッド・ラーニングサマリー"""
    try:
        return federated_learning.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Homomorphic Encryption Endpoints ===

@router.post("/homomorphic/submit-encrypted")
async def submit_encrypted_model(request: EncryptedModelRequest):
    """暗号化モデル提出"""
    try:
        model_id = homomorphic_aggregator.submit_encrypted_model(
            request.user_id,
            request.encrypted_weights,
            request.encryption_scheme
        )
        return {"model_id": model_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/homomorphic/aggregate/{model_type}")
async def aggregate_encrypted(model_type: str):
    """暗号化集約実行"""
    try:
        result_id = homomorphic_aggregator.aggregate_encrypted(model_type)
        if result_id is None:
            raise HTTPException(status_code=404, detail="No encrypted models available")
        return {"result_id": result_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/homomorphic/result/{result_id}")
async def get_aggregation_result(result_id: str):
    """集約結果取得"""
    try:
        result = homomorphic_aggregator.get_aggregation_result(result_id)
        if result is None:
            raise HTTPException(status_code=404, detail="Result not found")
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/homomorphic/summary")
async def get_homomorphic_summary():
    """同型暗号サマリー"""
    try:
        return homomorphic_aggregator.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Dashboard Endpoint ===

@router.get("/dashboard")
async def get_kbe_dashboard():
    """KBE統合ダッシュボード"""
    try:
        return {
            "kbe_version": "1.0.0",
            "core": kbe_core.get_summary(),
            "federated_learning": federated_learning.get_summary(),
            "homomorphic_encryption": homomorphic_aggregator.get_summary(),
            "privacy_features": {
                "data_sovereignty": "Telegram Personal Log Servers",
                "encryption": "End-to-end encrypted knowledge submission",
                "federated_learning": "Local AI training, parameter sharing only",
                "homomorphic_aggregation": "Encrypted model aggregation"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
