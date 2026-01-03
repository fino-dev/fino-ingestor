from fino_core.infrastructure.adapter.disclosure_source.edinet import (
    EdinetAdapter,
    EdinetDocumentSearchCriteria,
)
from fino_core.interface.config.disclosure import EdinetConfig
from fino_core.interface.port.disclosure_source import DisclosureSourcePort


def create_disclosure_source(
    config: EdinetConfig,
) -> DisclosureSourcePort[EdinetDocumentSearchCriteria]:
    return EdinetAdapter(config=config)
