from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/api/devocionais", tags=["devocionais"])


@router.get("", response_model=schemas.PaginatedDevotionals)
def list_devotionals(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=50),
    search: Optional[str] = None,
    category_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Devotional).filter(models.Devotional.is_published == True)

    if search:
        term = f"%{search}%"
        query = query.filter(
            or_(
                models.Devotional.title.ilike(term),
                models.Devotional.content.ilike(term),
                models.Devotional.bible_verse.ilike(term),
            )
        )

    if category_id:
        query = query.filter(models.Devotional.category_id == category_id)

    total = query.count()
    pages = max(1, (total + per_page - 1) // per_page)
    items = query.order_by(desc(models.Devotional.published_at), desc(models.Devotional.created_at)) \
                 .offset((page - 1) * per_page).limit(per_page).all()

    return {"items": items, "total": total, "page": page, "pages": pages}


@router.get("/admin", response_model=schemas.PaginatedDevotionals)
def list_devotionals_admin(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    search: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Devotional)

    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Devotional.author_id == current_user.id)

    if search:
        term = f"%{search}%"
        query = query.filter(models.Devotional.title.ilike(term))

    total = query.count()
    pages = max(1, (total + per_page - 1) // per_page)
    items = query.order_by(desc(models.Devotional.created_at)) \
                 .offset((page - 1) * per_page).limit(per_page).all()

    return {"items": items, "total": total, "page": page, "pages": pages}


@router.get("/admin/{devotional_id}", response_model=schemas.DevotionalOut)
def get_devotional_admin(
    devotional_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    query = db.query(models.Devotional).filter(models.Devotional.id == devotional_id)
    if current_user.role != models.UserRole.admin:
        query = query.filter(models.Devotional.author_id == current_user.id)
    devotional = query.first()
    if not devotional:
        raise HTTPException(status_code=404, detail="Devocional não encontrado")
    return devotional


@router.get("/{devotional_id}", response_model=schemas.DevotionalOut)
def get_devotional(devotional_id: int, db: Session = Depends(get_db)):
    devotional = db.query(models.Devotional).filter(
        models.Devotional.id == devotional_id,
        models.Devotional.is_published == True,
    ).first()
    if not devotional:
        raise HTTPException(status_code=404, detail="Devocional não encontrado")
    return devotional


@router.post("", response_model=schemas.DevotionalOut, status_code=status.HTTP_201_CREATED)
def create_devotional(
    data: schemas.DevotionalCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    devotional = models.Devotional(
        **data.model_dump(exclude={'published_at'}),
        author_id=current_user.id,
        published_at=data.published_at or (datetime.utcnow() if data.is_published else None),
    )
    db.add(devotional)
    db.commit()
    db.refresh(devotional)
    return devotional


@router.put("/{devotional_id}", response_model=schemas.DevotionalOut)
def update_devotional(
    devotional_id: int,
    data: schemas.DevotionalUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    devotional = db.query(models.Devotional).filter(models.Devotional.id == devotional_id).first()
    if not devotional:
        raise HTTPException(status_code=404, detail="Devocional não encontrado")

    if current_user.role != models.UserRole.admin and devotional.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para editar esta devocional")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(devotional, field, value)

    if data.is_published and not devotional.published_at:
        devotional.published_at = datetime.utcnow()

    db.commit()
    db.refresh(devotional)
    return devotional


@router.delete("/{devotional_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_devotional(
    devotional_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(auth.get_current_user),
):
    devotional = db.query(models.Devotional).filter(models.Devotional.id == devotional_id).first()
    if not devotional:
        raise HTTPException(status_code=404, detail="Devocional não encontrado")

    if current_user.role != models.UserRole.admin and devotional.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Sem permissão para excluir esta devocional")

    db.delete(devotional)
    db.commit()
