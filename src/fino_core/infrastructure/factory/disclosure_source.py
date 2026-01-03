from fino_core.infrastructure.adapter.disclosure_source.edinet import EdinetAdapter
from fino_core.infrastructure.adapter.disclosure_source.tdnet import TDNetAdapter
from fino_core.interface.port.disclosure_source import DisclosureSourcePort
from fino_core.public.config.disclosure import EdinetConfig, TDNetSampleConfig


def create_disclosure_source(config: EdinetConfig | TDNetSampleConfig) -> DisclosureSourcePort:
    if isinstance(config, EdinetConfig):
        return EdinetAdapter(config.api_key)
    else:
        return TDNetAdapter(config.username, config.password)
