from pydantic import BaseModel


class AuthContext(BaseModel):
    user_id: str
    roles: list[str]
    is_authenticated: bool
