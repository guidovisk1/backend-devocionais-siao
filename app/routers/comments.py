from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(tags=["comentarios"])


@router.get("/api/devocionais/{devotional_id}/comentarios", response_model=List[schemas.CommentOut])
def list_comments(devotional_id: int, db: Session = Depends(get_db)):
    devotional = db.query(models.Devotional).filter(
        models.Devotional.id == devotional_id,
        models.Devotional.is_published == True,
    ).first()
    if not devotional:
        raise HTTPException(status_code=404, detail="Devocional não encontrado")

    return db.query(models.Comment).filter(
        models.Comment.devotional_id == devotional_id,
        models.Comment.is_approved == True,
    ).order_by(models.Comment.created_at).all()


@router.post(
    "/api/devocionais/{devotional_id}/comentarios",
    response_model=schemas.CommentOut,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(devotional_id: int, data: schemas.CommentCreate, db: Session = Depends(get_db)):
    devotional = db.query(models.Devotional).filter(
        models.Devotional.id == devotional_id,
        models.Devotional.is_published == True,
    ).first()
    if not devotional:
        raise HTTPException(status_code=404, detail="Devocional não encontrado")

    comment = models.Comment(devotional_id=devotional_id, **data.model_dump())
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/api/admin/comentarios", response_model=List[schemas.CommentAdminOut])
def list_all_comments(
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    return db.query(models.Comment).order_by(models.Comment.created_at.desc()).all()


@router.patch("/api/comentarios/{comment_id}/aprovar", response_model=schemas.CommentOut)
def approve_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    comment.is_approved = True
    db.commit()
    db.refresh(comment)
    return comment


@router.delete("/api/comentarios/{comment_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_comment(
    comment_id: int,
    db: Session = Depends(get_db),
    _: models.User = Depends(auth.require_admin),
):
    comment = db.query(models.Comment).filter(models.Comment.id == comment_id).first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comentário não encontrado")
    db.delete(comment)
    db.commit()
