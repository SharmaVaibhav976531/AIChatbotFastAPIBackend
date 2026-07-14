# services/user_service.py

import uuid
import logging
from database.repositories.user_repository import UserRepository
from database.models.user import User

logger = logging.getLogger(__name__)


class UserService:
    """
    Handles user profile management operations.
    """

    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    def get_profile(self, user_id: uuid.UUID) -> User:
        """
        Retrieve a user's profile by ID.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            User: The user object
            
        Raises:
            ValueError: If user not found
        """
        user = self.user_repo.get_user_by_id(user_id)
        if not user:
            raise ValueError("User not found")
        return user

    def update_profile(self, user_id: uuid.UUID, username: str | None = None, email: str | None = None) -> User:
        """
        Update a user's profile fields.
        
        Only updates the fields that are provided (not None).
        Checks for uniqueness before updating username or email.
        
        Args:
            user_id: The user's UUID
            username: New username (optional)
            email: New email (optional)
            
        Returns:
            User: The updated user object
            
        Raises:
            ValueError: If username/email is taken or user not found
        """
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

        logger.info(f"[USER] ✅ Profile updated: {user.username}")
        return user
