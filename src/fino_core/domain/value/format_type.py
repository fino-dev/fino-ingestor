from dataclasses import dataclass
from enum import Enum

from fino_core.domain.model import ValueObject


class FormatTypeEnum(Enum):
    CSV = "csv"
    XBRL = "xbrl"
    PDF = "pdf"
    OTHER = "other"


@dataclass(frozen=True, slots=True)
class FormatType(ValueObject):
    value: FormatTypeEnum

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Format type cannot be empty")
