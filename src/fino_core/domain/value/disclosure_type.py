from dataclasses import dataclass
from enum import Enum

from fino_core.domain.model import ValueObject


class DisclosureTypeEnum(Enum):
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


@dataclass(frozen=True, slots=True)
class DisclosureType(ValueObject):
    value: DisclosureTypeEnum

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Disclosure type cannot be empty")
