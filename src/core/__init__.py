"""
Core Application Components

Authentication, error handling, and other core functionality.
"""

from .auth import (
    AuthManager,
    check_password_strength,
    create_user,
    require_admin_role,
    require_authentication,
    show_password_requirements,
)
from .error_handling import (
    AuthenticationError,
    DatabaseError,
    ErrorHandler,
    FeatureExtractionError,
    ModelError,
    ValidationError,
    ZScoreError,
    handle_exceptions,
)

__all__ = [
    "AuthManager",
    "create_user",
    "check_password_strength",
    "show_password_requirements",
    "require_authentication",
    "require_admin_role",
    "ZScoreError",
    "ModelError",
    "DatabaseError",
    "AuthenticationError",
    "ValidationError",
    "FeatureExtractionError",
    "ErrorHandler",
    "handle_exceptions",
]
