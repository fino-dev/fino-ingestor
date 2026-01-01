from fino_core.infrastructure.edinet import EdinetAdapter
from fino_core.domain.edinet import Edinet


def create_edinet(api_key: str) -> Edinet:
    return EdinetAdapter(api_key=api_key)
