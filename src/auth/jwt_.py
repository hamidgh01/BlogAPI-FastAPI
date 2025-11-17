from typing import Literal, Any
import uuid
from datetime import datetime, timezone, timedelta

import jwt
from jwt.exceptions import PyJWTError
from redis.asyncio import Redis

from src.core.config import settings
from ._exceptions import JWTDecodeError, TokenError
from .token_revocation import TokenRevocation


class JWTHandler:
    """
    Handle JWT operations
    methods:
        generate_token()    : is used to generate an access/refresh token
        get_token_payload() : is used to extract a token's payload
    """

    SECRET_KEY = settings.JWT_SECRET_KEY
    ALGORITHM = settings.JWT_ALGORITHM
    access_token_expire_minutes = settings.ACCESS_TOKEN_EXPIRE_MINUTES
    refresh_token_expire_minutes = settings.REFRESH_TOKEN_EXPIRE_MINUTES

    @staticmethod
    def generate_token(
        user_id: int, token_type: Literal["access", "refresh"],
    ) -> str:
        match token_type:
            case "access":
                return JWTHandler._encode(
                    user_id, "access", JWTHandler.access_token_expire_minutes
                )
            case "refresh":
                return JWTHandler._encode(
                    user_id, "refresh", JWTHandler.refresh_token_expire_minutes
                )

    @staticmethod
    def get_token_payload(
        token: str, token_type: Literal["access", "refresh"], redis: Redis
    ) -> dict[str, Any]:
        payload = JWTHandler._decode(token, token_type, redis)
        return payload

    @staticmethod
    def _encode(
        user_id: int,
        token_type: Literal["access", "refresh"],
        token_expire_minutes: int
    ) -> str:
        """
        params:
            - `user_id` : id of the user-obj for token
            - `token_type` : intended type of token to generate
            - `token_expire_minutes` : refresh/access expire_minutes
        steps:
        1-  generate a 'jti' (uuid4) (jti: jwtID -> Unique ID for token)
        2-  calculate 'token-expiration'
        3-  build a "payload" dict with needed fields to encode
        4-  encode "payload" to generate token and return it
        """
        jti = str(uuid.uuid4())
        utc_now = datetime.now(timezone.utc)
        expires_at = utc_now + timedelta(minutes=token_expire_minutes)
        payload = {
            "jti": jti,
            "type": token_type,
            "user_id": user_id,
            "iat": utc_now,
            "exp": expires_at
        }
        return jwt.encode(payload, JWTHandler.SECRET_KEY, JWTHandler.ALGORITHM)

    @staticmethod
    def _decode(
        token: str,
        type_must_be: Literal["access", "refresh"],
        redis: Redis
    ) -> dict[str, Any]:
        """
        params:
            - `token` : token to decode (and extracting its payload)
            - `type_must_be` : intended type of token
            - `redis` : redis-client (async) to check if token is blacklisted
        steps:
        1-  decode `token` to extract its "payload" -> (raise a Custom
            'JWTDecodeError') if there's a problem in decoding process
        2-  analyze extracted "payload" -> raise a Custom 'TokenError' if
            token: "is expired" or "has not-intended type" or "is blacklisted"
        3-  return extracted "payload" if everything is ok
        """
        try:
            payload = jwt.decode(
                token, JWTHandler.SECRET_KEY, JWTHandler.ALGORITHM
            )
            # check token expiration:
            utc_now_ts = datetime.now(timezone.utc).timestamp()
            token_expire_ts = payload.get("exp", None)
            if (token_expire_ts is None) or utc_now_ts > token_expire_ts:
                raise TokenError("token expired.")
            # check token type:
            token_type = payload.get("type")
            if token_type != type_must_be:
                raise TokenError("invalid token type.")
            # check token is blacklisted or not:
            jti = payload.get("jti")
            if TokenRevocation.is_token_blacklisted(jti, redis):
                raise TokenError("token revoked.")

            return payload

        except PyJWTError as err:
            raise JWTDecodeError(f"{err.__class__.__name__}: {err}") from err
