from dataclasses import dataclass
from enum import Enum


class FilingFormatEnum(Enum):
    """提出フォーマットの種類"""

    PDF = "pdf"
    XBRL = "xbrl"
    CSV = "csv"


@dataclass(frozen=True)
class FilingFormat:
    """提出フォーマットを表現するValue Object

    許可されたフォーマットのみを受け付けます。
    """

    value: str

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        if not self.value or not self.value.strip():
            raise ValueError("FilingFormat must not be empty")
        format_value = self.value.strip().lower()
        try:
            _ = FilingFormatEnum(format_value)
        except ValueError as err:
            raise ValueError(
                f"FilingFormat must be one of {[ft.value for ft in FilingFormatEnum]}: {format_value}"
            ) from err

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"FilingFormat('{self.value}')"

    @property
    def is_pdf(self) -> bool:
        """PDFフォーマットかどうかを判定"""
        return self.value.strip().lower() == FilingFormatEnum.PDF.value

    @property
    def is_xbrl(self) -> bool:
        """XBRLフォーマットかどうかを判定"""
        return self.value.strip().lower() == FilingFormatEnum.XBRL.value

    @property
    def is_csv(self) -> bool:
        """CSVフォーマットかどうかを判定"""
        return self.value.strip().lower() == FilingFormatEnum.CSV.value
