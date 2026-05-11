"""
Redis caching utility for Public API.

This module provides a caching layer to minimize database hits by storing
frequently accessed data in Redis with configurable TTLs.
"""

import json
import os
from functools import wraps
from typing import Any, Callable, Optional
from uuid import UUID

import redis
from taca_logging import get_logger

logger = get_logger("public-api.cache")

# Cache configuration
REDIS_HOST = os.getenv("REDIS_HOST", "redis")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))
CACHE_ENABLED = os.getenv("CACHE_ENABLED", "true").lower() == "true"

# TTL configurations (in seconds)
CACHE_TTL = {
    "team": 3600,  # 1 hour
    "team_list": 1800,  # 30 minutes
    "student": 3600,  # 1 hour
    "student_list": 1800,  # 30 minutes
    "tournament": 3600,  # 1 hour
    "tournament_list": 60,  # 1 minute
    "match": 1800,  # 30 minutes
    "match_list": 30,  # 30 seconds
    "ranking": 60,  # 1 minute
    "modality": 3600,  # 1 hour
    "nucleo": 3600,  # 1 hour
    "nucleo_list": 7200,  # 2 hours
    "regulation": 7200,  # 2 hours
}

# Redis client instance
_redis_client: Optional[redis.Redis] = None


def get_redis_client() -> Optional[redis.Redis]:
    """
    Get or create Redis client instance.

    Returns:
        Redis client instance or None if cache is disabled
    """
    global _redis_client

    if not CACHE_ENABLED:
        return None

    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True,
                socket_connect_timeout=5,
                socket_keepalive=True,
                retry_on_timeout=True,
                connection_pool=redis.ConnectionPool(
                    host=REDIS_HOST,
                    port=REDIS_PORT,
                    db=REDIS_DB,
                    max_connections=100,
                ),
            )
            # Test connection
            _redis_client.ping()
            logger.info("redis_connected", host=REDIS_HOST, port=REDIS_PORT)
        except Exception as e:
            logger.error(
                "redis_connection_failed",
                error=str(e),
                host=REDIS_HOST,
                port=REDIS_PORT,
            )
            _redis_client = None

    return _redis_client


def clear_redis_cache():
    """Clear all cache entries (use with caution)."""
    client = get_redis_client()
    if client:
        try:
            client.flushdb()
            logger.info("redis_cache_cleared")
        except Exception as e:
            logger.error("redis_clear_failed", error=str(e))


def json_serializer(obj: Any) -> Any:
    """
    Serialize objects to JSON-compatible format.

    Handles:
    - UUID objects -> converted to string
    - SQLAlchemy ORM models -> converted to dict
    - datetime objects -> converted to ISO format string
    - Other objects with __dict__ -> converted to dict (private attrs excluded)
    """
    if isinstance(obj, UUID):
        return str(obj)

    # Handle SQLAlchemy model instances with __table__ attribute
    if hasattr(obj, "__table__"):
        result = {}
        try:
            for col in obj.__table__.columns:
                val = getattr(obj, col.name, None)
                if isinstance(val, UUID):
                    result[col.name] = str(val)
                elif hasattr(val, "isoformat"):  # datetime objects
                    result[col.name] = val.isoformat()
                else:
                    result[col.name] = val
            return result
        except Exception as e:
            logger.warning(
                "sqlalchemy_serialization_failed",
                error=str(e),
                object_type=type(obj).__name__,
            )

    # For other objects with __dict__, convert to dict excluding private attributes
    if hasattr(obj, "__dict__"):
        try:
            result = {}
            for key, value in vars(obj).items():
                if not key.startswith("_"):
                    if isinstance(value, UUID):
                        result[key] = str(value)
                    elif hasattr(value, "isoformat"):
                        result[key] = value.isoformat()
                    else:
                        result[key] = value
            return result
        except (TypeError, ValueError):
            pass

    # Last resort - convert to string
    return str(obj)


