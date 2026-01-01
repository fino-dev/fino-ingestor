# 静的型チェックの設定

## 概要

Python でも静的型チェックを厳密に行い、開発時にエラーを検出できるように設定しました。

## 設定内容

### 1. `typing.override`デコレータの使用

Python 3.12 以降で利用可能な`typing.override`デコレータを使用することで、オーバーライドの検証が厳密になります。

```python
from typing import override

class EdinetAdapter(Edinet):
    @override
    def get_document_list(
        self, date: date, withdocs: bool = False
    ) -> GetDocumentResponse | GetDocumentResponseWithDocs:
        # 基底クラスと完全に一致する必要がある
        # 不一致があると静的エラーになる
```

**効果**:

- 基底クラスに存在しないメソッドを`@override`でマークするとエラー
- 基底クラスとシグネチャが一致しないとエラー
- 引数名、型、必須/オプションの不一致を検出

### 2. mypy 設定（`pyproject.toml`）

```toml
[tool.mypy]
python_version = "3.13"
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
warn_unreachable = true
strict_equality = true
strict_optional = true
```

**効果**:

- 型アノテーションの欠落を検出
- 型の不一致を検出
- 未使用の変数やインポートを警告

### 3. pyright 設定（`pyrightconfig.json`）

```json
{
  "typeCheckingMode": "strict",
  "reportIncompatibleMethodOverride": "error",
  "reportIncompatibleFunctionOverride": "error",
  "reportArgumentType": "error",
  "reportCallIssue": "error",
  ...
}
```

**効果**:

- メソッドオーバーライドの不一致を検出
- 引数の型不一致を検出
- 関数呼び出しの問題を検出

## 使用方法

### VS Code / Cursor での使用

1. **Pylance 拡張機能**をインストール（pyright ベース）

   - 自動的に`pyrightconfig.json`を読み込む
   - エディタ上でリアルタイムにエラーを表示

2. **mypy 拡張機能**をインストール（オプション）
   - コマンドパレットから`mypy`を実行

### コマンドラインでの使用

```bash
# mypyでチェック
mypy src/fino_core

# pyrightでチェック
pyright src/fino_core
```

### CI/CD での使用

```yaml
# GitHub Actions例
- name: Type check
  run: |
    pip install mypy pyright
    mypy src/fino_core
    pyright src/fino_core
```

## 検出されるエラー例

### 1. 引数名の不一致

```python
# 基底クラス
class Edinet(ABC):
    @abstractmethod
    def get_document_list(self, date: date, hoge: bool) -> ...: ...

# 実装クラス（エラーになる）
class EdinetAdapter(Edinet):
    @override
    def get_document_list(self, date: date, hog: bool) -> ...:  # ❌ 引数名が異なる
        pass
```

### 2. 必須引数がデフォルト引数になる

```python
# 基底クラス
class Edinet(ABC):
    @abstractmethod
    def get_document_list(self, date: date, hoge: bool) -> ...: ...

# 実装クラス（エラーになる）
class EdinetAdapter(Edinet):
    @override
    def get_document_list(self, date: date, hoge: bool = False) -> ...:  # ❌ 必須がデフォルトに
        pass
```

### 3. 型の不一致

```python
# 基底クラス
class Edinet(ABC):
    @abstractmethod
    def get_document_list(self, date: date) -> ...: ...

# 実装クラス（エラーになる）
class EdinetAdapter(Edinet):
    @override
    def get_document_list(self, date: datetime.datetime) -> ...:  # ❌ 型が異なる
        pass
```

### 4. 追加の必須引数

```python
# 基底クラス
class Edinet(ABC):
    @abstractmethod
    def get_document_list(self, date: date) -> ...: ...

# 実装クラス（エラーになる）
class EdinetAdapter(Edinet):
    @override
    def get_document_list(self, date: date, extra: str) -> ...:  # ❌ 追加の必須引数
        pass
```

## 注意点

### `@override`の制限

- **Python 3.12 以降でのみ利用可能**
- 基底クラスに存在しないメソッドに`@override`を付けるとエラー
- 基底クラスと完全に一致する必要がある

### 型チェッカーの違い

- **mypy**: より保守的、厳密
- **pyright/pylance**: より柔軟、VS Code 統合が良い

両方を使用することで、より確実にエラーを検出できます。

## まとめ

Python でも以下の設定により、静的型チェックを厳密に行えます：

1. ✅ `typing.override`デコレータでオーバーライドを検証
2. ✅ mypy の strict モードで型チェックを厳密化
3. ✅ pyright の strict モードでメソッドオーバーライドを検証

これにより、**開発時にエラーを検出**でき、**実行時エラーを防ぐ**ことができます。

