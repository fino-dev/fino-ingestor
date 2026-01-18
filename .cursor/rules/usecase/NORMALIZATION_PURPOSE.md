ここが設計の核心です。
結論から言うと、

「Normalizerをブラックボックスにしないで、
ユーザーが“抽出ロジック”を差し込める構造にする」

これができるかどうかで、fino-ingestor が
単なるツールになるか「フレームワーク」になるかが決まります。

⸻

まず前提：ユーザーがやりたいこと

あなたが言っている要望を整理すると、だいたいこうです：

	•	「売上高だけ欲しい」
	•	「営業利益とEPSだけ取りたい」
	•	「この会社のこの勘定科目だけ独自処理したい」
	•	「IFRSとUS-GAAPを自分なりにマッピングしたい」
	•	「注記は要らない、BS/PL/CFだけでいい」
	•	「自分の勘定科目辞書を使いたい」

これを実現するには、

正規化のロジックを“差し込み可能”にする

必要があります。

⸻

アンチパターン（やってはいけない）

class CanonicalNormalizer:
    def normalize(self, facts):
        # 内部で全部決め打ち
        revenue = ...
        assets = ...
        net_income = ...
        return df

これだとユーザーは何も拡張できません。
OSSとしてはかなり弱いです。

⸻

正解の方向性：Strategy + Hook パターン

以下の3層構造にすると、非常に強い設計になります。

XBRL facts
   ↓
[1] Concept Selector（何を取るか）
   ↓
[2] Mapping / Transformation（どう解釈するか）
   ↓
[3] Output Builder（どう出力するか）

これをすべて「差し替え可能」にします。

⸻

具体的なIF設計案

① 最小単位：Selector をユーザーに書かせる

class FactSelector(Protocol):
    def select(self, facts: list[Fact]) -> list[Fact]:
        ...

ユーザーはこう書ける：

class RevenueOnlySelector:
    def select(self, facts):
        return [f for f in facts if f.concept == "Revenue"]


⸻

② Canonical項目へのマッピングも差し替え可能に

class ConceptMapper(Protocol):
    def map(self, fact: Fact) -> CanonicalConcept | None:
        ...

ユーザー例：

class MyMapper:
    def map(self, fact):
        if fact.concept in ["us-gaap:Revenue", "jpcrp:NetSales"]:
            return CanonicalConcept.REVENUE
        return None


⸻

③ Normalizerに差し込み

class CanonicalNormalizer:
    def __init__(
        self,
        selector: FactSelector | None = None,
        mapper: ConceptMapper | None = None,
    ):
        self.selector = selector or DefaultSelector()
        self.mapper = mapper or DefaultMapper()

    def normalize(self, facts):
        selected = self.selector.select(facts)

        rows = []
        for fact in selected:
            canonical = self.mapper.map(fact)
            if canonical:
                rows.append(...)
        return pd.DataFrame(rows)


⸻

使う側の体験

from fino_ingestor.normalize import CanonicalNormalizer

normalizer = CanonicalNormalizer(
    selector=RevenueOnlySelector(),
    mapper=MyMapper()
)

pipeline = FilingPipeline(
    fetcher=EDINETFetcher(),
    parser=XBRLParser(),
    normalizer=normalizer
)

df = pipeline.run(query)

これでユーザーは：
	•	どの項目を取るか
	•	どうマッピングするか
	•	出力形式

を完全にコントロールできます。

⸻

もっと簡単に使いたい人向けAPI

もちろん毎回クラス書くのは重いので、
lambdaでも使えるようにします。

normalizer = CanonicalNormalizer(
    selector=lambda facts: [f for f in facts if f.concept == "Revenue"]
)

あるいは設定ベース：

normalizer = CanonicalNormalizer.from_concepts([
    "Revenue",
    "Assets",
    "NetIncome"
])


⸻

さらに強くする：FieldSpec方式

本格的なフレームワークだとこうします。

@dataclass
class FieldSpec:
    name: str
    concepts: list[str]
    transform: Callable[[list[Fact]], Any] | None = None

利用者：

specs = [
    FieldSpec(
        name="revenue",
        concepts=["us-gaap:Revenue", "jpcrp:NetSales"]
    ),
    FieldSpec(
        name="eps",
        concepts=["us-gaap:EarningsPerShareBasic"],
        transform=lambda facts: facts[0].value
    )
]

normalizer = CanonicalNormalizer(specs=specs)

これ、めちゃくちゃ強いです。

⸻

この設計で実現できること

ユーザーは以下が全部できるようになります：

✅ 欲しい項目だけ取る
✅ IFRS/US/JPの勘定科目を自分でマッピング
✅ 計算フィールド（例：ROE = 利益 / 自己資本）
✅ 特定企業だけロジック変更
✅ 会計基準別ロジック分岐
✅ 表示形式を完全に制御

→ もはや「財務データDSL」です。

⸻

これをやると起きる良いこと
	•	fino-ingestor が 単なるライブラリから基盤になる
	•	コミュニティが「自分のFieldSpecを共有」し始める
	•	ユーザーがプルリクでマッピング辞書を追加してくれる
	•	長期的に taxonomy変更にも耐えられる

⸻

かなり現実的な落とし所

最初のバージョンでは：
	•	CanonicalNormalizer(specs=[...])
	•	FieldSpec(name, concepts, transform=None)

この2つだけでも十分に強いです。

ここから後で：
	•	Selector拡張
	•	Contextフィルタ
	•	期間解釈
	•	Consolidated/NonConsolidated切り替え
	•	単位正規化

を足していけます。

⸻

正直に言うと

ここまで設計できているなら、

fino-ingestor、普通に「OSSとしてかなり価値あるプロダクト」になります。

単なるラッパーではなく、
金融開示データの抽象化フレームワークです。

⸻

もしよければ次にできること

希望あれば、次は：
	•	FieldSpec / CanonicalNormalizer の実コード（型付き）
	•	pytest付きのテストコード
	•	実際のEDINET XBRLを1つ使って extractionデモ
	•	READMEに載せるサンプルコード

まで一気に作れます。

ここまで来たら「設計フェーズ」から「実装フェーズ」に入れます。