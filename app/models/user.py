from typing import Optional

from pydantic import PrivateAttr
from sqlmodel import SQLModel, Field

from app.auth import verify_password, get_hashed_password


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: Optional[str]
    is_superuser: bool = False
    is_active: bool = False
    username: str
    name: str
    email: str
    _token: str = PrivateAttr(default=None)

    @property
    def token(self):
        return self._token

    def set_token(self, token):
        self._token = token

    def set_password(self, password):
        self.password = get_hashed_password(password)

    def check_password(self, password):
        return verify_password(password, self.password)
