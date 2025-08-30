"""
Core Application Components

Authentication, error handling, and other core functionality.
"""

from .auth import (
    AuthManager, 
    create_user, 
    check_password_strength, 
    show_password_requirements,
    require_authentication,
    require_admin_role
)
from .error_handling import (
    ZScoreError,
    ModelError,
    DatabaseError,
    AuthenticationError,
    ValidationError,
    FeatureExtractionError,
    ErrorHandler,
    handle_exceptions
)

__all__ = [
    'AuthManager',
    'create_user',
    'check_password_strength',
    'show_password_requirements',
    'require_authentication',
    'require_admin_role',
    'ZScoreError',
    'ModelError',
    'DatabaseError',
    'AuthenticationError',
    'ValidationError',
    'FeatureExtractionError',
    'ErrorHandler',
    'handle_exceptions'
]
