"""
Z-Cred Application Source Code

This package contains the core source code for the Z-Cred
Dynamic Trust-Based Credit Framework application.
"""

__version__ = "1.0.0"
__author__ = "Team Z-Row"

# Expose key components for easy importing
from . import models
from . import core
from . import database
from . import apps
from . import utils

# Quick access to commonly used items
from .models import model_integrator, get_unified_trust_scores
from .database import db
from .core import AuthManager, ErrorHandler

__all__ = [
    'models',
    'core', 
    'database',
    'apps',
    'utils',
    'model_integrator',
    'get_unified_trust_scores',
    'db',
    'AuthManager',
    'ErrorHandler'
]
