import logging
from typing import Any, Dict, Optional

import requests

from app.core.config import settings

logger = logging.getLogger(__name__)


def ai_analyze(prompt: str, system_prompt: Optional[str] = None, model: str = "llama3-70b-8192") -> Dict[str, Any]:
    """
    Call Groq (OpenAI-compatible) chat completions API with a simple prompt.
    Returns a small normalized dict with ok/content fields.

    Behavior:
    - If GROQ_API_KEY is not set: returns {"skipped": True} to allow offline use.
    - On HTTP 200: returns {"ok": True, "content": <string>}.
    - Otherwise: returns {"ok": False, "status": <code>}.
    """
    if not settings.GROQ_API_KEY:
        logger.info("GROQ_API_KEY not set; skipping AI call")
        return {"skipped": True}

    headers = {
        "Authorization": f"Bearer {settings.GROQ_API_KEY}",
        "Content-Type": "application/json",
    }
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        # Keep it minimal; tune as needed
        "temperature": 0.2,
        "stream": False,
    }

    try:
        resp = requests.post(settings.GROQ_API_URL, json=payload, headers=headers, timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            # Align with OpenAI-like schema: choices[0].message.content
            content = None
            try:
                content = data["choices"][0]["message"]["content"]
            except Exception:  # noqa: BLE001
                content = str(data)
            return {"ok": True, "content": content, "model": model}
        else:
            logger.warning("Groq API returned %s", resp.status_code)
            return {"ok": False, "status": resp.status_code}
    except Exception as e:  # noqa: BLE001
        logger.exception("Error calling Groq API: %s", e)
        return {"ok": False, "error": str(e)}
