from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
import enum
from .database import Base


class UserRole(str, enum.Enum):
    admin = "admin"
    author = "author"


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.author)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    devotionals = relationship("Devotional", back_populates="author", cascade="all, delete-orphan")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    slug = Column(String(100), unique=True, nullable=False)
    description = Column(String(255), nullable=True)

    devotionals = relationship("Devotional", back_populates="category")


class Devotional(Base):
    __tablename__ = "devotionals"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False)
    content = Column(Text, nullable=False)
    bible_verse = Column(String(100), nullable=True)
    bible_text = Column(Text, nullable=True)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
    is_published = Column(Boolean, default=True)
    published_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    author = relationship("User", back_populates="devotionals")
    category = relationship("Category", back_populates="devotionals")
    comments = relationship("Comment", back_populates="devotional", cascade="all, delete-orphan")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    devotional_id = Column(Integer, ForeignKey("devotionals.id"), nullable=False)
    author_name = Column(String(100), nullable=False)
    author_email = Column(String(255), nullable=True)
    content = Column(Text, nullable=False)
    is_approved = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    devotional = relationship("Devotional", back_populates="comments")
