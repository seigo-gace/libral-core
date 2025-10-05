"""
AEG API Router
Auto Evolution Gateway APIエンドポイント
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from .core import aeg_core
from .prioritization import prioritization_ai
from .git_pr import github_pr_generator

router = APIRouter(prefix="/aeg", tags=["aeg"])


# === Request/Response Models ===

class EvolutionTaskRequest(BaseModel):
    """進化タスクリクエスト"""
    priority: int
    category: str
    description: str
    auto_generated: bool = True


class AnalysisRequest(BaseModel):
    """分析リクエスト"""
    health_score: float
    mttr_stats: Dict[str, Any]
    knowledge_base_insights: Dict[str, Any]


class PRTemplateRequest(BaseModel):
    """PRテンプレートリクエスト"""
    title: str
    description: str
    file_changes: Dict[str, str]
    labels: Optional[List[str]] = None
    assignees: Optional[List[str]] = None


# === Core Endpoints ===

@router.post("/create-task")
async def create_evolution_task(request: EvolutionTaskRequest):
    """進化タスク作成"""
    try:
        task_id = aeg_core.create_evolution_task(
            request.priority,
            request.category,
            request.description,
            request.auto_generated
        )
        return {"task_id": task_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_aeg_summary():
    """AEGサマリー"""
    try:
        return aeg_core.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Prioritization AI Endpoints ===

@router.post("/analyze-and-prioritize")
async def analyze_and_prioritize(request: AnalysisRequest):
    """分析と優先度決定"""
    try:
        suggestion_ids = prioritization_ai.analyze_and_prioritize(
            request.health_score,
            request.mttr_stats,
            request.knowledge_base_insights
        )
        return {"generated_suggestion_ids": suggestion_ids}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/top-priorities")
async def get_top_priorities(limit: int = 10):
    """優先度上位の提案取得"""
    try:
        return {"priorities": prioritization_ai.get_top_priorities(limit)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/prioritization/summary")
async def get_prioritization_summary():
    """優先度決定サマリー"""
    try:
        return prioritization_ai.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === GitHub PR Generator Endpoints ===

@router.post("/pr/create-template")
async def create_pr_template(request: PRTemplateRequest):
    """PRテンプレート作成"""
    try:
        template_id = github_pr_generator.create_pr_template(
            request.title,
            request.description,
            request.file_changes,
            request.labels,
            request.assignees
        )
        return {"template_id": template_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/pr/generate/{template_id}")
async def generate_pr(template_id: str):
    """PR生成"""
    try:
        pr_id = github_pr_generator.generate_pr(template_id)
        return {"pr_id": pr_id}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pr/status/{pr_id}")
async def get_pr_status(pr_id: str):
    """PRステータス取得"""
    try:
        status = github_pr_generator.get_pr_status(pr_id)
        if status is None:
            raise HTTPException(status_code=404, detail="PR not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/pr/summary")
async def get_pr_summary():
    """PR生成サマリー"""
    try:
        return github_pr_generator.get_summary()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === Dashboard Endpoint ===

@router.get("/dashboard")
async def get_aeg_dashboard():
    """AEG統合ダッシュボード"""
    try:
        return {
            "aeg_version": "1.0.0",
            "core": aeg_core.get_summary(),
            "prioritization_ai": prioritization_ai.get_summary(),
            "github_pr_generator": github_pr_generator.get_summary(),
            "evolution_capabilities": {
                "auto_prioritization": "AI-driven development priority decisions",
                "github_integration": "Automated Pull Request generation",
                "knowledge_based": "Collective intelligence from KBE",
                "health_driven": "LPO health score guided improvements"
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
