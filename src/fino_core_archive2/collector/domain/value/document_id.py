from dataclasses import dataclass


@dataclass(frozen=True)
class DocumentId:
    """文書IDを表現するValue Object

    EDINETのドキュメントIDは通常、S100XXXXX形式（S + 5桁の数字）です。
    """

    value: str

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        if not self.value or not self.value.strip():
            raise ValueError("DocumentId must not be empty")
        # EDINETのドキュメントIDは通常、S + 5桁以上の数字または英数字
        # より柔軟な形式も許可（将来の拡張性のため）
        if len(self.value.strip()) < 1:
            raise ValueError("DocumentId must have at least 1 character")

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"DocumentId('{self.value}')"
