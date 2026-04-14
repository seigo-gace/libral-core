"""AutoTagger and infer_local request validation (Sovereign Autarchy)."""
import pytest
from pydantic import ValidationError

from libral_core.modules.ai.tagger import normalize_tag, rule_tags, TAG_MAX


def test_normalize_tag():
    assert normalize_tag("  meeting  ") == "#meeting"
    assert normalize_tag("meeting") == "#meeting"
    assert normalize_tag("#idea") == "#idea"
    assert normalize_tag("") == ""
    assert len(normalize_tag("a" * 50)) <= 40


def test_rule_tags():
    tags = rule_tags("明日の会議は10時から")
    assert "#meeting" in tags or "#tomorrow" in tags
    assert len(tags) <= TAG_MAX
    tags_fin = rule_tags("請求書を確認")
    assert "#finance" in tags_fin


@pytest.mark.asyncio
async def test_auto_tagger_generate_metadata_fallback():
    from libral_core.modules.ai.tagger import AutoTagger
    tagger = AutoTagger()
    out = await tagger.generate_metadata("明日の会議はZoomで", "text")
    assert "summary" in out
    assert "tags" in out
    assert "category" in out
    assert "priority" in out
    assert isinstance(out["tags"], list)
    assert out["category"] in ("Work", "Personal", "Finance", "Health", "Idea", "Other")


def test_infer_local_request_validation():
    """InferLocalRequest: prompt length limit (DoS prevention)."""
    from libral_core.modules.ai.schemas import InferLocalRequest, INFER_LOCAL_PROMPT_MAX
    req = InferLocalRequest(prompt="Hi")
    assert req.prompt == "Hi"
    with pytest.raises(ValidationError):
        InferLocalRequest(prompt="x" * (INFER_LOCAL_PROMPT_MAX + 1))
    with pytest.raises(ValidationError):
        InferLocalRequest(prompt="")
