"""Output models for collecting EDINET documents."""

from dataclasses import dataclass

from fino_core.collector.domain.entity.document import Document


@dataclass
class EdinetDocumentCollectionOutput:
    """Output from collecting EDINET documents

    Contains the list of collected documents (metadata only).
    """

    document_list: list[Document]
    """List of collected documents (metadata only, resource=None)"""
