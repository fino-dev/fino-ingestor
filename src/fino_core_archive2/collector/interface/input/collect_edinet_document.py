"""Input models for collecting EDINET documents.

These models are part of the interface layer and may contain EDINET-specific concepts.
"""

from dataclasses import dataclass
from typing import Any, Optional

from fino_core.collector.domain.value import DocumentType
from fino_core.util.timescope import TimeScope


@dataclass
class EdinetDocumentCollectionInput:
    """Input for collecting EDINET documents

    This is the public API input model that accepts EDINET-specific parameters.
    """

    api_key: str
    """EDINET API subscription key"""

    timescope: TimeScope
    """Time scope for document collection"""

    storage_config: dict[str, Any] | Any
    """Storage configuration (dict or object with type, path/bucket, etc.)"""

    doc_types: Optional[list[DocumentType]] = None
    """Optional filter for document types to collect.

    If None, collects all document types.
    """
