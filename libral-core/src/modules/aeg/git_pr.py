"""
GitHub PR Generator
GitHub Pull Request自動生成機能

決定された優先度に基づき、GitHub上で自動でコード修正案（Pull Request）を作成
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from library.components import utc_now, generate_random_id


@dataclass
class PRTemplate:
    """PRテンプレート"""
    template_id: str
    title: str
    description: str
    branch_name: str
    file_changes: Dict[str, str]  # {filepath: change_description}
    labels: List[str]
    assignees: List[str]
    created_at: datetime


@dataclass
class GeneratedPR:
    """生成されたPR"""
    pr_id: str
    template_id: str
    github_pr_url: Optional[str]
    status: str  # "draft" | "submitted" | "merged" | "closed"
    created_at: datetime


class GitHubPRGenerator:
    """
    GitHub PR自動生成
    
    優先度決定AIの提案に基づき、PRを自動生成
    実際のGitHub APIとの統合は将来実装
    """
    
    def __init__(self):
        self.pr_templates: List[PRTemplate] = []
        self.generated_prs: List[GeneratedPR] = []
        self.github_integration_enabled = False  # Mock実装
    
    def create_pr_template(
        self,
        title: str,
        description: str,
        file_changes: Dict[str, str],
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None
    ) -> str:
        """
        PRテンプレート作成
        
        Args:
            title: PR タイトル
            description: PR 説明
            file_changes: 変更ファイル
            labels: ラベル
            assignees: アサイニー
        
        Returns:
            テンプレートID
        """
        # ブランチ名生成（タイトルから）
        branch_name = f"auto-improvement/{title.lower().replace(' ', '-')[:30]}"
        
        template = PRTemplate(
            template_id=generate_random_id(),
            title=title,
            description=description,
            branch_name=branch_name,
            file_changes=file_changes,
            labels=labels or ["auto-generated", "improvement"],
            assignees=assignees or [],
            created_at=utc_now()
        )
        
        self.pr_templates.append(template)
        
        # 最新20件のみ保持
        if len(self.pr_templates) > 20:
            self.pr_templates = self.pr_templates[-20:]
        
        return template.template_id
    
    def generate_pr(self, template_id: str) -> str:
        """
        PRを実際に生成（Mock実装）
        
        Args:
            template_id: テンプレートID
        
        Returns:
            PR ID
        """
        template = next((t for t in self.pr_templates if t.template_id == template_id), None)
        if not template:
            raise ValueError(f"Template {template_id} not found")
        
        pr = GeneratedPR(
            pr_id=generate_random_id(),
            template_id=template_id,
            github_pr_url=f"https://github.com/mock/repo/pull/{len(self.generated_prs) + 1}" if self.github_integration_enabled else None,
            status="draft",
            created_at=utc_now()
        )
        
        self.generated_prs.append(pr)
        
        # 最新50件のみ保持
        if len(self.generated_prs) > 50:
            self.generated_prs = self.generated_prs[-50:]
        
        return pr.pr_id
    
    def get_pr_status(self, pr_id: str) -> Optional[Dict[str, Any]]:
        """PR ステータス取得"""
        pr = next((p for p in self.generated_prs if p.pr_id == pr_id), None)
        if not pr:
            return None
        
        template = next((t for t in self.pr_templates if t.template_id == pr.template_id), None)
        
        return {
            "pr_id": pr.pr_id,
            "title": template.title if template else "Unknown",
            "status": pr.status,
            "github_url": pr.github_pr_url,
            "created_at": pr.created_at.isoformat()
        }
    
    def get_summary(self) -> Dict[str, Any]:
        """サマリー取得"""
        return {
            "github_integration_enabled": self.github_integration_enabled,
            "total_templates": len(self.pr_templates),
            "total_generated_prs": len(self.generated_prs),
            "pr_status_breakdown": {
                "draft": sum(1 for p in self.generated_prs if p.status == "draft"),
                "submitted": sum(1 for p in self.generated_prs if p.status == "submitted"),
                "merged": sum(1 for p in self.generated_prs if p.status == "merged"),
                "closed": sum(1 for p in self.generated_prs if p.status == "closed")
            }
        }


# グローバルインスタンス
github_pr_generator = GitHubPRGenerator()
