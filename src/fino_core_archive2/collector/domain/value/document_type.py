from dataclasses import dataclass
from enum import Enum


class DocumentTypeEnum(Enum):
    """開示書類の種類"""

    ANNUAL_REPORT = "annual_report"
    """有価証券報告書"""
    AMENDED_ANNUAL_REPORT = "amended_annual_report"
    """訂正有価証券報告書"""
    SEMI_ANNUAL_REPORT = "semi_annual_report"
    """半期報告書"""
    AMENDED_SEMI_ANNUAL_REPORT = "amended_semi_annual_report"
    """訂正半期報告書"""
    QUARTERLY_REPORT = "quarterly_report"
    """四半期報告書"""
    AMENDED_QUARTERLY_REPORT = "amended_quarterly_report"
    """訂正四半期報告書"""
    MATERIAL_EVENT_REPORT = "material_event_report"
    """臨時報告書"""
    PARENT_COMPANY_REPORT = "parent_company_report"
    """親会社等状況報告書"""
    SHARE_REPURCHASE_REPORT = "share_repurchase_report"
    """自己株券買付状況報告書"""
    AMENDED_SHARE_REPURCHASE_REPORT = "amended_share_repurchase_report"
    """訂正自己株券買付状況報告書"""


@dataclass(frozen=True)
class DocumentType:
    """開示書類の種類を表現するValue Object

    許可された開示書類の種類のみを受け付けます。
    """

    value: str

    def __post_init__(self) -> None:
        """ドメイン不変条件の検証"""
        if not self.value or not self.value.strip():
            raise ValueError("DisclosureType must not be empty")
        disclosure_type = self.value.strip().lower()
        try:
            _ = DocumentTypeEnum(disclosure_type)
        except ValueError as err:
            raise ValueError(
                f"DisclosureType must be one of {[dt.value for dt in DocumentTypeEnum]}: {disclosure_type}"
            ) from err

    def __str__(self) -> str:
        return self.value

    def __repr__(self) -> str:
        return f"DisclosureType('{self.value}')"

    @property
    def is_annual_report(self) -> bool:
        """有価証券報告書かどうかを判定"""
        return self.value.strip().lower() == DocumentTypeEnum.ANNUAL_REPORT.value

    @property
    def is_amended(self) -> bool:
        """訂正報告書かどうかを判定"""
        return "amended" in self.value.strip().lower()

    @property
    def is_quarterly(self) -> bool:
        """四半期報告書かどうかを判定"""
        return "quarterly" in self.value.strip().lower()

    @property
    def is_semi_annual(self) -> bool:
        """半期報告書かどうかを判定"""
        return "semi_annual" in self.value.strip().lower()
