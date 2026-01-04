from dataclasses import dataclass
from enum import Enum

from fino_core.domain.model import ValueObject


class DisclosureTypeEnum(Enum):
    """開示書類の種類"""

    ANNUAL_REPORT = "ANNUAL_REPORT"
    """有価証券報告書"""
    AMENDED_ANNUAL_REPORT = "AMENDED_ANNUAL_REPORT"
    """訂正有価証券報告書"""
    SEMI_ANNUAL_REPORT = "SEMI_ANNUAL_REPORT"
    """半期報告書"""
    AMENDED_SEMI_ANNUAL_REPORT = "AMENDED_SEMI_ANNUAL_REPORT"
    """訂正半期報告書"""
    QUARTERLY_REPORT = "QUARTERLY_REPORT"
    """四半期報告書"""
    AMENDED_QUARTERLY_REPORT = "AMENDED_QUARTERLY_REPORT"
    """訂正四半期報告書"""
    MATERIAL_EVENT_REPORT = "MATERIAL_EVENT_REPORT"
    """臨時報告書"""
    AMENDED_MATERIAL_EVENT_REPORT = "AMENDED_MATERIAL_EVENT_REPORT"
    """訂正臨時報告書"""
    PARENT_COMPANY_REPORT = "PARENT_COMPANY_REPORT"
    """親会社等状況報告書"""
    AMENDED_PARENT_COMPANY_REPORT = "AMENDED_PARENT_COMPANY_REPORT"
    """訂正親会社等状況報告書"""
    SHARE_REPURCHASE_REPORT = "SHARE_REPURCHASE_REPORT"
    """自己株券買付状況報告書"""
    AMENDED_SHARE_REPURCHASE_REPORT = "AMENDED_SHARE_REPURCHASE_REPORT"
    """訂正自己株券買付状況報告書"""


@dataclass(frozen=True, slots=True)
class DisclosureType(ValueObject):
    enum: DisclosureTypeEnum

    @property
    def value(self) -> str:
        return self.enum.value

    @property
    def name(self) -> str:
        return self.enum.name

    def _validate(self) -> None:
        if not self.value:
            raise ValueError("Disclosure type cannot be empty")
