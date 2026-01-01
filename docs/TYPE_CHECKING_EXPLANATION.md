# 型チェッカーが基底クラスの不一致を検出しない理由

## 問題の状況

`infrastructure/edinet.py`の`EdinetAdapter`クラスが、基底クラス`Edinet`の`get_document_list`メソッドをオーバーライドする際に、基底クラスに存在しない`hog`引数を追加していますが、静的エラーになっていません。

### 基底クラス（`model/edinet.py`）

```python
class Edinet(ABC):
    @abstractmethod
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs: ...
```

### 実装クラス（`infrastructure/edinet.py`）

```python
class EdinetAdapter(Edinet):
    def get_document_list(
        self, date: datetime.datetime, withdocs: bool = False, hog: bool = False
    ) -> Union[GetDocumentResponse, GetDocumentResponseWithDocs]:
        # ...
```

## なぜ静的エラーにならないのか

### 1. Python の型システムの制限

Python の型チェッカー（mypy、pyright 等）は、**デフォルト引数を持つ追加パラメータ**については、デフォルトでは警告を出しません。

**理由**:

- デフォルト引数があるため、基底クラスのシグネチャで呼び出しても技術的には動作する
- 例: `edinet.get_document_list(date, withdocs=True)` は `hog` 引数なしで呼び出せる

### 2. 型チェッカーの設定

現在のプロジェクトには型チェッカーの設定ファイル（`mypy.ini`、`pyrightconfig.json`等）が見当たりません。デフォルト設定では、この種の不一致は検出されないことがあります。

### 3. Liskov Substitution Principle の違反

技術的には動作しますが、**Liskov Substitution Principle（LSP）に違反**しています：

- 基底クラスの型シグネチャと一致していない
- 呼び出し側が基底クラスの型で使用する場合、`hog`引数は使用できない
- 型の不一致: `date: date` vs `date: datetime.datetime`

## 解決方法

### 方法 1: `typing.override`デコレータを使用（推奨）

Python 3.12 以降では、`typing.override`デコレータを使用することで、オーバーライドの検証がより厳密になります。

```python
from typing import override

class EdinetAdapter(Edinet):
    @override
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs:
        # hog引数を削除し、基底クラスのシグネチャに合わせる
        # ...
```

### 方法 2: 型チェッカーの設定を厳密にする

`pyproject.toml`に mypy の設定を追加：

```toml
[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
check_untyped_defs = true
```

### 方法 3: 基底クラスのシグネチャを拡張する

もし`hog`引数が本当に必要なら、基底クラスにも追加する：

```python
class Edinet(ABC):
    @abstractmethod
    def get_document_list(
        self, date: date, withdocs: bool = False, hog: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs: ...
```

### 方法 4: 型の不一致を修正する

`date: datetime.datetime`を`date: date`に修正：

```python
from datetime import date

class EdinetAdapter(Edinet):
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs:
        # datetime.datetimeではなくdateを使用
        # ...
```

## 推奨される修正

1. **`hog`引数を削除**（使用されていない場合）
2. **`date: datetime.datetime`を`date: date`に修正**
3. **`typing.override`デコレータを追加**（Python 3.12 以降）

修正例：

```python
from typing import override
from datetime import date

class EdinetAdapter(Edinet):
    @override
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs:
        # hog引数を削除
        # date型を使用
        # ...
```

