# Fino

### アーキテクチャ概要

- AWS Cloud にホスト
- サーバーレス・マネージドサービスを活用して、コスト削減
- 初期段階は、イベント駆動により、常時稼働を行わない構成
- Iceberg テーブルスキーマにより、拡張しやすい形のデータ・レイクハウスを構築
- 様々な形式のデータを取り込めるように、中継ストレージを S3 で導入

<img src="./docs/assets/architecture.png" width="1000px" />

### コンポーネント・サービス群

---

##### Hoth（Data LakeHouse）

##### Kamino（Ingestion Workflow & RAQ Data Strorage）

##### Naboo（Portfolio Service）

##### Bespin（Bashboard）

##### Coruscant（Jupyter Nootebook）
