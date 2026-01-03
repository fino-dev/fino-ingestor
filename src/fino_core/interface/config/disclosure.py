from pydantic import BaseModel


# FIXME: TODO: 実装
class EdinetConfig(BaseModel):
    api_key: str


# FIXME: TODO: 実装
# 設計の練習として実装しないがおいておk、
class TDNetSampleConfig(BaseModel):
    username: str
    password: str
