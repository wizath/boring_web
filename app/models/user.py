from typing import Optional
from app.auth import verify_password, get_hashed_password
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    password: Optional[str]
    is_superuser: bool = False
    username: str
    name: str
    email: str

    def set_password(self, password):
        self.password = get_hashed_password(password)

    def check_password(self, password):
        return verify_password(self.password, password)
