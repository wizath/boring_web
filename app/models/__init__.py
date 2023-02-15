from app.models.user import User
from sqlmodel import SQLModel, Field, select


class Model(SQLModel):

    @classmethod
    def query(cls):
        return select(cls)

    def filter(self):
        pass

    def all(self):
        pass

    def save(self):
        pass
