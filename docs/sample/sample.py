from fino_core.public.config.disclosure import EdinetConfig
from fino_core.public.config.storage import LocalConfig
from fino_core.public.document_collector import DocumentCollector

edinet_config = EdinetConfig(
    api_key="your-api-key",
)
storage_config = LocalConfig(absolute_path="./data")

document_collector = DocumentCollector(
    disclosure_config=edinet_config,
    storage_config=storage_config,
)

document_collector.list_document()
