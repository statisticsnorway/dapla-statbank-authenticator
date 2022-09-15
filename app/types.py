from pydantic import BaseModel


class EncryptionRequest(BaseModel):
    message: str


class EncryptionResponse(BaseModel):
    message: str
