from fino_core.application.input.collect_document import CollectDocumentInput
from fino_core.application.output.collect_document import CollectDocumentOutput
from fino_core.domain.entity.document import Document
from fino_core.domain.repository.document import DocumentRepository


class CollectDocumentUseCase:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository

    def execute(self, input: CollectDocumentInput) -> CollectDocumentOutput:
        available_document_list = input.disclosure_source.list_available_documents(
            input.criteria
        )

        stored_document_list: list[Document] = []
        for available_document in available_document_list:
            if self.document_repository.exists(available_document):
                stored_document_list.append(available_document)

        collected_documents: list[Document] = []
        for available_document in available_document_list:
            if available_document not in stored_document_list:
                file = input.disclosure_source.download_document(
                    available_document.document_id,
                    format_type=available_document.filing_format_list,
                )
                self.document_repository.save(available_document, file)
                collected_documents.append(available_document)

        return CollectDocumentOutput(collected_document_list=collected_documents)
