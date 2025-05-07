from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db

class User(db.Model):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    name : so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    email : so.Mapped[str] = so.mapped_column(sa.String(50), unique=True, nullable=False)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'
    
class Restaurant(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False, unique=True)
    location: so.Mapped[str] = so.mapped_column(sa.String(150), nullable=False)
    cuisine: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    added_by: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f"<Restaurant {self.name}>"
