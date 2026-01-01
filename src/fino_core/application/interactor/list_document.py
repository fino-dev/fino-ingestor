from fino_core.application.input.list_document import ListDocumentInput
from fino_core.application.output.list_document import ListDocumentOutput
from fino_core.interface.port.disclosure_source import DisclosureSourcePort


class ListDocumentInteractor:
    def __init__(self, disclosure_source_port: DisclosureSourcePort) -> None:
        self.disclosure_source_port = disclosure_source_port

    def execute(self, input: ListDocumentInput) -> ListDocumentOutput:
        documents = self.disclosure_source_port.list_available_documents(input.criteria)
        return ListDocumentOutput(document_list=documents)
