# database/repositories/user_repository.py

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models.user import User
import uuid
import logging

logger = logging.getLogger(__name__)

class UserRepository:
    """
    Repository for User model.
    Handles all database operations for the 'users' table.
    """
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_user(self, username: str, email: str, hashed_password: str | None = None) -> User:
        """
        Creates a new user in the database.
        
        Args:
            username: Unique username
            email: Unique email address
            hashed_password: Optional hashed password (for future auth)
            
        Returns:
            User: The created user object
            
        Raises:
            IntegrityError: If username or email already exists
        """
        logger.info(f"Creating user: {username}")
        
        try:
            new_user = User(
                username=username,
                email=email,
                hashed_password=hashed_password,
                is_active=True
            )
            
            self.db.add(new_user)
            self.db.commit()
            self.db.refresh(new_user)
            
            logger.info(f"User created successfully: {new_user.id}")
            return new_user
            
        except IntegrityError as e:
            self.db.rollback()
            logger.error(f"Failed to create user '{username}': Username or email already exists")
            raise IntegrityError(
                statement=e.statement,
                params=e.params,
                orig=e.orig
            ) from e
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error creating user '{username}': {str(e)}")
            raise
    
    def get_user_by_id(self, user_id: uuid.UUID) -> User | None:
        """
        Retrieves a user by their UUID.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            User | None: The user object if found, None otherwise
        """
        logger.info(f"Fetching user by ID: {user_id}")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if user:
            logger.info(f"User found: {user.username}")
        else:
            logger.warning(f"User not found: {user_id}")
        
        return user
    
    def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieves a user by their username.
        
        Args:
            username: The username to search for
            
        Returns:
            User | None: The user object if found, None otherwise
        """
        logger.info(f"Fetching user by username: {username}")
        
        user = self.db.query(User).filter(User.username == username).first()
        
        if user:
            logger.info(f"User found: {user.username}")
        else:
            logger.warning(f"User not found: {username}")
        
        return user
    
    def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieves a user by their email.
        
        Args:
            email: The email to search for
            
        Returns:
            User | None: The user object if found, None otherwise
        """
        logger.info(f"Fetching user by email: {email}")
        
        user = self.db.query(User).filter(User.email == email).first()
        
        if user:
            logger.info(f"User found: {user.username}")
        else:
            logger.warning(f"User not found with email: {email}")
        
        return user
    
    def update_user(self, user_id: uuid.UUID, **kwargs) -> User | None:
        """
        Updates a user's attributes.
        
        Args:
            user_id: The user's UUID
            **kwargs: Attributes to update (e.g., username="new_name", is_active=False)
            
        Returns:
            User | None: The updated user object if found, None otherwise
        """
        logger.info(f"Updating user: {user_id}")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"User not found for update: {user_id}")
            return None
        
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
                logger.debug(f"Updated {key} for user {user_id}")
        
        try:
            self.db.commit()
            self.db.refresh(user)
            logger.info(f"User updated successfully: {user_id}")
            return user
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to update user {user_id}: {str(e)}")
            raise
    
    def delete_user(self, user_id: uuid.UUID) -> bool:
        """
        Deletes a user from the database.
        
        Args:
            user_id: The user's UUID
            
        Returns:
            bool: True if deleted, False if not found
        """
        logger.info(f"Deleting user: {user_id}")
        
        user = self.db.query(User).filter(User.id == user_id).first()
        
        if not user:
            logger.warning(f"User not found for deletion: {user_id}")
            return False
        
        try:
            self.db.delete(user)
            self.db.commit()
            logger.info(f"User deleted successfully: {user_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Failed to delete user {user_id}: {str(e)}")
            raise