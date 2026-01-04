from dataclasses import dataclass
from enum import Enum

from fino_core.domain.model import ValueObject


class MarketEnum(Enum):
    JP = "JP"
    US = "US"


@dataclass(frozen=True, slots=True)
class Market(ValueObject):
    enum: MarketEnum

    @property
    def value(self) -> str:
        return self.enum.value

    @property
    def name(self) -> str:
        return self.enum.name

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Market cannot be empty")
