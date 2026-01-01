from dataclasses import dataclass

from ..input.collect_document import CollectDocumentsInput
from ..output.collect_document import CollectDocumentsOutput


@dataclass
class CollectDocumentsUseCase:
    """文書収集のユースケース

    このユースケースは、データソース（EDINET、TDnetなど）に依存しません。
    抽象的なDocumentSourceインターフェースを使用して、ソース固有の実装から分離されています。
    """

    def execute(self, input: CollectDocumentsInput) -> CollectDocumentsOutput:
        """文書を収集する

        Args:
            input: 文書収集の入力（Criteria、DocumentSource、Storageを含む）

        Returns:
            収集された文書のリスト（メタデータのみの状態）
        """
        # DocumentSourceから文書リストを取得
        documents = input.document_source.get_document_list(input.criteria)

        # 各文書をストレージに保存
        for document in documents:
            if document.is_complete:
                # DocumentPathを生成してストレージに保存
                # TODO: DocumentPathServiceを使用してパスを生成
                # path = DocumentPathService.generate_path(document)
                # input.storage.save(path.to_string(), document.resource)
                pass

        return CollectDocumentsOutput(document_list=documents)
