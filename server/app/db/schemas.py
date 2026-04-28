from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str | None = None


class UserRead(BaseModel):
    id: int
    email: str
    full_name: str | None = None
    is_active: bool = True

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    id: int | None = None
