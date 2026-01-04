from dataclasses import dataclass
from enum import Enum

from fino_core.domain.model import ValueObject


class FormatTypeEnum(Enum):
    CSV = "CSV"
    XBRL = "XBRL"
    PDF = "PDF"
    OTHER = "OTHER"


@dataclass(frozen=True, slots=True)
class FormatType(ValueObject):
    enum: FormatTypeEnum

    @property
    def value(self) -> str:
        return self.enum.value

    @property
    def name(self) -> str:
        return self.enum.name

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Format type cannot be empty")
