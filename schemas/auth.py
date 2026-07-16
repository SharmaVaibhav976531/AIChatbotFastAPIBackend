# schemas/auth.py

from pydantic import BaseModel, Field, EmailStr, ConfigDict
from datetime import datetime
from uuid import UUID


# =====================================================================
# REQUEST SCHEMAS — What the frontend sends TO the backend
# =====================================================================

class SignupRequest(BaseModel):
    """
    Schema for user registration.
    Validates username length, email format, and password strength.
    """
    username: str = Field(
        ...,
        min_length=3,
        max_length=50,
        description="Unique username (3-50 characters)",
        examples=["vaibhav"]
    )
    email: str = Field(
        ...,
        min_length=5,
        max_length=100,
        description="Valid email address",
        examples=["vaibhav@example.com"]
    )
    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Password (minimum 8 characters)",
        examples=["MySecurePass123"]
    )


class LoginRequest(BaseModel):
    """
    Schema for user login.
    Accepts either username or email — the service will check both.
    """
    username: str = Field(
        ...,
        min_length=1,
        description="Username or email address",
        examples=["vaibhav"]
    )
    password: str = Field(
        ...,
        min_length=1,
        description="Account password",
        examples=["MySecurePass123"]
    )


class RefreshTokenRequest(BaseModel):
    """
    Schema for token refresh.
    The client sends the refresh token to get a new access token.
    """
    refresh_token: str = Field(
        ...,
        min_length=1,
        description="The refresh token received during login"
    )


class UpdateProfileRequest(BaseModel):
    """
    Schema for updating user profile.
    All fields are optional — only the provided fields will be updated.
    """
    username: str | None = Field(
        None,
        min_length=3,
        max_length=50,
        description="New username"
    )
    email: str | None = Field(
        None,
        min_length=5,
        max_length=100,
        description="New email address"
    )


# =====================================================================
# RESPONSE SCHEMAS — What the backend sends TO the frontend
# =====================================================================

class TokenResponse(BaseModel):
    """
    Response after successful login or token refresh.
    Contains both tokens so the frontend can store them.
    """
    access_token: str = Field(..., description="JWT access token (short-lived)")
    refresh_token: str = Field(..., description="JWT refresh token (long-lived)")
    token_type: str = Field(default="bearer", description="Token type (always 'bearer')")


class UserProfileResponse(BaseModel):
    """
    Response for user profile endpoints.
    NEVER includes the hashed_password — security best practice.
    """
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    username: str
    email: str
    is_active: bool
    is_verified: bool
    is_superuser: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime


class SignupResponse(BaseModel):
    """
    Response after successful registration.
    Returns the user profile + tokens so the user is immediately logged in.
    """
    message: str = Field(default="Account created successfully")
    user: UserProfileResponse
    access_token: str
    refresh_token: str
    token_type: str = Field(default="bearer")


class MessageResponse(BaseModel):
    """
    Generic message response for operations like logout.
    """
    message: str
