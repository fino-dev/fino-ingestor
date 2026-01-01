# 必須引数が不一致でもエラーにならない理由

## 現在の状況

### 基底クラス（`model/edinet.py`）

```python
class Edinet(ABC):
    @abstractmethod
    def get_document_list(
        self, date: date, hoge: bool, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs: ...
```

- `hoge: bool` は**必須引数**（デフォルト値なし）

### 実装クラス（`infrastructure/edinet.py`）

```python
class EdinetAdapter(Edinet):
    def get_document_list(
        self, date: datetime.datetime, withdocs: bool = False, hog: bool = False
    ) -> Union[GetDocumentResponse, GetDocumentResponseWithDocs]:
        # ...
```

- `hog: bool = False` は**デフォルト引数**（デフォルト値あり）
- 引数名も`hoge`ではなく`hog`（typo？）

## なぜエラーにならないのか

### 1. Python の型チェッカーの制限

Python の型チェッカー（mypy、pyright 等）は、**メソッドのオーバーライド時に引数の不一致を完全には検証しません**。

**理由**:

- Python は動的型付け言語であり、実行時に型チェックが行われる
- 型チェッカーは「互換性がある」と判断する場合がある
- デフォルト引数があるため、技術的には呼び出し可能と判断される

### 2. 引数名の不一致が検出されない

- 基底クラス: `hoge: bool`（必須）
- 実装クラス: `hog: bool = False`（デフォルト引数）

**問題点**:

- 引数名が異なる（`hoge` vs `hog`）
- 必須引数がデフォルト引数に変わっている
- これらは**Liskov Substitution Principle に明らかに違反**しているが、型チェッカーは検出しない

### 3. 実行時エラーになる可能性

実際にコードを実行すると、以下のような問題が発生します：

```python
edinet: Edinet = EdinetAdapter(api_key="test")
# 基底クラスの型で呼び出すと、hoge引数が必須
edinet.get_document_list(date=date.today(), hoge=True)  # ❌ 実行時エラー: hog引数が見つからない
```

または：

```python
edinet: Edinet = EdinetAdapter(api_key="test")
# hoge引数を渡さないとエラーになるべきだが...
edinet.get_document_list(date=date.today())  # ❌ 基底クラスではhogeが必須なのに、実装ではデフォルト値がある
```

## 実際の問題

### 問題 1: 引数名の不一致

基底クラスでは`hoge`、実装クラスでは`hog`となっており、**完全に異なる引数**として扱われます。

### 問題 2: 必須引数がデフォルト引数に

基底クラスで必須の`hoge: bool`が、実装クラスでは`hog: bool = False`（デフォルト引数）になっています。これは**契約違反**です。

### 問題 3: 型の不一致

- 基底クラス: `date: date`
- 実装クラス: `date: datetime.datetime`

## なぜ型チェッカーが検出しないのか

### mypy の場合

mypy はデフォルトでは、以下のような不一致を検出しません：

1. **引数名の不一致** - 引数名は型チェックの対象外
2. **必須引数がデフォルト引数になる** - 互換性があると判断される場合がある
3. **追加の必須引数** - これは通常検出されるが、引数名が異なる場合は検出されないことがある

### pyright の場合

pyright も同様に、引数名の不一致や必須引数の扱いについて、デフォルトでは厳密にチェックしません。

## 解決方法

### 方法 1: 基底クラスと実装クラスのシグネチャを一致させる（推奨）

```python
# 基底クラス
class Edinet(ABC):
    @abstractmethod
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs: ...

# 実装クラス
class EdinetAdapter(Edinet):
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs:
        # hog/hoge引数を削除
        # ...
```

### 方法 2: `typing.override`デコレータを使用

Python 3.12 以降では、`typing.override`デコレータを使用することで、より厳密な検証が可能です：

```python
from typing import override

class EdinetAdapter(Edinet):
    @override
    def get_document_list(
        self, date: date, hoge: bool, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs:
        # 基底クラスと完全に一致させる
        # ...
```

### 方法 3: 型チェッカーの設定を厳密にする

`pyproject.toml`に設定を追加：

```toml
[tool.mypy]
strict = true
warn_unused_ignores = true
disallow_any_generics = true
disallow_subclassing_any = true
disallow_untyped_calls = true
disallow_untyped_defs = true
disallow_incomplete_defs = true
check_untyped_defs = true
disallow_untyped_decorators = true
no_implicit_optional = true
warn_redundant_casts = true
warn_unused_configs = true
warn_return_any = true
```

ただし、これでも引数名の不一致は検出されない可能性があります。

## 推奨される修正

1. **`hog`/`hoge`引数を削除**（使用されていない場合）
2. **引数名を統一**（`hoge`に統一するか、削除）
3. **型を統一**（`date: date`に統一）
4. **`typing.override`デコレータを追加**（Python 3.12 以降）

修正例：

```python
from typing import override
from datetime import date

class EdinetAdapter(Edinet):
    @override
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs:
        # hog/hoge引数を削除
        # date型を使用
        # ...
```

## まとめ

必須引数が不一致でもエラーにならない理由：

1. **Python の型チェッカーは引数名の不一致を検出しない**
2. **必須引数がデフォルト引数になることを検出しない場合がある**
3. **デフォルト引数があるため、技術的には呼び出し可能と判断される**

しかし、これは**実行時エラーの原因**となり、**Liskov Substitution Principle に違反**しています。必ず修正する必要があります。

