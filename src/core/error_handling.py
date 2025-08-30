"""
Centralized Error Handling Module for Z-Score Application

Provides consistent error handling, logging, and user-friendly error messages
across all modules of the application.
"""

import functools
import json
import logging
import traceback
from datetime import datetime
from typing import Any, Callable, Dict, Optional


class ZScoreError(Exception):
    """Base exception class for Z-Score application"""

    def __init__(
        self,
        message: str,
        error_code: str = "GENERIC_ERROR",
        details: Optional[Dict] = None,
    ):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}
        self.timestamp = datetime.now().isoformat()


class ModelError(ZScoreError):
    """Errors related to machine learning models"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "MODEL_ERROR", details)


class DatabaseError(ZScoreError):
    """Errors related to database operations"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "DATABASE_ERROR", details)


class AuthenticationError(ZScoreError):
    """Errors related to authentication and authorization"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "AUTH_ERROR", details)


class ValidationError(ZScoreError):
    """Errors related to data validation"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", details)


class FeatureExtractionError(ZScoreError):
    """Errors related to feature extraction and processing"""

    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "FEATURE_ERROR", details)


class ErrorHandler:
    """Centralized error handling and logging"""

    def __init__(self, log_level=logging.INFO):
        self.setup_logging(log_level)

    def setup_logging(self, log_level):
        """Setup logging configuration"""
        # Create logs directory if it doesn't exist
        import os

        os.makedirs("logs", exist_ok=True)

        logging.basicConfig(
            level=log_level,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("logs/zscore_errors.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger("ZScore")

    def log_error(self, error: Exception, context: Optional[Dict] = None):
        """Log error with context information"""
        error_info = {
            "error_type": type(error).__name__,
            "error_message": str(error),
            "timestamp": datetime.now().isoformat(),
            "context": context or {},
            "traceback": traceback.format_exc(),
        }

        if isinstance(error, ZScoreError):
            error_info.update(
                {"error_code": error.error_code, "details": error.details}
            )

        self.logger.error(f"Error occurred: {json.dumps(error_info, indent=2)}")
        return error_info

    def handle_error(
        self, error: Exception, context: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Handle error and return user-friendly response"""
        self.log_error(error, context)

        # Return user-friendly error response
        if isinstance(error, ModelError):
            return {
                "success": False,
                "error": "Model prediction failed. Please try again.",
                "error_code": error.error_code,
                "user_message": self._get_user_friendly_message(error),
            }
        elif isinstance(error, DatabaseError):
            return {
                "success": False,
                "error": "Database operation failed. Please contact support.",
                "error_code": error.error_code,
                "user_message": self._get_user_friendly_message(error),
            }
        elif isinstance(error, AuthenticationError):
            return {
                "success": False,
                "error": "Authentication failed. Please check your credentials.",
                "error_code": error.error_code,
                "user_message": self._get_user_friendly_message(error),
            }
        elif isinstance(error, ValidationError):
            return {
                "success": False,
                "error": "Invalid data provided. Please check your input.",
                "error_code": error.error_code,
                "user_message": self._get_user_friendly_message(error),
            }
        elif isinstance(error, FeatureExtractionError):
            return {
                "success": False,
                "error": "Failed to process applicant data. Please verify the information.",
                "error_code": error.error_code,
                "user_message": self._get_user_friendly_message(error),
            }
        else:
            return {
                "success": False,
                "error": "An unexpected error occurred. Please try again.",
                "error_code": "UNEXPECTED_ERROR",
                "user_message": "Something went wrong. Our team has been notified.",
            }

    def _get_user_friendly_message(self, error: ZScoreError) -> str:
        """Get user-friendly error message"""
        error_messages = {
            "MODEL_ERROR": "Our credit assessment system is temporarily unavailable. Please try again in a few moments.",
            "DATABASE_ERROR": "We're experiencing technical difficulties. Your data is safe, please try again shortly.",
            "AUTH_ERROR": "Please check your login credentials and try again.",
            "VALIDATION_ERROR": "Please review and correct the highlighted fields.",
            "FEATURE_ERROR": "Some of your information couldn't be processed. Please review and resubmit.",
        }
        return error_messages.get(error.error_code, error.message)


# Global error handler instance
error_handler = ErrorHandler()


def handle_exceptions(error_type=ZScoreError):
    """Decorator for handling exceptions in functions"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                context = {
                    "function": func.__name__,
                    "args_count": len(args),
                    "kwargs_keys": list(kwargs.keys()),
                }

                if isinstance(e, ZScoreError):
                    raise e
                else:
                    # Convert generic exceptions to specific error types
                    if (
                        "model" in func.__name__.lower()
                        or "predict" in func.__name__.lower()
                    ):
                        raise ModelError(
                            f"Model operation failed: {str(e)}",
                            {"original_error": str(e)},
                        )
                    elif (
                        "database" in func.__name__.lower()
                        or "db" in func.__name__.lower()
                    ):
                        raise DatabaseError(
                            f"Database operation failed: {str(e)}",
                            {"original_error": str(e)},
                        )
                    elif (
                        "auth" in func.__name__.lower()
                        or "login" in func.__name__.lower()
                    ):
                        raise AuthenticationError(
                            f"Authentication failed: {str(e)}",
                            {"original_error": str(e)},
                        )
                    else:
                        raise error_type(f"Operation failed: {str(e)}")

        return wrapper

    return decorator


def validate_input(validation_rules: Dict[str, Callable]) -> Callable:
    """Decorator for input validation"""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Validate inputs based on rules
            for param_name, validation_func in validation_rules.items():
                if param_name in kwargs:
                    value = kwargs[param_name]
                    if not validation_func(value):
                        raise ValidationError(
                            f"Invalid value for parameter '{param_name}'",
                            {"parameter": param_name, "value": str(value)[:100]},
                        )

            return func(*args, **kwargs)

        return wrapper

    return decorator


def safe_json_parse(json_string: str, default: Optional[Dict] = None) -> Dict:
    """Safely parse JSON string with error handling"""
    try:
        if isinstance(json_string, dict):
            return json_string
        if not json_string or json_string.strip() == "":
            return default or {}
        return json.loads(json_string)
    except json.JSONDecodeError as e:
        error_handler.log_error(
            ValidationError(f"Invalid JSON format: {str(e)}"),
            {"json_string": json_string[:100]},
        )
        return default or {}
    except Exception as e:
        error_handler.log_error(
            ValidationError(f"Unexpected error parsing JSON: {str(e)}"),
            {"json_string": json_string[:100]},
        )
        return default or {}


def safe_numeric_conversion(
    value: Any,
    default: float = 0.0,
    min_val: Optional[float] = None,
    max_val: Optional[float] = None,
) -> float:
    """Safely convert value to numeric with bounds checking"""
    try:
        if value is None or value == "":
            return default

        numeric_value = float(value)

        if min_val is not None and numeric_value < min_val:
            return min_val
        if max_val is not None and numeric_value > max_val:
            return max_val

        return numeric_value
    except (ValueError, TypeError) as e:
        error_handler.log_error(
            ValidationError(f"Invalid numeric value: {str(e)}"),
            {"value": str(value), "default": default},
        )
        return default


def confidence_interval_calculator(
    predictions: list, confidence_level: float = 0.95
) -> Dict[str, float]:
    """Calculate confidence intervals for model predictions"""
    try:
        import numpy as np
        from scipy import stats

        if not predictions or len(predictions) < 2:
            return {"lower": 0.0, "upper": 1.0, "mean": 0.5}

        predictions_array = np.array(predictions)
        mean = float(np.mean(predictions_array))
        std_err = float(stats.sem(predictions_array))
        confidence_interval = stats.t.interval(
            confidence_level, len(predictions_array) - 1, loc=mean, scale=std_err
        )

        return {
            "lower": max(0.0, float(confidence_interval[0])),
            "upper": min(1.0, float(confidence_interval[1])),
            "mean": mean,
            "std_error": std_err,
        }
    except Exception as e:
        error_handler.log_error(
            ModelError(f"Confidence interval calculation failed: {str(e)}")
        )
        return {"lower": 0.0, "upper": 1.0, "mean": 0.5}


# Validation helper functions
def is_valid_email(email: str) -> bool:
    """Validate email format"""
    import re

    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_phone(phone: str) -> bool:
    """Validate phone number format"""
    import re

    # Indian phone number pattern
    pattern = r"^[6-9]\d{9}$"
    return bool(
        re.match(
            pattern, str(phone).replace("+91", "").replace("-", "").replace(" ", "")
        )
    )


def is_valid_age(age: Any) -> bool:
    """Validate age range"""
    try:
        age_val = float(age)
        return 18 <= age_val <= 100
    except (ValueError, TypeError):
        return False


def is_valid_income(income: Any) -> bool:
    """Validate monthly income"""
    try:
        income_val = float(income)
        return 0 <= income_val <= 10000000  # Up to 1 crore per month
    except (ValueError, TypeError):
        return False
