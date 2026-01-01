from dataclasses import dataclass
from enum import Enum


class FilingLanguageEnum(Enum):
    """提出言語の種類"""

    JAPANESE = "japanese"
    ENGLISH = "english"


@dataclass(frozen=True)
class FilingLanguage:
    """提出言語を表現するValue Object

    許可された言語のみを受け付けます。
    """

    value: str

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        if not self.value or not self.value.strip():
            raise ValueError("FilingLanguage must not be empty")
        language = self.value.strip().lower()
        try:
            _ = FilingLanguageEnum(language)
        except ValueError as err:
            raise ValueError(
                f"FilingLanguage must be one of {[lt.value for lt in FilingLanguageEnum]}: {language}"
            ) from err

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"FilingLanguage('{self.value}')"

    @property
    def is_japanese(self) -> bool:
        """日本語かどうかを判定"""
        return self.value.strip().lower() == FilingLanguageEnum.JAPANESE.value

    @property
    def is_english(self) -> bool:
        """英語かどうかを判定"""
        return self.value.strip().lower() == FilingLanguageEnum.ENGLISH.value
