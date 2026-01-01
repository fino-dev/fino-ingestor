# Fino Core Storage 設計レビュー

## 現在の実装状況

### 1. ドメイン層（Port 定義）

**ファイル**: `src/archive/_domain/storage/main.py`

```python
@dataclass
class StorageConfig:
    """Storage URI (s3://, file://, etc.)"""
    uri: str
    password: str | None = None
    username: str | None = None

class StoragePort(ABC):
    @abstractmethod
    def save(self, data: bytes, path: str) -> None:
        pass
```

### 2. インフラ層（実装）

**ファイル**: `src/archive/_infrastructure/storage/main.py` (Factory)

```python
def create_storage(config: StorageConfig) -> StoragePort:
    parsed = urlparse(config.storage_path)  # ❌ storage_path属性が存在しない
    if parsed.scheme == "s3" or parsed.hostname == "localhost":
        return S3Storage(config)
    elif parsed.scheme == "":
        return LocalStorage(config)
    else:
        raise ValueError(f"Unsupported storage scheme: {parsed}")
```

**ファイル**: `src/archive/_infrastructure/storage/s3_storage.py`

```python
class S3Storage(StoragePort):
    def __init__(self, config: Storage) -> None:  # ❌ Storage型だがStorageConfigが渡される
        self.config = config
    def save(self, object: bytes) -> None:  # ❌ path引数が欠けている
        pass
```

**ファイル**: `src/archive/_infrastructure/storage/local_storage.py`

```python
class LocalStorage(StoragePort):
    def __init__(self, config: Storage) -> None:  # ❌ 同様の問題
        self.config = config
    def save(self, object: bytes) -> None:  # ❌ path引数が欠けている
        pass
```

### 3. 使用例

**ファイル**: `src/fino_core/application/usecases/collect_edinet.py`

```python
def collect_edinet(input: CollectEdinetInput) -> CollectEdinetOutput:
    storage = create_storage(input.storage)  # ✅ Factoryパターン使用
    # ...
    storage.save(doc_bytes, path=f"edinet/{document['docID']}")
```

---

## 問題点の分析

### ❌ 問題 1: 設定オブジェクトが統一されすぎている

現在の`StorageConfig`は単一の dataclass で、URI ベースの設計になっています。

**問題**:

- Local Storage には`password`や`username`が不要
- S3 Storage には`bucket`や`api_key`が必要だが、現在の Config には含まれていない
- URI パースに依存した判定ロジックが複雑

### ❌ 問題 2: 型の不一致

- `S3Storage.__init__`は`Storage`型を期待しているが、実際には`StorageConfig`が渡される
- `create_storage`内で`config.storage_path`にアクセスしているが、`StorageConfig`には`uri`属性しかない

### ❌ 問題 3: メソッドシグネチャの不一致

- `StoragePort.save()`は`path`引数を要求
- 実装クラス（`S3Storage`, `LocalStorage`）の`save()`は`path`引数がない

### ❌ 問題 4: 拡張性の問題

- 新しいストレージタイプ（GCS 等）を追加する際、URI パースロジックを修正する必要がある
- 設定の差異が呼び出し側に漏れ出る可能性

---

## 推奨される設計パターン（提供された例）

### ✅ 正解アプローチ: 設定オブジェクトを分離する

#### 1. StorageConfig を基底クラスとして分離

```python
from dataclasses import dataclass
from abc import ABC

class StorageConfig(ABC):
    pass

@dataclass
class LocalStorageConfig(StorageConfig):
    base_path: str

@dataclass
class S3StorageConfig(StorageConfig):
    bucket: str
    api_key: str
    region: str
```

**メリット**:

- 必要な設定が型で明確になる
- 不正な組み合わせを型で防げる
- 各ストレージタイプに必要な設定だけを含められる

#### 2. Port（インターフェース）は共通

```python
class StoragePort(ABC):
    @abstractmethod
    def save(self, key: str, data: bytes) -> None: ...

    @abstractmethod
    def get(self, key: str) -> bytes: ...
```

#### 3. Factory が config を解釈する

```python
def create_storage(config: StorageConfig) -> StoragePort:
    if isinstance(config, LocalStorageConfig):
        return LocalStorage(config.base_path)
    if isinstance(config, S3StorageConfig):
        return S3Storage(
            bucket=config.bucket,
            api_key=config.api_key,
            region=config.region,
        )
    raise ValueError("Unknown StorageConfig")
```

#### 4. 呼び出し側（UseCase）は「設定を渡すだけ」

```python
# UseCase内
storage = create_storage(input.storage)
storage.save(key, data)

# Entrypoint
config = S3StorageConfig(
    bucket="my-bucket",
    api_key=os.environ["API_KEY"],
    region="ap-northeast-1",
)
storage = create_storage(config)
```

---

## 判断基準チェックリスト

現在の実装を評価:

- [ ] `save/get`のシグネチャは共通 → ❌ 実装で不一致
- [ ] UseCase に`bucket`や`api_key`が出てこない → ✅ 現状 OK
- [ ] 差異は Config or Factory に閉じている → ⚠️ URI パースが複雑
- [ ] 新しい storage を足しても UseCase は無変更 → ⚠️ URI パースロジック修正が必要

---

## 改善提案

### 優先度: 高

1. **設定オブジェクトの分離**

   - `LocalStorageConfig`と`S3StorageConfig`を分離
   - 基底クラス`StorageConfig`を作成

2. **型の修正**

   - `S3Storage`と`LocalStorage`の`__init__`の型を修正
   - `StorageConfig`の各サブクラスを受け取るように変更

3. **メソッドシグネチャの統一**
   - `StoragePort.save()`のシグネチャに合わせて実装を修正

### 優先度: 中

4. **Factory の簡素化**

   - URI パースに依存しない`isinstance`ベースの判定に変更

5. **テスト容易性の向上**
   - 各 Config クラスが独立してテスト可能に

---

## まとめ

現在の実装は**Factory パターンを使用している点は良い**ですが、以下の改善が必要です:

1. ✅ **設定オブジェクトを分離する** - 型安全性と拡張性の向上
2. ✅ **型の不一致を修正する** - 実行時エラーの防止
3. ✅ **メソッドシグネチャを統一する** - インターフェース契約の遵守

提供された設計パターンに従うことで、より保守性が高く、拡張しやすい設計になります。

