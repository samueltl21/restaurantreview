from typing import Optional
import sqlalchemy as sa
import sqlalchemy.orm as so
from app import db
from flask_login import UserMixin
import json

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
    
class SharedReview(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    sender_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    recipient_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    token: so.Mapped[str] = so.mapped_column(sa.String(64), unique=True, nullable=False)
    review_ids: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)  # JSON string of review IDs
    shared_at: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)  # new field for timestamp

    

    sender: so.Mapped["User"] = so.relationship(foreign_keys=[sender_id])
    recipient: so.Mapped["User"] = so.relationship(foreign_keys=[recipient_id])

class SharedComment(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    shared_review_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('shared_review.id'), nullable=False)
    user_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('user.id'), nullable=False)
    content: so.Mapped[str] = so.mapped_column(sa.Text, nullable=False)
    timestamp: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)
    
    user: so.Mapped["User"] = so.relationship()
    shared_review: so.Mapped["SharedReview"] = so.relationship()

class SharedReviewEntry(db.Model):
    id: so.Mapped[int] = so.mapped_column(primary_key=True)
    shared_review_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('shared_review.id'), nullable=False)
    review_id: so.Mapped[int] = so.mapped_column(sa.ForeignKey('review.id'), nullable=False)
    shared_at: so.Mapped[str] = so.mapped_column(sa.String(30), nullable=False)

    shared_review: so.Mapped["SharedReview"] = so.relationship()
    review: so.Mapped["Review"] = so.relationship()
