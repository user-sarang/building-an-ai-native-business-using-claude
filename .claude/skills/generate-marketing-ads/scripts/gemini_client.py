"""Shared Gemini client + config for the generate-marketing-ads skill.

Loads secrets from <repo>/secrets/.env (walks up to find it). No third-party
dotenv dependency — a tiny parser is built in. Only requires `google-genai`.

Env vars:
  GEMINI_API_KEY        (required)
  GEMINI_IMAGE_MODEL    creator model (default: gemini-3-pro-image)
  GEMINI_AUDIT_MODEL    reviewer vision model (default: gemini-2.5-flash)
"""
from __future__ import annotations

import os
from pathlib import Path


def _find_repo_root(start: Path) -> Path | None:
    """Walk upward looking for a secrets/.env file."""
    for parent in [start, *start.parents]:
        if (parent / "secrets" / ".env").exists():
            return parent
    return None


def load_env() -> None:
    """Load KEY=VALUE pairs from secrets/.env into os.environ (no overwrite)."""
    root = _find_repo_root(Path(__file__).resolve())
    if root is None:
        return
    env_path = root / "secrets" / ".env"
    for raw in env_path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        key, value = key.strip(), value.strip().strip('"').strip("'")
        os.environ.setdefault(key, value)


def get_api_key() -> str:
    load_env()
    key = os.environ.get("GEMINI_API_KEY", "").strip()
    if not key:
        raise SystemExit(
            "GEMINI_API_KEY is not set. Add it to secrets/.env "
            "(see secrets/.env.example)."
        )
    return key


def image_model() -> str:
    load_env()
    return os.environ.get("GEMINI_IMAGE_MODEL", "gemini-3-pro-image").strip()


def audit_model() -> str:
    load_env()
    return os.environ.get("GEMINI_AUDIT_MODEL", "gemini-2.5-flash").strip()


def get_client():
    """Return a configured google-genai Client."""
    try:
        from google import genai  # noqa: WPS433
    except ImportError as exc:  # pragma: no cover
        raise SystemExit(
            "The google-genai package is required. Install it with:\n"
            "  pip install google-genai --break-system-packages"
        ) from exc
    return genai.Client(api_key=get_api_key())
