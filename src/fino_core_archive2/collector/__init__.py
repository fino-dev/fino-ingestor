"""Public API for collecting financial documents.

Thisc provides the public API functions for collecting documents from various sources.
"""

from .collector.collect_edinet_documents import collect_edinet_documents

__all__ = ["collect_edinet_documents"]
