"""
Database Models Module
Defines the relational schema for the Flask blog application using SQLAlchemy.
"""
from extensions import db
from flask_login import UserMixin
from sqlalchemy.orm import relationship


class User(UserMixin, db.Model):
    """Represents a registered user in the application."""
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)

    # Increased to 254 to accommodate the RFC 5321 standard for email length
    email = db.Column(db.String(254), unique=True, nullable=False)

    # Increased to 1000 to safely accommodate Bcrypt/Argon2 password hash outputs
    password = db.Column(db.String(1000), nullable=False)

    # Increased to 250 for safer text boundaries
    name = db.Column(db.String(250), nullable=False)

    is_admin = db.Column(db.Boolean, default=False)

    # Relationships
    posts = relationship("BlogPost", back_populates="author", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="comment_author", cascade="all, delete-orphan")


class BlogPost(db.Model):
    """Represents a blog post authored by a user."""
    __tablename__ = "blog_posts"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    author = relationship("User", back_populates="posts")

    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)

    # Text type allows for unlimited length content
    body = db.Column(db.Text, nullable=False)
    img_url = db.Column(db.String(250), nullable=False)

    # Relationships
    comments = relationship("Comment", back_populates="parent_post", cascade="all, delete-orphan")


class Comment(db.Model):
    """Represents a user comment on a specific blog post."""
    __tablename__ = "comments"

    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    comment_author = relationship("User", back_populates="comments")

    post_id = db.Column(db.Integer, db.ForeignKey("blog_posts.id"))
    parent_post = relationship("BlogPost", back_populates="comments")

    text = db.Column(db.Text, nullable=False)