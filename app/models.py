from typing import Optional
from sqlalchemy import sa
from sqlalchemy.orm import so
from app import db

class User(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    name : so.Mapped[str] = so.mapped_column(sa.String(100), index=True, unique=True)
    email : so.Mapped[str] = so.mapped_column(sa.String(50), unique=True, nullable=False)
    password_hash: so Mapped[Optional[str]] = so.mapped_column(sa.String(100)), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'