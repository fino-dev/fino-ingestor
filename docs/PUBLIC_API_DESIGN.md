# Fino Core 公開 API 設計

## 概要

このドキュメントでは、`fino_core`パッケージの公開 API 設計について説明します。

## 設計方針

### 1. Facade パターンの採用

ユーザーがパッケージを簡単に使用できるように、Facade パターンを採用しています。`DocumentCollector`クラスが、内部の複雑なユースケースや依存関係を隠蔽し、シンプルなインターフェースを提供します。

### 2. 依存性注入（DI）

`DocumentCollector`は、以下の依存関係をコンストラクタで受け取ります：

- `DisclosureSourcePort`: データソース（EDINET 等）へのアクセス
- `DocumentRepository`: ドキュメントメタデータの永続化

これにより、ユーザーは自身の環境に合わせた実装を提供できます。

### 3. Port-Adapter パターン

インフラストラクチャへの依存を抽象化するため、Port インターフェースを定義しています：

- `DisclosureSourcePort`: データソースとの通信を抽象化
- `StoragePort`: ストレージへのアクセスを抽象化
- `DocumentRepository`: リポジトリパターンでデータアクセスを抽象化

## 公開 API 構造

### パッケージエクスポート

`fino_core/__init__.py`から以下をエクスポートしています：

#### メイン Facade

- `DocumentCollector`: ドキュメント収集・管理のメインクラス

#### Domain Entities

- `Document`: ドキュメントのエンティティ
- `DisclosureSource`: 開示情報源のエンティティ

#### Domain Values

- `Ticker`: 銘柄コード
- `DocumentId`: ドキュメント ID
- `DisclosureDate`: 開示日
- `DisclosureType`: 開示種別
- `FormatType`: ファイル形式
- `DocumentSearchCriteria`: ドキュメント検索条件

#### Ports（実装が必要）

- `DisclosureSourcePort`: データソースインターフェース
- `StoragePort`: ストレージインターフェース
- `DocumentRepository`: リポジトリインターフェース

#### Utilities

- `TimeScope`: 期間指定のためのユーティリティクラス

## DocumentCollector クラス API

### コンストラクタ

```python
def __init__(
    self,
    disclosure_source: DisclosureSourcePort,
    document_repository: DocumentRepository
) -> None
```

### メソッド

#### collect_documents

```python
def collect_documents(
    self,
    timescope: Optional[TimeScope] = None,
    tickers: Optional[list[Ticker]] = None,
) -> list[Document]
```

指定された条件に基づいてドキュメントを収集します。データソースから利用可能なドキュメントを取得し、まだ保存されていないものをダウンロード・保存します。

**パラメータ:**

- `timescope`: 収集対象の期間（None の場合、tickers が必須）
- `tickers`: 収集対象のティッカーリスト（None の場合、timescope が必須）

**戻り値:**

- 新しく収集されたドキュメントのリスト

#### list_available_documents

```python
def list_available_documents(
    self,
    timescope: Optional[TimeScope] = None,
    tickers: Optional[list[Ticker]] = None,
) -> list[Document]
```

データソースから取得可能なドキュメントのリストを返します。

**パラメータ:**

- `timescope`: 検索対象の期間（None の場合、tickers が必須）
- `tickers`: 検索対象のティッカーリスト（None の場合、timescope が必須）

**戻り値:**

- データソースで利用可能なドキュメントのリスト

#### list_stored_documents

```python
def list_stored_documents(
    self,
    timescope: Optional[TimeScope] = None,
    tickers: Optional[list[Ticker]] = None,
) -> list[Document]
```

ストレージに保存済みのドキュメントのリストを返します。

**パラメータ:**

- `timescope`: 検索対象の期間（None の場合、tickers が必須）
- `tickers`: 検索対象のティッカーリスト（None の場合、timescope が必須）

**戻り値:**

- ストレージに保存済みのドキュメントのリスト

#### list_documents

```python
def list_documents(
    self,
    timescope: Optional[TimeScope] = None,
    tickers: Optional[list[Ticker]] = None,
) -> tuple[list[Document], list[Document]]
```

利用可能なドキュメントと保存済みドキュメントの両方を取得します。効率的に両方の情報を取得したい場合に使用します。

**パラメータ:**

- `timescope`: 検索対象の期間（None の場合、tickers が必須）
- `tickers`: 検索対象のティッカーリスト（None の場合、timescope が必須）

**戻り値:**

- (利用可能なドキュメントリスト, 保存済みドキュメントリスト)のタプル

## 設計の利点

### 1. シンプルな使用感

ユーザーは複雑な内部構造を意識せず、`DocumentCollector`のメソッドを呼び出すだけで金融データの収集・管理ができます。

### 2. 柔軟な拡張性

新しいデータソースやストレージを追加する場合、対応する Port インターフェースを実装するだけで対応できます。コアロジックの変更は不要です。

### 3. テスタビリティ

依存性注入により、テスト時にモックやスタブを簡単に差し込むことができます。

### 4. Clean Architecture 準拠

ドメインロジックがインフラストラクチャから独立しており、ビジネスルールの変更がインフラストラクチャの実装に影響しません。

## アーキテクチャレイヤー

```
┌─────────────────────────────────────────┐
│          User Application               │ ← ユーザーのコード
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Interface Layer (Facade)            │
│     - DocumentCollector                 │ ← 公開API
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Application Layer (Use Cases)       │
│     - CollectDocumentUseCase            │
│     - ListDocumentUseCase               │ ← ビジネスロジック
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Domain Layer                        │
│     - Entities, Value Objects           │
│     - Repository Interfaces             │ ← ドメインモデル
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Interface Layer (Ports)             │
│     - DisclosureSourcePort              │
│     - StoragePort               │ ← インターフェース定義
│     - DocumentRepository                │
└─────────────────┬───────────────────────┘
                  │
┌─────────────────▼───────────────────────┐
│     Infrastructure Layer (Adapters)     │
│     - EDINETSource                      │
│     - LocalStorage / S3Storage          │ ← ユーザーが実装
│     - DocumentRepositoryImpl            │
└─────────────────────────────────────────┘
```

## 使用例

詳細な使用例については、`USAGE_GUIDE.md`を参照してください。

## 今後の拡張予定

- バッチ処理のサポート
- 非同期処理のサポート
- プログレスコールバックの追加
- より詳細な検索条件のサポート
- キャッシング機構の追加
