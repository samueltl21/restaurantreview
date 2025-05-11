from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    id : so.Mapped[int] = so.mapped_column(primary_key=True)
    name : so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)
    email : so.Mapped[str] = so.mapped_column(sa.String(50), unique=True, nullable=False)
    password_hash: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False)

    reviews: so.Mapped[list["Review"]] = so.relationship(back_populates="user")

    def __repr__(self):
        return f'<User {self.email}>'
    
class Restaurant(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    name: so.Mapped[str] = so.mapped_column(sa.String(100), nullable=False, unique=True)
    location: so.Mapped[str] = so.mapped_column(sa.String(150), nullable=False)
    cuisine: so.Mapped[str] = so.mapped_column(sa.String(50), nullable=False)
    added_by: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    image: so.Mapped[Optional[str]] = so.mapped_column(sa.String(255), nullable=True)

    reviews: so.Mapped[list["Review"]] = so.relationship(back_populates="restaurant")


    def __repr__(self):
        return f"<Restaurant {self.name}>"

class Review(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    date: so.Mapped[str] = so.mapped_column(sa.String(10), nullable=False)  # Format: YYYY-MM-DD
    rating: so.Mapped[int] = so.mapped_column(sa.Integer, nullable=False)
    spend: so.Mapped[float] = so.mapped_column(sa.Float, nullable=False)
    comment: so.Mapped[Optional[str]] = so.mapped_column(sa.Text, nullable=True)


    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    restaurant_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('restaurant.id'), nullable=False)

    user: so.Mapped["User"] = so.relationship(back_populates="reviews")
    restaurant: so.Mapped["Restaurant"] = so.relationship(back_populates="reviews")

    def __repr__(self):
        return f"<Review {self.id}>"