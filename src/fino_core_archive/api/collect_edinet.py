"""Public API for collecting EDINET documents."""

from typing import Optional, cast

from fino_core.application.collector.collect_edinet import collect_edinet as _collect_edinet
from fino_core.application.model.edinet_doc_type_dto import EdinetDocTypeDto
from fino_core.application.model.time_scope import TimeScope
from fino_core.domain.model.edinet import EdinetDocType
from fino_core.infrastructure.edinet import create_edinet
from fino_core.infrastructure.storage import create_storage
from pydantic import BaseModel, Field


class StorageConfigInput(BaseModel):
    """Input model for storage configuration."""

    type: StorageType
    path: Optional[str] = Field(default="")
    storage_uri: Optional[str] = None
    password: Optional[str] = None
    username: Optional[str] = None
    bucket: Optional[str] = None
    api_key: Optional[str] = None
    region: Optional[str] = None


class CollectEdinetInput(BaseModel):
    """Input model for collecting EDINET documents."""

    year: int
    month: int | None = None
    day: int | None = None
    storage: StorageConfigInput
    doc_types: list[int] | int | list[EdinetDocType] | EdinetDocType = EdinetDocType.ANNUAL_REPORT
    api_key: str


def collect_edinet(input: CollectEdinetInput) -> None:
    # Convert input time scope to time scope model
    timescope = TimeScope(year=input.year, month=input.month, day=input.day)

    # Convert doc_types to domain model
    doc_types_dto = EdinetDocTypeDto(
        doc_types=cast(
            list[int], input.doc_types
        )  # validatorでnormalizeされ、list[int]になる想定のためcastで型を強制する
    )

    # Create infrastructure implementations using factory functions
    storage = create_storage(input.storage)
    edinet = create_edinet(api_key=input.api_key)

    # Call application layer function with injected dependencies
    _collect_edinet(
        timescope=timescope,
        storage=storage,
        edinet=edinet,
        doc_types=doc_types_dto.to_domain(),
    )
