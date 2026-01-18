from fino_ingestor.domain.entity.document import Document
from fino_ingestor.domain.repository.document import DocumentRepository
from fino_ingestor.infrastructure.policy.document_path import DocumentPathPolicy
from fino_ingestor.interface.port.storage import StoragePort


class DocumentRepositoryImpl(DocumentRepository):
    def __init__(self, storage: StoragePort) -> None:
        self._storage = storage
        self._path_policy = DocumentPathPolicy

    def exists(self, document: Document) -> bool:
        path = self._path_policy.generate_path(document, is_zip=True)
        return self._storage.exists(path=path)

    def save(self, document: Document, file: bytes) -> None:
        path = self._path_policy.generate_path(document, is_zip=True)
        self._storage.save(path=path, file=file)
