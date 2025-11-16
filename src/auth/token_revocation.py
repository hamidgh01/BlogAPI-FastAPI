import time

from redis.asyncio import Redis


class TokenRevocation:
    """
    Handle Token-Revocation strategy:
    revoke/blacklist non-expired tokens that should be useable anymore.
    (for example: when a user logs out, or get new-tokens using `renew_tokens`
    endpoint, its token in browser's cookie or frontend-app temp-memory
    will be deleted too; but the token itself is not expired and it can
    be misused -> so these tokens must be blacklisted until they expire)

    methods:
        put_in_blacklist() : put non-expired but used tokens in blacklist
        is_token_blacklisted() : check whether a token is blacklisted/revoked

    NOTE: Token-Revocation strategy is implemented using Redis DB
    """

    KEY_PREFIX = "jwt-bl:"  # blacklist-tokens prefix

    @staticmethod
    async def put_in_blacklist(payload: dict, redis: Redis):
        """
        params:
            - `payload` : extracted payload of the token to blacklist
            - `redis` : redis-client (async) to save token in Redis DB
        steps:
        1-  get token's "exp" (expiration timestamp) (payload["exp"]) and
            calculate TTL to save in Redis DB
        2-  get token's "jti" (payload["jti"]) -> key to blacklist a token
        3-  set a key="KEY_PREFIX:jti" with expire="ttl" in Redis DB
        """
        exp_ts = payload.get("exp")
        now = int(time.time())
        ttl = exp_ts - now
        if ttl <= 0:
            return  # nothing to do, token already expired

        jti = payload.get("jti")
        key = TokenRevocation._blacklist_key(jti)
        value = payload.get("user_id")
        await redis.set(key, str(value), ex=ttl)

    @staticmethod
    async def is_token_blacklisted(jti: str, redis: Redis) -> bool:
        key = TokenRevocation._blacklist_key(jti)
        return await redis.exists(key) == 1

    @staticmethod
    def _blacklist_key(jti: str) -> str:
        """ add KEY_PREFIX to jti to distinguish keys in Redis DB """
        return f"{TokenRevocation.KEY_PREFIX}{jti}"
