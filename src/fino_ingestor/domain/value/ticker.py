from dataclasses import dataclass

from fino_ingestor.domain.model import ValueObject


@dataclass(frozen=True, slots=True)
class Ticker(ValueObject):
    """
    Ticker VO
    - 市場内で一意
    - 表示・検索・外部API連携に使う識別子
    """

    value: str

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Ticker cannot be empty")
