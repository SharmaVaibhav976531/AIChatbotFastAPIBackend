# services/jwt_service.py

import uuid
import logging
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError, ExpiredSignatureError
from core.settings import get_settings

logger = logging.getLogger(__name__)


class JWTService:
    """
    Stateless service for creating and verifying JWT tokens.
    All methods are static — no instance state needed.
    """

    @staticmethod
    def create_access_token(user_id: uuid.UUID, username: str, email: str) -> str:
        """
        Create a short-lived access token containing user claims.
        
        Claims (the data encoded in the token):
            sub: Subject — the user's UUID (standard JWT claim)
            username: The user's display name
            email: The user's email
            type: "access" — distinguishes from refresh tokens
            iat: Issued At — when the token was created
            exp: Expiration — when the token becomes invalid
            
        Args:
            user_id: The authenticated user's UUID
            username: The user's username
            email: The user's email
            
        Returns:
            str: The encoded JWT string
        """
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.access_token_expire_minutes)
        
        payload = {
            "sub": str(user_id),         # Subject: Who this token belongs to
            "username": username,         # User's display name
            "email": email,              # User's email
            "type": "access",            # Token type (access vs refresh)
            "iat": now,                  # Issued At
            "exp": expire,              # Expiration
        }
        
        token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
        logger.info(f"[JWT] Access token created for user: {username} (expires: {expire.strftime('%H:%M:%S')})")
        return token

    @staticmethod
    def create_refresh_token(user_id: uuid.UUID) -> str:
        """
        Create a long-lived refresh token.
        
        The refresh token intentionally contains FEWER claims than the access token.
        It only needs the user_id to issue a new access token. This minimizes the
        data exposed if the refresh token is compromised.
        
        Args:
            user_id: The authenticated user's UUID
            
        Returns:
            str: The encoded JWT refresh token string
        """
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=settings.refresh_token_expire_days)
        
        payload = {
            "sub": str(user_id),         # Subject: Who this token belongs to
            "type": "refresh",           # Token type
            "iat": now,                  # Issued At
            "exp": expire,              # Expiration
        }
        
        # IMPORTANT: Uses a DIFFERENT secret key than access tokens
        token = jwt.encode(payload, settings.jwt_refresh_secret_key, algorithm=settings.jwt_algorithm)
        logger.info(f"[JWT] Refresh token created for user: {user_id}")
        return token

    @staticmethod
    def verify_access_token(token: str) -> dict | None:
        """
        Verify and decode an access token.
        
        Verification steps:
        1. Decode the token using the secret key
        2. Check if the token has expired (jose does this automatically)
        3. Verify the token type is "access"
        4. Return the payload (claims) if valid
        
        Args:
            token: The JWT string from the Authorization header
            
        Returns:
            dict | None: The decoded payload if valid, None if invalid
        """
        settings = get_settings()
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            
            # Ensure this is an access token, not a refresh token
            if payload.get("type") != "access":
                logger.warning("[JWT] Token type mismatch — expected 'access'")
                return None
            
            logger.debug(f"[JWT] Access token verified for user: {payload.get('username')}")
            return payload
            
        except ExpiredSignatureError:
            logger.warning("[JWT] Access token EXPIRED")
            return None
        except JWTError as e:
            logger.warning(f"[JWT] Access token INVALID: {e}")
            return None

    @staticmethod
    def verify_refresh_token(token: str) -> dict | None:
        """
        Verify and decode a refresh token.
        
        Uses a DIFFERENT secret key than access tokens. This is a security measure:
        if the access token key is compromised, refresh tokens remain secure.
        
        Args:
            token: The JWT refresh token string
            
        Returns:
            dict | None: The decoded payload if valid, None if invalid
        """
        settings = get_settings()
        try:
            payload = jwt.decode(
                token, 
                settings.jwt_refresh_secret_key, 
                algorithms=[settings.jwt_algorithm]
            )
            
            # Ensure this is a refresh token, not an access token
            if payload.get("type") != "refresh":
                logger.warning("[JWT] Token type mismatch — expected 'refresh'")
                return None
            
            logger.debug(f"[JWT] Refresh token verified for user: {payload.get('sub')}")
            return payload
            
        except ExpiredSignatureError:
            logger.warning("[JWT] Refresh token EXPIRED")
            return None
        except JWTError as e:
            logger.warning(f"[JWT] Refresh token INVALID: {e}")
            return None
