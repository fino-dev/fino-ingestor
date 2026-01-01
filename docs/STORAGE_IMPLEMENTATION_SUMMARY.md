# Fino Core Storage 実装サマリー

## 実装完了内容

設計パターンに基づいて、`fino_core/src/fino_core`配下に storage 実装を整理しました。

### 1. モデル層 (`model/storage.py`)

- ✅ `StorageConfig` (基底クラス)
- ✅ `LocalStorageConfig` (ローカルストレージ設定)
- ✅ `S3StorageConfig` (S3 ストレージ設定)
- ✅ `StoragePort` (インターフェース)

### 2. ファクトリー層 (`factory/storage.py`)

- ✅ `create_storage()` - `isinstance`ベースの判定でストレージインスタンスを生成

### 3. インフラ層 (`infrastructure/storage/`)

- ✅ `LocalStorage` - ローカルファイルシステム実装
- ✅ `S3Storage` - S3 実装（TODO: boto3 統合が必要）

### 4. 名前空間エイリアス

- ✅ `fino_core/__init__.py` - `_model`と`_factory`のエイリアスを追加（後方互換性）

## 設計パターンの遵守状況

### ✅ 判断基準チェックリスト

- [x] `save/get`のシグネチャは共通 → ✅ 実装済み
- [x] UseCase に`bucket`や`api_key`が出てこない → ✅ 現状 OK
- [x] 差異は Config or Factory に閉じている → ✅ `isinstance`ベースの判定
- [x] 新しい storage を足しても UseCase は無変更 → ✅ Factory パターンで実現

## 使用例

### Entrypoint での使用

```python
from fino_core._model.storage import S3StorageConfig
from fino_core._factory.storage import create_storage
import os

# S3設定
config = S3StorageConfig(
    bucket="my-bucket",
    api_key=os.environ["AWS_ACCESS_KEY_ID"],
    region="ap-northeast-1",
)

# ストレージインスタンス生成
storage = create_storage(config)

# 使用
storage.save(key="path/to/file", data=b"file content")
data = storage.get(key="path/to/file")
```

### UseCase での使用

```python
from fino_core._model.storage import StorageConfig
from fino_core._factory.storage import create_storage

def collect_edinet(input: CollectEdinetInput) -> CollectEdinetOutput:
    # input.storageはStorageConfig（LocalStorageConfigまたはS3StorageConfig）
    storage = create_storage(input.storage)
    storage.save(key="edinet/doc123", data=doc_bytes)
```

## 今後の課題

1. **StorageInput から StorageConfig への変換**

   - `application/collector/input/collect_document.py`の`StorageInput`から`StorageConfig`への変換ロジックが必要
   - 現在は`StorageType` Enum ベースの設計になっているため、変換関数の実装が必要

2. **S3Storage の実装完了**

   - `infrastructure/storage/s3_storage.py`で boto3 を使用した実装が必要
   - 依存関係に`boto3`を追加する必要がある

3. **テストの追加**
   - 各 Config クラスのテスト
   - Factory 関数のテスト
   - LocalStorage/S3Storage の実装テスト

## ファイル構成

```
fino_core/src/fino_core/
├── __init__.py                    # _model, _factoryエイリアス
├── model/
│   ├── __init__.py               # StorageConfig等をエクスポート
│   └── storage.py                # StorageConfig, StoragePort定義
├── factory/
│   ├── __init__.py               # create_storageをエクスポート
│   └── storage.py                # create_storage Factory関数
└── infrastructure/
    ├── __init__.py
    └── storage/
        ├── __init__.py
        ├── local_storage.py      # LocalStorage実装
        └── s3_storage.py         # S3Storage実装
```

## 設計の利点

1. **型安全性**: 各 Config クラスで必要な設定が型で明確
2. **拡張性**: 新しいストレージタイプ（GCS 等）を追加しても UseCase は無変更
3. **テスト容易性**: 各 Config クラスが独立してテスト可能
4. **保守性**: 差異が Config と Factory に閉じている

