from abc import ABC, abstractmethod

from fino_core.domain.entity.document import Document
from fino_core.domain.value.format_type import FormatType


class DocumentRepository(ABC):
    @abstractmethod
    def exists(self, document: Document, format_type: FormatType) -> bool: ...
    TODO: format typeも指定しないと一意に指定できないのでここのロジックを変える in DocumentRepository impl
    documentID単位でexistsを確認してしまうと、この関数を呼び出しているuseca側でformat　typeを踏まえた判定ロジックが必要になるので、シンプルに、criteriaにformat typeを使用しているusecaseしか現状ないのでこれにより、document id x format typeのループは発生しない
    @abstractmethod
    def save(self, document: Document, file: bytes) -> None: ...
