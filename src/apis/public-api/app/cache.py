"""
Redis cache helper for the Public API.

Provides a simple get/set interface with:
- Graceful degradation: if Redis is unavailable, all operations are no-ops
  and the API falls back to hitting the DB normally.
- JSON serialization via FastAPI's jsonable_encoder (handles UUIDs, datetimes).
- Per-key TTL configuration.
"""

import json
import os

import redis
from fastapi.encoders import jsonable_encoder

from .logger import logger

REDIS_URL = os.getenv("REDIS_URL", "redis://redis:6379/0")

# TTLs (seconds)
TTL_RANKINGS = 120
TTL_LISTS = 60
TTL_DETAIL = 30


def _make_client():
    try:
        client = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=2)
        client.ping()
        logger.info("redis_connected", url=REDIS_URL)
        return client
    except Exception as exc:
        logger.warning("redis_unavailable", error=str(exc))
        return None


_client = _make_client()


def cache_get(key: str):
    """Return the cached value for *key*, or None on miss / Redis unavailable."""
    if _client is None:
        return None
    try:
        raw = _client.get(key)
        if raw is None:
            return None
        return json.loads(raw)
    except Exception as exc:
        logger.warning("cache_get_error", key=key, error=str(exc))
        return None


def cache_set(key: str, value, ttl: int) -> None:
    """Serialise *value* and store it under *key* with the given TTL in seconds."""
    if _client is None:
        return
    try:
        _client.setex(key, ttl, json.dumps(jsonable_encoder(value)))
    except Exception as exc:
        logger.warning("cache_set_error", key=key, error=str(exc))
