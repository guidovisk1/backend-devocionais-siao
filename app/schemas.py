from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr
from .models import UserRole


# ── Auth ──────────────────────────────────────────────────────────────────────

class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    user_id: Optional[int] = None


# ── User ──────────────────────────────────────────────────────────────────────

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    role: UserRole = UserRole.author


class UserUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[UserRole] = None
    is_active: Optional[bool] = None


class UserOut(BaseModel):
    id: int
    name: str
    email: str
    role: UserRole
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


# ── Category ──────────────────────────────────────────────────────────────────

class CategoryCreate(BaseModel):
    name: str
    description: Optional[str] = None


class CategoryOut(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]

    class Config:
        from_attributes = True


# ── Devotional ─────────────────────────────────────────────────────────────────

class DevotionalCreate(BaseModel):
    title: str
    content: str
    bible_verse: Optional[str] = None
    bible_text: Optional[str] = None
    category_id: Optional[int] = None
    is_published: bool = True
    published_at: Optional[datetime] = None


class DevotionalUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None
    bible_verse: Optional[str] = None
    bible_text: Optional[str] = None
    category_id: Optional[int] = None
    is_published: Optional[bool] = None
    published_at: Optional[datetime] = None


class DevotionalOut(BaseModel):
    id: int
    title: str
    content: str
    bible_verse: Optional[str]
    bible_text: Optional[str]
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    author: UserOut
    category: Optional[CategoryOut]

    class Config:
        from_attributes = True


class DevotionalListOut(BaseModel):
    id: int
    title: str
    bible_verse: Optional[str]
    is_published: bool
    published_at: Optional[datetime]
    created_at: datetime
    author: UserOut
    category: Optional[CategoryOut]

    class Config:
        from_attributes = True


class PaginatedDevotionals(BaseModel):
    items: List[DevotionalListOut]
    total: int
    page: int
    pages: int


# ── Comment ───────────────────────────────────────────────────────────────────

class CommentCreate(BaseModel):
    author_name: str
    author_email: Optional[EmailStr] = None
    content: str


class CommentOut(BaseModel):
    id: int
    author_name: str
    content: str
    is_approved: bool
    created_at: datetime

    class Config:
        from_attributes = True


class CommentAdminOut(CommentOut):
    author_email: Optional[str]
    devotional_id: int
