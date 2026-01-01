from dataclasses import dataclass
from datetime import date

from fino_core.domain.model import ValueObject


@dataclass(frozen=True, slots=True)
class DisclosureDate(ValueObject):
    value: date

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Disclosure date cannot be empty")
        if self.value > date.today():
            raise ValueError("Disclosure date cannot be in the future")
