from redis.asyncio import Redis, ConnectionPool

from .config import settings


redis_connection_poll = ConnectionPool.from_url(
    settings.REDIS_URL,
    max_connections=settings.MAX_CONNECTIONS_PER_PROCESS,
    decode_responses=True,
    socket_connect_timeout=settings.TCP_CONNECTION_ESTABLISHMENT_TIMEOUT
)


async def init_redis() -> Redis:
    """ Create a single Redis client (used in app's Startup) """
    try:
        _redis = Redis(connection_pool=redis_connection_poll)
        await _redis.ping()
    except Exception as e:
        print(e)  # ToDo: handle here later
        await _redis.close()
        _redis = None
        raise  # a custom connection failed exception

    return _redis


async def close_redis(redis: Redis) -> None:
    """close redis-client and redis-connection-poll (used in app's shutdown)"""
    await redis.close()
    await redis_connection_poll.disconnect()
