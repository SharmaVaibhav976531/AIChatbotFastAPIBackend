# services/user_service.py

from services.cache_service import CacheService
import uuid
import logging
from database.repositories.user_repository import UserRepository
from database.models.user import User

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repo: UserRepository, cache_service: CacheService):
        self.user_repo = user_repo
        self.cache_service = cache_service

    def get_profile(self, user_id: uuid.UUID) -> User:
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def update_profile(self, user_id: uuid.UUID, username: str | None = None, email: str | None = None) -> User:
        logger.info(f"[USER] Profile update for user: {user_id}")

        # Build update dict with only provided fields
        updates = {}

        if username is not None:
            # Check uniqueness
            existing = self.user_repo.get_user_by_username(username)
            if existing and existing.id != user_id:
                raise ValueError(f"Username '{username}' is already taken")
            updates["username"] = username

        if email is not None:
            # Check uniqueness
            existing = self.user_repo.get_user_by_email(email)
            if existing and existing.id != user_id:
                raise ValueError(f"Email '{email}' is already registered")
            updates["email"] = email

        if not updates:
            logger.info("[USER] No fields to update")
            return self.get_profile(user_id)

        user = self.user_repo.update_user(user_id, **updates)
        if not user:
            raise ValueError("User not found")

        self.cache_service.invalidate_user_cache(str(user_id))
        
        logger.info(f"[USER] ✅ Profile updated and cache invalidated: {user.username}")
        return user
