"""Factory for creating document source implementations.

This factory handles dependency injection for document sources.
It creates concrete implementations (EdinetSource, TdnetSource, etc.) based on configuration.
"""

from fino_core.collector.infrastructure.edinet_source import EdinetSource


def create_edinet_source(api_key: str) -> EdinetSource:
    """Create an EDINET document source instance.

    Args:
        api_key: EDINET API subscription key

    Returns:
        EdinetSource instance implementing DocumentSource interface
    """
    return EdinetSource(api_key=api_key)
