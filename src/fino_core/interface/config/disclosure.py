from pydantic import BaseModel


class EdinetConfig(BaseModel):
    api_key: str
