"""
Database Operations

SQLite database management, transactions, and data persistence.
"""

from .local_db import Database, DatabaseException, TransactionRetryException

# Create a default database instance
db = Database()

__all__ = ["Database", "DatabaseException", "TransactionRetryException", "db"]
