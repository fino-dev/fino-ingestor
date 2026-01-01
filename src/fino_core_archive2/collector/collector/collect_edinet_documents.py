from fino_core.collector.application.input.collect_document import CollectDocumentsInput
from fino_core.collector.application.input.edinet_criteria import EdinetCriteria
from fino_core.collector.application.interactor.collect_documents import CollectDocumentsUseCase
from fino_core.collector.factory.document_source import create_edinet_source
from fino_core.collector.factory.storage import create_storage
from fino_core.collector.interface.input.collect_edinet_document import (
    EdinetDocumentCollectionInput,
)
from fino_core.collector.interface.output.collect_edinet_document import (
    EdinetDocumentCollectionOutput,
)


def collect_edinet_documents(
    input: EdinetDocumentCollectionInput,
) -> EdinetDocumentCollectionOutput:
    """Collect documents from EDINET.

    This is the public API function for collecting EDINET documents.
    It handles EDINET-specific setup and calls the source-agnostic use case.

    Args:
        input: EDINET-specific input (API key, time scope, storage config, etc.)

    Returns:
        Output containing list of collected documents (metadata only)

    Example:
        ```python
        from fino_core.collector import collect_edinet_documents
        from fino_core.util import TimeScope

        input_data = EdinetDocumentCollectionInput(
            api_key="your-api-key",
            timescope=TimeScope(year=2024, month=1, day=1),
            storage_config={"type": "local", "path": "./data"},
        )
        result = collect_edinet_documents(input_data)
        ```
    """
    # Create EDINET source
    edinet_source = create_edinet_source(input.api_key)

    # Create storage
    storage = create_storage(input.storage_config)

    # Create EDINET criteria from input
    criteria = EdinetCriteria(
        date=input.timescope.closest_day,
        doc_types=input.doc_types,
        with_docs=False,  # Get metadata only initially
    )

    # Create use case input
    use_case_input = CollectDocumentsInput(
        criteria=criteria,
        document_source=edinet_source,
        storage=storage,
    )

    # Execute use case
    use_case = CollectDocumentsUseCase()
    output = use_case.execute(use_case_input)

    # Return interface output
    return EdinetDocumentCollectionOutput(document_list=output.document_list)
