import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Ticker:
    """証券コード（ティッカーシンボル）を表現するValue Object

    日本の証券コードは通常4桁の数字です。
    米国のティッカーは1-5文字の英数字です。
    """

    value: str

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        if not self.value or not self.value.strip():
            raise ValueError("Ticker must not be empty")
        ticker = self.value.strip()
        # 日本の証券コード（4桁の数字）または米国のティッカー（1-5文字の英数字）
        if not re.match(r"^[0-9]{4}$|^[A-Z]{1,5}$", ticker):
            raise ValueError(
                f"Ticker must be 4-digit number (Japanese) or 1-5 letter uppercase (US): {ticker}"
            )

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"Ticker('{self.value}')"

    @property
    def is_japanese(self) -> bool:
        """日本の証券コードかどうかを判定"""
        return bool(re.match(r"^[0-9]{4}$", self.value.strip()))
