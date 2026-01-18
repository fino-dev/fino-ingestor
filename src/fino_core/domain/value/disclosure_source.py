from dataclasses import dataclass
from enum import Enum

from fino_ingestor.domain.model import ValueObject


class DisclosureSourceEnum(Enum):
    """開示ソースの種類"""

    EDINET = "EDINET"
    """EDINET"""
    EDGER = "EDGER"
    """EDGER"""


@dataclass(frozen=True, slots=True)
class DisclosureSource(ValueObject):
    enum: DisclosureSourceEnum

    @property
    def value(self) -> str:
        return self.enum.value

    @property
    def name(self) -> str:
        return self.enum.name

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Disclosure source cannot be empty")
