import json
from types import SimpleNamespace

import app.utils.ai as ai


def test_ai_analyze_skipped_when_no_key(monkeypatch):
    # Ensure GROQ_API_KEY is None
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "GROQ_API_KEY", None, raising=False)
    res = ai.ai_analyze("hello")
    assert res.get("skipped") is True


def test_ai_analyze_ok(monkeypatch):
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "GROQ_API_KEY", "test", raising=False)

    class FakeResp:
        status_code = 200

        def json(self):
            return {"choices": [{"message": {"content": "ok"}}]}

    def fake_post(url, json=None, headers=None, timeout=None):  # noqa: A002
        return FakeResp()

    monkeypatch.setattr(ai.requests, "post", fake_post)
    out = ai.ai_analyze("ping", system_prompt="sys", model="llama3-70b-8192")
    assert out["ok"] is True
    assert out["content"] == "ok"


def test_ai_analyze_non_200(monkeypatch):
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "GROQ_API_KEY", "test", raising=False)

    class FakeResp:
        status_code = 500

        def json(self):
            return {}

    monkeypatch.setattr(ai.requests, "post", lambda *a, **k: FakeResp())
    out = ai.ai_analyze("ping")
    assert out["ok"] is False
    assert out["status"] == 500


def test_ai_analyze_exception(monkeypatch):
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "GROQ_API_KEY", "test", raising=False)
    monkeypatch.setattr(ai.requests, "post", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    out = ai.ai_analyze("ping")
    assert out["ok"] is False
    assert "error" in out


def test_ai_analyze_unexpected_payload_structure(monkeypatch):
    from app.core import config as cfg

    monkeypatch.setattr(cfg.settings, "GROQ_API_KEY", "test", raising=False)

    class FakeResp:
        status_code = 200

        def json(self):
            # Missing choices[0].message.content to trigger fallback branch
            return {"foo": "bar", "choices": [{"delta": {"role": "assistant"}}]}

    monkeypatch.setattr(ai.requests, "post", lambda *a, **k: FakeResp())
    out = ai.ai_analyze("prompt")
    assert out["ok"] is True
    # content should be stringified data
    assert isinstance(out["content"], str)
