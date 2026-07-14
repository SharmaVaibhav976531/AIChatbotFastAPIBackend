# api/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from schemas.auth import (
    SignupRequest, LoginRequest, RefreshTokenRequest,
    UpdateProfileRequest, TokenResponse, UserProfileResponse,
    SignupResponse, MessageResponse
)
from services.auth_service import AuthService
from services.user_service import UserService
from database.models.user import User
from app.dependencies import get_auth_service, get_user_service, get_current_active_user
import logging

logger = logging.getLogger(__name__)

auth_router = APIRouter(tags=["Authentication"])


# ══════════════════════════════════════════════════════════════════
# POST /auth/signup — Register a new user account
# ══════════════════════════════════════════════════════════════════
@auth_router.post(
    "/signup",
    response_model=SignupResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new user account"
)
async def signup(
    request: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    - Validates input (username length, email format, password strength)
    - Checks for duplicate username/email
    - Hashes the password with bcrypt
    - Creates the user in the database
    - Returns user profile + JWT tokens (user is immediately logged in)
    """
    try:
        result = auth_service.signup(
            username=request.username,
            email=request.email,
            password=request.password
        )
        return SignupResponse(
            user=UserProfileResponse.model_validate(result["user"]),
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )


# ══════════════════════════════════════════════════════════════════
# POST /auth/login — Authenticate and receive tokens
# ══════════════════════════════════════════════════════════════════
@auth_router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Login with username/email and password"
)
async def login(
    request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Authenticate a user and return JWT tokens.
    
    - Accepts username OR email in the 'username' field
    - Verifies password against stored bcrypt hash
    - Updates last_login timestamp
    - Returns access_token + refresh_token
    """
    try:
        result = auth_service.login(
            username=request.username,
            password=request.password
        )
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


# ══════════════════════════════════════════════════════════════════
# POST /auth/refresh — Get new tokens using refresh token
# ══════════════════════════════════════════════════════════════════
@auth_router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh expired access token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Issue new access + refresh tokens using a valid refresh token.
    
    This is the "silent re-authentication" flow:
    1. Frontend detects 401 on a request
    2. Frontend sends refresh_token to this endpoint
    3. Server validates and issues new tokens
    4. Frontend retries the original request with the new access_token
    """
    try:
        result = auth_service.refresh_tokens(request.refresh_token)
        return TokenResponse(
            access_token=result["access_token"],
            refresh_token=result["refresh_token"]
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )


# ══════════════════════════════════════════════════════════════════
# POST /auth/logout — Client-side logout
# ══════════════════════════════════════════════════════════════════
@auth_router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout (client-side token removal)"
)
async def logout(
    user: User = Depends(get_current_active_user)
):
    """
    Logout the current user.
    
    Since JWTs are stateless (server doesn't store them), logout is
    handled client-side by deleting the stored tokens. This endpoint
    exists for:
    1. Logging the logout event (audit trail)
    2. Future-proofing for token blacklisting (Phase 4 with Redis)
    """
    logger.info(f"[AUTH] User '{user.username}' logged out")
    return MessageResponse(message="Logged out successfully")


# ══════════════════════════════════════════════════════════════════
# GET /auth/me — Get current user profile
# ══════════════════════════════════════════════════════════════════
@auth_router.get(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get current user profile"
)
async def get_profile(
    user: User = Depends(get_current_active_user)
):
    """
    Return the currently authenticated user's profile.
    The user is extracted from the JWT token automatically.
    """
    return UserProfileResponse.model_validate(user)


# ══════════════════════════════════════════════════════════════════
# PUT /auth/me — Update current user profile
# ══════════════════════════════════════════════════════════════════
@auth_router.put(
    "/me",
    response_model=UserProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update current user profile"
)
async def update_profile(
    request: UpdateProfileRequest,
    user: User = Depends(get_current_active_user),
    user_service: UserService = Depends(get_user_service)
):
    """
    Update the current user's profile fields (username, email).
    Only provided fields will be updated.
    """
    try:
        updated_user = user_service.update_profile(
            user_id=user.id,
            username=request.username,
            email=request.email
        )
        return UserProfileResponse.model_validate(updated_user)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e)
        )
