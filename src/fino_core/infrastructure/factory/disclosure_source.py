from fino_ingestor.infrastructure.adapter.disclosure_source.edinet import (
    EdinetAdapter,
    EdinetDocumentSearchCriteria,
)
from fino_ingestor.interface.config.disclosure import EdinetConfig
from fino_ingestor.interface.port.disclosure_source import DisclosureSourcePort


def create_disclosure_source(
    config: EdinetConfig,
) -> DisclosureSourcePort[EdinetDocumentSearchCriteria]:
    return EdinetAdapter(config=config)