class CacheKeyGenerator:
    """Generate cache keys for different entity types."""

    @staticmethod
    def team(team_id: UUID) -> str:
        """Cache key for a single team by ID."""
        return f"team:{team_id}"

    @staticmethod
    def team_list(
        skip: int = 0,
        limit: int = 50,
        course_id: Optional[UUID] = None,
        nucleo_id: Optional[UUID] = None,
        modality_id: Optional[UUID] = None,
    ) -> str:
        """Cache key for team list with filters."""
        filters = f"course={course_id}:nucleo={nucleo_id}:modality={modality_id}"
        return f"team:list:{skip}:{limit}:{filters}"

    @staticmethod
    def student(student_id: UUID) -> str:
        """Cache key for a single student by ID."""
        return f"student:{student_id}"

    @staticmethod
    def student_by_number(student_number: str) -> str:
        """Cache key for student by number."""
        return f"student:number:{student_number}"

    @staticmethod
    def student_list(
        skip: int = 0,
        limit: int = 50,
        course_id: Optional[UUID] = None,
        nucleo_id: Optional[UUID] = None,
        is_member: Optional[bool] = None,
        search: Optional[str] = None,
    ) -> str:
        """Cache key for student list with filters."""
        filters = (
            f"course={course_id}:nucleo={nucleo_id}:member={is_member}:search={search}"
        )
        return f"student:list:{skip}:{limit}:{filters}"

    @staticmethod
    def tournament(tournament_id: UUID) -> str:
        """Cache key for a single tournament by ID."""
        return f"tournament:{tournament_id}"

    @staticmethod
    def tournament_list(
        skip: int = 0,
        limit: int = 50,
        modality_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> str:
        """Cache key for tournament list with filters."""
        filters = f"modality={modality_id}:status={status}"
        return f"tournament:list:{skip}:{limit}:{filters}"

    @staticmethod
    def match(match_id: UUID) -> str:
        """Cache key for a single match by ID."""
        return f"match:{match_id}"

    @staticmethod
    def match_list(
        skip: int = 0,
        limit: int = 50,
        tournament_id: Optional[UUID] = None,
        status: Optional[str] = None,
    ) -> str:
        """Cache key for match list with filters."""
        filters = f"tournament={tournament_id}:status={status}"
        return f"match:list:{skip}:{limit}:{filters}"

    @staticmethod
    def ranking(ranking_type: str, ranking_id: UUID) -> str:
        """Cache key for ranking (general or modality)."""
        return f"ranking:{ranking_type}:{ranking_id}"

    @staticmethod
    def ranking_list(ranking_type: str, skip: int = 0, limit: int = 100) -> str:
        """Cache key for ranking list."""
        return f"ranking:{ranking_type}:list:{skip}:{limit}"

    @staticmethod
    def nucleo(nucleo_id: UUID) -> str:
        """Cache key for a single nucleo by ID."""
        return f"nucleo:{nucleo_id}"

    @staticmethod
    def nucleo_list(skip: int = 0, limit: int = 100) -> str:
        """Cache key for nucleo list."""
        return f"nucleo:list:{skip}:{limit}"

    @staticmethod
    def modality(modality_id: UUID) -> str:
        """Cache key for modality."""
        return f"modality:{modality_id}"

    @staticmethod
    def regulation(regulation_id: UUID) -> str:
        """Cache key for regulation."""
        return f"regulation:{regulation_id}"


def cached(
    cache_key: str,
    ttl: int = 3600,
    key_builder: Optional[Callable] = None,
) -> Callable:
    """
    Decorator for caching function results in Redis.

    Args:
        cache_key: Base cache key (if key_builder is provided, this is ignored)
        ttl: Time to live in seconds
        key_builder: Optional function to dynamically build cache key from function args

    Returns:
        Decorated function with caching
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            client = get_redis_client()

            # Skip cache if disabled or client unavailable
            if client is None:
                return func(*args, **kwargs)

            try:
                # Build cache key
                if key_builder:
                    final_key = key_builder(*args, **kwargs)
                else:
                    final_key = cache_key

                # Try to get from cache
                cached_value = client.get(final_key)
                if cached_value is not None:
                    logger.debug(
                        "cache_hit",
                        key=final_key,
                        function=func.__name__,
                    )
                    return json.loads(cached_value)

                # Cache miss - call function
                result = func(*args, **kwargs)

                # Store in cache
                try:
                    serialized = json.dumps(
                        result,
                        default=json_serializer,
                        separators=(",", ":"),
                    )
                    client.setex(final_key, ttl, serialized)
                    logger.debug(
                        "cache_set",
                        key=final_key,
                        ttl=ttl,
                        function=func.__name__,
                    )
                except Exception as e:
                    logger.warning(
                        "cache_serialization_failed",
                        function=func.__name__,
                        error=str(e),
                    )

                return result

            except Exception as e:
                logger.warning(
                    "cache_operation_failed",
                    function=func.__name__,
                    error=str(e),
                )
                # On error, bypass cache and call function directly
                return func(*args, **kwargs)

        return wrapper

    return decorator


def invalidate_cache(pattern: str = "*") -> None:
    """
    Invalidate cache entries matching a pattern.

    Args:
        pattern: Redis key pattern to match (e.g., "team:*" or "*")
    """
    client = get_redis_client()
    if client is None:
        return

    try:
        keys = client.keys(pattern)
        if keys:
            client.delete(*keys)
            logger.info(
                "cache_invalidated",
                pattern=pattern,
                keys_deleted=len(keys),
            )
    except Exception as e:
        logger.error(
            "cache_invalidation_failed",
            pattern=pattern,
            error=str(e),
        )


def invalidate_entity_cache(entity_type: str, entity_id: Optional[UUID] = None) -> None:
    """
    Invalidate cache for a specific entity type.

    Args:
        entity_type: Type of entity (team, student, tournament, etc.)
        entity_id: Optional specific entity ID (if not provided, clears entire entity type)
    """
    if entity_id:
        # Clear specific entity and related lists
        invalidate_cache(f"{entity_type}:{entity_id}*")
        invalidate_cache(f"{entity_type}:list:*")
    else:
        # Clear entire entity type
        invalidate_cache(f"{entity_type}:*")


def get_cache_stats() -> dict:
    """Get cache statistics."""
    client = get_redis_client()
    if client is None:
        return {"status": "disabled"}

    try:
        info = client.info()
        return {
            "status": "enabled",
            "memory_used": info.get("used_memory_human", "N/A"),
            "connected_clients": info.get("connected_clients", 0),
            "total_commands": info.get("total_commands_processed", 0),
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}
