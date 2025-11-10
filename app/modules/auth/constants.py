"""
Auth Module Constants and Enums
Authentication and authorization specific constants
"""
from enum import Enum


class AuthTokenType(str, Enum):
    """Authentication token types"""
    ACCESS = "access"
    REFRESH = "refresh"
    RESET_PASSWORD = "reset_password"
    VERIFY_EMAIL = "verify_email"


class LoginMethod(str, Enum):
    """User login methods"""
    EMAIL_PASSWORD = "email_password"
    OAUTH_GOOGLE = "oauth_google"
    OAUTH_GITHUB = "oauth_github"
    SSO = "sso"


class PasswordResetStatus(str, Enum):
    """Password reset request status"""
    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"


# JWT Constants
JWT_ALGORITHM = "HS256"
JWT_TOKEN_PREFIX = "Bearer"

# Password validation
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL = False

# Account security
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCKOUT_DURATION_MINUTES = 15
PASSWORD_RESET_TOKEN_EXPIRE_MINUTES = 30
EMAIL_VERIFICATION_TOKEN_EXPIRE_HOURS = 24

# Session management
MAX_ACTIVE_SESSIONS_PER_USER = 5
SESSION_INACTIVITY_TIMEOUT_MINUTES = 30
