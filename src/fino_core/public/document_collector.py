from typing import Literal

from fino_core.domain.value.document_search_criteria import DocumentSearchCriteria
from fino_core.infrastructure.repository.documenet import DocumentRepositoryImpl
from fino_core.public.config.disclosure import EdinetConfig, TDNetSampleConfig

from fino_core.application.input.collect_document import CollectDocumentInput
from fino_core.application.input.list_document import ListDocumentInput
from fino_core.application.interactor.collect_document import CollectDocumentUseCase
from fino_core.application.interactor.list_document import ListDocumentUseCase
from fino_core.domain.entity.document import Document
from fino_core.infrastructure.factory.disclosure_source import create_disclosure_source
from fino_core.infrastructure.factory.storage import create_storage
from fino_core.util.timescope import TimeScope


class DocumentCollector:
    def __init__(
        self,
        disclosure_config: EdinetConfig | TDNetSampleConfig,
        storage_config: LocalConfig | S3Config,
    ) -> None:
        self._disclosure_source = create_disclosure_source(disclosure_config)

        storage = create_storage(storage_config)
        self._document_repository = DocumentRepositoryImpl(storage)

    def list_document(
        self, timescope: TimeScope
    ) -> dict[
        Literal["available_document_list", "stored_document_list"], list[Document]
    ]:
        usecase = ListDocumentUseCase(self._document_repository)

        criteria = DocumentSearchCriteria(
            disclosure_source_id=self._disclosure_source.id, timescope=timescope
        )
        input = ListDocumentInput(self._disclosure_source, criteria)

        output = usecase.execute(input)
        return {
            "available_document_list": output.available_document_list,
            "stored_document_list": output.stored_document_list,
        }

    def collect_document(
        self, criteria: DocumentSearchCriteria
    ) -> dict[Literal["collected_document_list"], list[Document]]:
        usecase = CollectDocumentUseCase(self._document_repository)

        input = CollectDocumentInput(self._disclosure_source, criteria)

        output = usecase.execute(input)

        return {"collected_document_list": output.collected_document_list}


# TODO: FIXME: inrfaの整理
# TODO: FIXME: domainが露出してるところを整理する
