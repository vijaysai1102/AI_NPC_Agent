import json
import re
from groq import Groq
from config.settings import GROQ_API_KEY, GROQ_MODEL

_client = None


def _get_client() -> Groq:
    global _client
    if _client is None:
        if not GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set. Add it to your .env file.")
        _client = Groq(api_key=GROQ_API_KEY)
    return _client


def generate_response(prompt: str) -> dict:
    client = _get_client()
    try:
        response = client.chat.completions.create(
            model=GROQ_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.85,
            max_tokens=1024
        )
        raw = response.choices[0].message.content.strip()
        return _parse_response(raw)
    except Exception as e:
        err = str(e)
        if "429" in err or "rate" in err.lower():
            raise QuotaExceededError("Groq rate limit hit. Wait a moment and try again.")
        raise


def _parse_response(raw: str) -> dict:
    cleaned = re.sub(r"```json\s*", "", raw)
    cleaned = re.sub(r"```\s*", "", cleaned).strip()
    # Fix invalid JSON: strip // comments
    cleaned = re.sub(r"//[^\n\"]*", "", cleaned)
    # Fix invalid JSON: +5 → 5 (JSON doesn't allow leading +)
    cleaned = re.sub(r":\s*\+(\d)", r": \1", cleaned)
    try:
        data = json.loads(cleaned)
        # Lowercase emotion_delta keys in case model capitalizes them
        raw_delta = data.get("emotion_delta", {})
        delta = {k.lower(): v for k, v in raw_delta.items()}
        return {
            "reply": data.get("reply", raw),
            "emotion_delta": delta,
            "memory_note": data.get("memory_note", "")
        }
    except (json.JSONDecodeError, ValueError):
        return {"reply": raw, "emotion_delta": {}, "memory_note": ""}


def ping() -> str:
    client = _get_client()
    response = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": "Say 'API connection successful' and nothing else."}],
        max_tokens=20
    )
    return response.choices[0].message.content.strip()


class QuotaExceededError(Exception):
    pass
