from fino_core.collector import collect_document_from_edinet, collect_document_from_tdnet

saved_documents = collect_document_from_edinet(
    storage_config=StorageConfig(
        type=StorageType.LOCAL,
        path="./data",
    ),
    api_key="1234567890",
    timescope=TimeScope(year=2024, month=1),
    doc_types=[EdinetDocType.ANNUAL_REPORT],
)

saved_documents = collect_document_from_tdnet(
    storage_config=StorageConfig(
        type=StorageType.S3,
        storage_uri="s3://your-bucket/path",
    ),
    username="your-username",
    password="your-password",
    ticker="1234567890",
    doc_types=[EdinetDocType.ANNUAL_REPORT],
)
