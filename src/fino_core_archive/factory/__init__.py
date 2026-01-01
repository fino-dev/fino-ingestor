"""Factory module for backward compatibility.

This module re-exports factory functions from infrastructure layer.
Deprecated: Use infrastructure layer directly.
"""

from fino_core.infrastructure.edinet import create_edinet
from fino_core.infrastructure.storage import create_storage

__all__ = ["create_storage", "create_edinet"]

