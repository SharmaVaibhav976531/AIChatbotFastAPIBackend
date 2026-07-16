# core/security.py

from passlib.context import CryptContext
import logging

logger = logging.getLogger(__name__)

# CryptContext is passlib's recommended way to manage hashing.
# schemes=["bcrypt"]: Use bcrypt as the only hashing algorithm.
# deprecated="auto": Automatically re-hash passwords if the algorithm changes in the future.
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain_password: str) -> str:
    """
    Hash a plaintext password using bcrypt.
    
    The bcrypt algorithm:
    1. Generates a random 16-byte salt
    2. Runs the Blowfish cipher 2^12 (4096) times (the "cost factor")
    3. Produces a 60-character hash string like: $2b$12$salt_hash_combined
    
    Args:
        plain_password: The raw password from the user
        
    Returns:
        str: The bcrypt hash (always 60 characters)
    """
    hashed = pwd_context.hash(plain_password)
    logger.debug("[SECURITY] Password hashed successfully")
    return hashed


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a plaintext password against a bcrypt hash.
    
    This extracts the salt from the stored hash, re-hashes the plain password
    with the same salt, and compares the results. This is a constant-time
    comparison to prevent timing attacks.
    
    Args:
        plain_password: The raw password from the login attempt
        hashed_password: The stored bcrypt hash from the database
        
    Returns:
        bool: True if the password matches, False otherwise
    """
    is_valid = pwd_context.verify(plain_password, hashed_password)
    if is_valid:
        logger.debug("[SECURITY] Password verification succeeded")
    else:
        logger.debug("[SECURITY] Password verification failed")
    return is_valid
