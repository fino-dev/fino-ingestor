"""EDINET API implementation of DocumentSource.

This module implements the DocumentSource interface for EDINET API.
It handles EDINET-specific details like authentication, API endpoints, and response mapping.
"""

from datetime import date
from typing import Any

import requests
from fino_core.collector.application.input.edinet_criteria import EdinetCriteria
from fino_core.collector.domain.entity.document import Document
from fino_core.collector.domain.entity.document_metadata import DocumentMetadata
from fino_core.collector.domain.repository.document_source import DocumentSource
from fino_core.collector.domain.value import (
    DisclosureSource,
    DocumentId,
    DocumentType,
    FilingDate,
    FilingFormat,
    FilingLanguage,
    Ticker,
)
from fino_core.collector.infrastructure.edinet_exceptions import (
    BadRequestError,
    InternalServerError,
    InvalidAPIKeyError,
    ResourceNotFoundError,
    ResponseNot200Error,
)


class EdinetSource(DocumentSource):
    """EDINET API implementation of DocumentSource

    This class handles all EDINET-specific logic including:
    - HTTP requests to EDINET API
    - Authentication (API key)
    - Response parsing and mapping to domain entities
    - Error handling for EDINET API errors
    """

    api_version: int = 2
    base_url: str = "https://api.edinet-fsa.go.jp/api/v2/"

    def __init__(self, api_key: str) -> None:
        """Initialize EDINET source

        Args:
            api_key: EDINET API subscription key
        """
        self.api_key = api_key

    def _request(self, endpoint: str, params: dict[str, Any]) -> requests.Response:
        """Make HTTP request to EDINET API

        Args:
            endpoint: API endpoint (e.g., "documents.json")
            params: Query parameters

        Returns:
            HTTP response

        Raises:
            EdinetAPIError: For various HTTP error status codes
        """
        params["Subscription-Key"] = self.api_key

        response = requests.get(
            url=self.base_url + endpoint,
            params=params,
            timeout=(3.0, 7.0),  # (connect timeout, read timeout)
        )

        if response.status_code == 200:
            return response
        elif response.status_code == 400:
            raise BadRequestError(response.status_code, response.text)
        elif response.status_code == 401:
            raise InvalidAPIKeyError(response.status_code, response.text)
        elif response.status_code == 404:
            raise ResourceNotFoundError(response.status_code, response.text)
        elif response.status_code == 500:
            raise InternalServerError(response.status_code, response.text)
        else:
            raise ResponseNot200Error(response.status_code, response.text)

    def _map_edinet_doc_type_to_domain(self, edinet_doc_type_code: str) -> DocumentType:
        """Map EDINET document type code to domain DocumentType

        Args:
            edinet_doc_type_code: EDINET document type code (e.g., "A001")

        Returns:
            Domain DocumentType value object

        Note:
            This is a simplified mapping. A full implementation would need
            a comprehensive mapping table for all EDINET document types.
        """
        # TODO: Implement full mapping from EDINET doc type codes to domain DocumentType
        # For now, return a basic mapping
        # EDINET codes: A001=有価証券報告書, A002=訂正有価証券報告書, etc.
        mapping: dict[str, str] = {
            "A001": "annual_report",
            "A002": "amended_annual_report",
            "A003": "semi_annual_report",
            "A004": "amended_semi_annual_report",
            "A005": "quarterly_report",
            "A006": "amended_quarterly_report",
            # Add more mappings as needed
        }

        domain_type = mapping.get(edinet_doc_type_code, "material_event_report")
        return DocumentType(domain_type)

    def _map_edinet_response_to_document(
        self, edinet_doc: dict[str, Any], filing_date: date
    ) -> Document:
        """Map EDINET API response to domain Document entity

        Args:
            edinet_doc: EDINET document data from API response
            filing_date: Filing date from criteria

        Returns:
            Domain Document entity (metadata only, resource=None)
        """
        doc_id = edinet_doc.get("docID", "")
        doc_type_code = edinet_doc.get("docTypeCode", "")
        title = edinet_doc.get("title", "")
        ticker_code = edinet_doc.get("ticker", "")

        # Map EDINET document type to domain DocumentType
        document_type = self._map_edinet_doc_type_to_domain(doc_type_code)

        # Create domain value objects
        document_id = DocumentId(doc_id)
        source = DisclosureSource("edinet")
        ticker = Ticker(ticker_code) if ticker_code else Ticker("0000")  # Default if missing
        filing_language = FilingLanguage("japanese")  # EDINET is primarily Japanese
        filing_format = FilingFormat("xbrl")  # EDINET primarily uses XBRL
        filing_date_vo = FilingDate(filing_date)

        # Create metadata
        metadata = DocumentMetadata(
            document_id=document_id,
            source=source,
            title=title,
            ticker=ticker,
            filing_language=filing_language,
            filing_format=filing_format,
            filing_date=filing_date_vo,
            disclosure_type=document_type,
        )

        # Create document (metadata only, resource=None)
        return Document.from_metadata(metadata=metadata, name=title)

    def get_document_list(self, criteria: EdinetCriteria) -> list[Document]:
        """Get list of documents from EDINET API

        Args:
            criteria: EDINET-specific criteria (date, doc_types, with_docs)

        Returns:
            List of Document entities (metadata only, resource=None)
        """
        params = {
            "date": criteria.date.strftime("%Y-%m-%d"),
            "type": (2 if criteria.with_docs else 1),
        }

        response = self._request(endpoint="documents.json", params=params)
        response_data = response.json()

        # Parse response and map to domain entities
        documents: list[Document] = []
        results = response_data.get("results", [])

        for edinet_doc in results:
            # Filter by doc_types if specified
            if criteria.doc_types is not None:
                doc_type_code = edinet_doc.get("docTypeCode", "")
                doc_type = self._map_edinet_doc_type_to_domain(doc_type_code)
                if doc_type not in criteria.doc_types:
                    continue

            document = self._map_edinet_response_to_document(edinet_doc, criteria.date)
            documents.append(document)

        return documents

    def get_document(self, document_id: DocumentId, document_type: DocumentType) -> Document:
        """Get complete document (with resource) from EDINET API

        Args:
            document_id: Document ID
            document_type: Document type

        Returns:
            Complete Document entity (with resource set)
        """
        # EDINET API uses document type code, not domain DocumentType
        # For now, we'll need to map back or use a default
        # TODO: Implement proper mapping from domain DocumentType to EDINET doc type code
        edinet_doc_type = "1"  # Default to XBRL format

        response = self._request(
            endpoint=f"documents/{document_id.value}",
            params={"type": edinet_doc_type},
        )

        resource = response.content

        # Get metadata first (we need filing_date, but we don't have it here)
        # For now, we'll create a minimal document
        # TODO: Fetch metadata separately or include in response
        filing_date = FilingDate(date.today())  # Placeholder
        source = DisclosureSource("edinet")
        ticker = Ticker("0000")  # Placeholder
        filing_language = FilingLanguage("japanese")
        filing_format = FilingFormat("xbrl")

        metadata = DocumentMetadata(
            document_id=document_id,
            source=source,
            title="",  # Placeholder
            ticker=ticker,
            filing_language=filing_language,
            filing_format=filing_format,
            filing_date=filing_date,
            disclosure_type=document_type,
        )

        document = Document.from_metadata(metadata=metadata, name="")
        return document.with_resource(resource)
