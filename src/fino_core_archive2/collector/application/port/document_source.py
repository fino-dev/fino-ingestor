"""Application layer port for document source.

This module re-exports the DocumentSource interface from domain layer.
The application layer uses this port to depend on abstractions, not concrete implementations.
"""

from fino_core.collector.domain.repository.document_source import DocumentSource

__all__ = ["DocumentSource"]
