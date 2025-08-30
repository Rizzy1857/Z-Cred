"""
Z-Cred Application Source Code

This package contains the core source code for the Z-Cred
Dynamic Trust-Based Credit Framework application.
"""

__version__ = "1.0.0"
__author__ = "Team Z-Row"

# Expose key components for easy importing
from . import apps, core, database, models, utils
from .core import AuthManager, ErrorHandler
from .database import db

# Quick access to commonly used items
from .models import get_unified_trust_scores, model_integrator

__all__ = [
    "models",
    "core",
    "database",
    "apps",
    "utils",
    "model_integrator",
    "get_unified_trust_scores",
    "db",
    "AuthManager",
    "ErrorHandler",
]
