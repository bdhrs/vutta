"""Shared environment lookup. Reads vutta/.env or honours environment vars."""

import os
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def load_env() -> dict:
    """Return a dict of env vars from .env (if present) overlaid with os.environ."""
    env: dict[str, str] = {}
    env_file = _REPO_ROOT / ".env"
    if env_file.exists():
        for line in env_file.read_text().splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, _, v = line.partition("=")
            env[k.strip()] = v.strip().strip('"').strip("'")
    for k, v in os.environ.items():
        env[k] = v
    return env


def canon_db_path() -> str:
    env = load_env()
    raw = env.get("VUTTA_CANON_DB") or env.get("VICAYA_CANON_DB")
    if not raw:
        raise RuntimeError(
            "Set VUTTA_CANON_DB in .env or environment "
            "(pointing to the tipitaka-translation-data SQLite file)."
        )
    return os.path.expanduser(raw)


def repo_root() -> Path:
    return _REPO_ROOT
