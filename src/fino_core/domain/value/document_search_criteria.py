from dataclasses import dataclass
from typing import Optional

from fino_core.domain.model import ValueObject
from fino_core.domain.value.ticker import Ticker
from fino_core.util.timescope import TimeScope


@dataclass(frozen=True, slots=True)
class DocumentSearchCriteria(ValueObject):
    disclosure_source_id: str
    timescope: Optional[TimeScope] = None
    ticker: Optional[list[Ticker]] = None

    def _validate(self) -> None:
        if not self.disclosure_source_id:
            raise ValueError("disclosure_source_id cannot be empty")

        if (not self.ticker or len(self.ticker) == 0) and not self.timescope:
            raise ValueError("timescope or ticker must be specified")
