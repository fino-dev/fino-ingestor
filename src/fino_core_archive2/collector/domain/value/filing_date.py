from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class FilingDate:
    """提出日を表現するValue Object

    財務報告書の提出日は未来の日付であってはなりません。
    """

    value: date

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        today = date.today()
        if self.value > today:
            raise ValueError(f"FilingDate must not be in the future: {self.value}")

    def __str__(self) -> str:
        return self.value.isoformat()

    def __repr__(self) -> str:
        return f"FilingDate({self.value.isoformat()})"

    def to_date(self) -> date:
        """date型に変換"""
        return self.value
