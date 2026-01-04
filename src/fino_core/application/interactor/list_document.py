from fino_core.application.input.list_document import ListDocumentInput
from fino_core.application.output.list_document import ListDocumentOutput
from fino_core.domain.entity.document import Document
from fino_core.domain.repository.document import DocumentRepository


class ListDocumentUseCase:
    def __init__(self, document_repository: DocumentRepository) -> None:
        self.document_repository = document_repository

    def execute(self, input: ListDocumentInput) -> ListDocumentOutput:
        available_document_list = input.disclosure_source.list_available_documents(
            input.criteria
        )

        stored_document_list: list[Document] = []
        for available_document in available_document_list:
            if self.document_repository.exists(available_document):
                stored_document_list.append(available_document)

        return ListDocumentOutput(
            available_document_list=available_document_list,
            stored_document_list=stored_document_list,
        )
