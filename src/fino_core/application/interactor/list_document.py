from fino_core.application.input.list_document import ListDocumentInput
from fino_core.application.output.list_document import ListDocumentOutput
from fino_core.domain.repository.document import DocumentRepository
from fino_core.interface.port.disclosure_source import DisclosureSourcePort


class ListDocumentUseCase:
    def __init__(
        self, disclosure_source: DisclosureSourcePort, document_repository: DocumentRepository
    ) -> None:
        self.disclosure_source = disclosure_source
        self.document_repository = document_repository

    def execute(self, input: ListDocumentInput) -> ListDocumentOutput:
        available_documents = self.disclosure_source.list_available_documents(input.criteria)

        stored_documents = self.document_repository.list(input.criteria)
        return ListDocumentOutput(
            available_document_list=available_documents, stored_document_list=stored_documents
        )
