from dataclasses import dataclass

from fino_core.domain.model import ValueObject


@dataclass(frozen=True, slots=True)
class DocumentId(ValueObject):
    value: str

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Document ID cannot be empty")
