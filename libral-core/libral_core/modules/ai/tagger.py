"""
AutoTagger - Content to metadata and searchable tags (Sovereign Autarchy).
Uses Local LLM when available; falls back to rule-based tags.
"""

import json
import re
from typing import Any, Dict, List

TAG_MAX = 12
CATEGORIES = ("Work", "Personal", "Finance", "Health", "Idea", "Other")
PRIORITIES = ("High", "Medium", "Low")


def normalize_tag(t: str) -> str:
    t = re.sub(r"\s+", "", t.strip())
    if not t:
        return ""
    if not t.startswith("#"):
        t = "#" + t
    t = re.sub(r"[^#0-9A-Za-z\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\u31f0-\u31ff_]", "", t)
    return t[:40]


def rule_tags(text: str) -> List[str]:
    base = ["#uncategorized"]
    if "会議" in text or "mtg" in text.lower():
        base.append("#meeting")
    if "明日" in text:
        base.append("#tomorrow")
    if "請求" in text or "支払い" in text:
        base.append("#finance")
    if "健康" in text or "病院" in text:
        base.append("#health")
    if "アイデア" in text or "idea" in text.lower():
        base.append("#idea")
    return base[:TAG_MAX]


class AutoTagger:
    """Generate metadata and tags from content. LLM + rule fallback."""

    def __init__(self):
        try:
            from .worker import LocalLLMWorker
            self._worker = LocalLLMWorker()
        except Exception:
            self._worker = None

    async def generate_metadata(self, content: str, content_type: str = "text") -> Dict[str, Any]:
        system_prompt = (
            "Return JSON only. Keys:\n"
            "{\"summary\": string (max 50 chars), \"tags\": string[], "
            "\"category\": one of [Work, Personal, Finance, Health, Idea, Other], "
            "\"priority\": one of [High, Medium, Low]}\n"
            "No markdown. No extra keys."
        )
        raw = ""
        if self._worker:
            try:
                raw = await self._worker.infer(
                    user_prompt=content[:2000],
                    system_prompt=system_prompt,
                )
            except Exception:
                pass
        cleaned = (raw or "").replace("```json", "").replace("```", "").strip()
        try:
            obj = json.loads(cleaned)
            tags = [normalize_tag(t) for t in (obj.get("tags") or [])]
            tags = [t for t in tags if t][:TAG_MAX]
            if not tags:
                tags = rule_tags(content)
            cat = obj.get("category") or "Other"
            if cat not in CATEGORIES:
                cat = "Other"
            prio = obj.get("priority") or "Low"
            if prio not in PRIORITIES:
                prio = "Low"
            summary = (obj.get("summary") or content[:50]).strip()[:50]
            return {
                "summary": summary,
                "tags": tags,
                "category": cat,
                "priority": prio,
            }
        except Exception:
            pass
        return {
            "summary": (content[:50]).strip()[:50],
            "tags": rule_tags(content),
            "category": "Other",
            "priority": "Low",
        }
