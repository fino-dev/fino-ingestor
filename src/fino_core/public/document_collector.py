from typing import Literal, Optional

from fino_core.application.input.collect_document import CollectDocumentInput
from fino_core.application.input.list_document import ListDocumentInput
from fino_core.application.interactor.collect_document import CollectDocumentUseCase
from fino_core.application.interactor.list_document import ListDocumentUseCase
from fino_core.domain.entity.document import Document
from fino_core.domain.value.format_type import FormatType, FormatTypeEnum
from fino_core.domain.value.market import Market, MarketEnum
from fino_core.infrastructure.adapter.disclosure_source.edinet import (
    EdinetDocumentSearchCriteria,
)
from fino_core.infrastructure.factory.disclosure_source import create_disclosure_source
from fino_core.infrastructure.factory.storage import create_storage
from fino_core.infrastructure.repository.document import DocumentRepositoryImpl
from fino_core.interface.config.disclosure import EdinetConfig
from fino_core.interface.config.storage import LocalStorageConfig, S3StorageConfig
from fino_core.util.timescope import TimeScope


class DocumentCollector:
    def __init__(
        self,
        disclosure_config: EdinetConfig,
        storage_config: LocalStorageConfig | S3StorageConfig,
    ) -> None:
        self._disclosure_source = create_disclosure_source(disclosure_config)

        storage = create_storage(storage_config)
        self._document_repository = DocumentRepositoryImpl(storage)

    def list_document(
        self,
        timescope: TimeScope,
        format_type: Optional[FormatTypeEnum] = FormatTypeEnum.XBRL,
    ) -> dict[
        Literal["available_document_list", "stored_document_list"], list[Document]
    ]:
        # validation
        if format_type is None:
            raise ValueError(
                "format_type must not None. please specify format_type or use default value (XBRL)"
            )

        usecase = ListDocumentUseCase(self._document_repository)

        criteria = EdinetDocumentSearchCriteria(
            market=Market(enum=MarketEnum.JP),
            format_type=FormatType(enum=format_type),
            timescope=timescope,
        )
        input = ListDocumentInput(
            disclosure_source=self._disclosure_source, criteria=criteria
        )

        output = usecase.execute(input)
        return {
            "available_document_list": output.available_document_list,
            "stored_document_list": output.stored_document_list,
        }

    def collect_document(
        self, criteria: EdinetDocumentSearchCriteria
    ) -> dict[Literal["collected_document_list"], list[Document]]:
        usecase = CollectDocumentUseCase(self._document_repository)

        input = CollectDocumentInput(self._disclosure_source, criteria)

        output = usecase.execute(input)

        return {"collected_document_list": output.collected_document_list}


# TODO: FIXME: domainが露出してるところを整理する
