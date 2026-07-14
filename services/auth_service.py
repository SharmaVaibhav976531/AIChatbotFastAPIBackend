# services/auth_service.py

import uuid
import logging
from datetime import datetime, timezone
from sqlalchemy.exc import IntegrityError

from database.repositories.user_repository import UserRepository
from core.security import hash_password, verify_password
from services.jwt_service import JWTService
from database.models.user import User

logger = logging.getLogger(__name__)


class AuthService:
    """
    Handles all authentication business logic.
    Injected with a UserRepository via FastAPI dependency injection.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def signup(self, username: str, email: str, password: str) -> dict:
        """
        Register a new user account.
        
        Steps:
            1. Check if username already exists → 409 Conflict
            2. Check if email already exists → 409 Conflict
            3. Hash the password using bcrypt
            4. Create the user in the database
            5. Generate access + refresh tokens
            6. Return user profile + tokens
            
        Args:
            username: Desired username
            email: User's email address
            password: Raw password (will be hashed)
            
        Returns:
            dict: Contains 'user', 'access_token', 'refresh_token'
            
        Raises:
            ValueError: If username or email already exists
        """
        logger.info(f"[AUTH] Signup attempt: username='{username}', email='{email}'")

        # 1. Check for duplicate username
        existing_user = self.user_repo.get_user_by_username(username)
        if existing_user:
            logger.warning(f"[AUTH] Signup FAILED: Username '{username}' already taken")
            raise ValueError(f"Username '{username}' is already taken")

        # 2. Check for duplicate email
        existing_email = self.user_repo.get_user_by_email(email)
        if existing_email:
            logger.warning(f"[AUTH] Signup FAILED: Email '{email}' already registered")
            raise ValueError(f"Email '{email}' is already registered")

        # 3. Hash the password
        hashed = hash_password(password)

        # 4. Create the user
        try:
            user = self.user_repo.create_user(
                username=username,
                email=email,
                hashed_password=hashed
            )
        except IntegrityError:
            logger.error(f"[AUTH] Signup FAILED: Database integrity error for '{username}'")
            raise ValueError("Username or email already exists")

        # 5. Generate tokens
        access_token = JWTService.create_access_token(user.id, user.username, user.email)
        refresh_token = JWTService.create_refresh_token(user.id)

        logger.info(f"[AUTH] ✅ Signup SUCCESS: user='{user.username}', id={user.id}")

        return {
            "user": user,
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def login(self, username: str, password: str) -> dict:
        """
        Authenticate a user and issue JWT tokens.
        
        The username field accepts EITHER a username or an email address.
        This provides a better UX — users can log in with whichever they remember.
        
        Steps:
            1. Try to find user by username
            2. If not found, try to find by email
            3. Verify password against stored hash
            4. Update last_login timestamp
            5. Generate and return tokens
            
        Args:
            username: Username or email address
            password: Raw password
            
        Returns:
            dict: Contains 'access_token', 'refresh_token'
            
        Raises:
            ValueError: If credentials are invalid
        """
        logger.info(f"[AUTH] Login attempt: '{username}'")

        # 1. Find user by username OR email
        user = self.user_repo.get_user_by_username(username)
        if not user:
            user = self.user_repo.get_user_by_email(username)

        # 2. User not found
        if not user:
            logger.warning(f"[AUTH] Login FAILED: User '{username}' not found")
            raise ValueError("Invalid username or password")

        # 3. Check if user has a password (guest users don't)
        if not user.hashed_password:
            logger.warning(f"[AUTH] Login FAILED: User '{username}' has no password set")
            raise ValueError("Invalid username or password")

        # 4. Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(f"[AUTH] Login FAILED: Invalid password for '{username}'")
            raise ValueError("Invalid username or password")

        # 5. Check if account is active
        if not user.is_active:
            logger.warning(f"[AUTH] Login FAILED: Account '{username}' is deactivated")
            raise ValueError("Account is deactivated. Contact support.")

        # 6. Update last_login timestamp
        self.user_repo.update_user(user.id, last_login=datetime.now(timezone.utc))

        # 7. Generate tokens
        access_token = JWTService.create_access_token(user.id, user.username, user.email)
        refresh_token = JWTService.create_refresh_token(user.id)

        logger.info(f"[AUTH] ✅ Login SUCCESS: user='{user.username}'")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
        }

    def refresh_tokens(self, refresh_token: str) -> dict:
        """
        Issue new tokens using a valid refresh token.
        
        This is the "silent re-authentication" flow. The frontend calls this
        when the access token expires, so the user doesn't have to log in again.
        
        Steps:
            1. Verify the refresh token (signature + expiration)
            2. Extract user_id from token claims
            3. Look up the user in the database (they may have been deactivated)
            4. Issue new access + refresh tokens
            
        Args:
            refresh_token: The refresh token from the client
            
        Returns:
            dict: Contains new 'access_token' and 'refresh_token'
            
        Raises:
            ValueError: If the refresh token is invalid or expired
        """
        logger.info("[AUTH] Token refresh attempt")

        # 1. Verify refresh token
        payload = JWTService.verify_refresh_token(refresh_token)
        if not payload:
            logger.warning("[AUTH] Token refresh FAILED: Invalid or expired refresh token")
            raise ValueError("Invalid or expired refresh token")

        # 2. Extract user_id
        user_id = payload.get("sub")
        if not user_id:
            logger.warning("[AUTH] Token refresh FAILED: No user_id in token")
            raise ValueError("Invalid refresh token")

        # 3. Look up user (they might have been deleted/deactivated since the token was issued)
        user = self.user_repo.get_user_by_id(uuid.UUID(user_id))
        if not user:
            logger.warning(f"[AUTH] Token refresh FAILED: User {user_id} not found")
            raise ValueError("User not found")

        if not user.is_active:
            logger.warning(f"[AUTH] Token refresh FAILED: User {user_id} is deactivated")
            raise ValueError("Account is deactivated")

        # 4. Issue new tokens
        new_access = JWTService.create_access_token(user.id, user.username, user.email)
        new_refresh = JWTService.create_refresh_token(user.id)

        logger.info(f"[AUTH] ✅ Token refresh SUCCESS: user='{user.username}'")

        return {
            "access_token": new_access,
            "refresh_token": new_refresh,
        }
