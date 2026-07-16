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
from core.limiter import limiter
from fastapi import Request
from services.cache_service import CacheService
from app.dependencies import get_cache_service
from core.settings import get_settings

settings = get_settings()

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
@limiter.limit("3/minute") # Max 3 signups per IP per minute
async def signup(
    request: Request, # Required by SlowAPI
    signup_data: SignupRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
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
@limiter.limit("5/minute")
async def login(
    request: Request, 
    login_data: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    try:
        result = auth_service.login(
            username=login_data.username,
            password=login_data.password
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
    user: User = Depends(get_current_active_user),
    cache_service: CacheService = Depends(get_cache_service),
    user_service: UserService = Depends(get_user_service)
):
    """
    Returns the current user's profile.
    Implements Cache-Aside pattern:
    1. Check Redis cache.
    2. If miss, fetch from DB and populate cache.
    """
    cache_key = f"user:{user.id}:profile"
    
    # 1. Try to get from cache
    cached_profile = cache_service.get(cache_key)
    if cached_profile:
        return UserProfileResponse.model_validate(cached_profile)
    
    # 2. Cache miss: Fetch from DB (via user_service or directly from the injected user)
    # Since we already have the user object from the dependency, we just use it.
    profile_data = UserProfileResponse.model_validate(user)
    
    # 3. Populate cache (TTL from settings, default 300s)
    cache_service.set(
        cache_key, 
        profile_data.model_dump(mode="json"), 
        ttl=settings.cache_default_ttl
    )
    
    return profile_data


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
