"""
routes/content.py
POST   /generate-content
GET    /history
GET    /history/{id}
DELETE /history/{id}
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from database.db import get_db
from middleware.auth import get_current_user
from models.content import GeneratedContent
from models.user import User
from schemas.content import ContentGenerateRequest, ContentOut, HistoryListResponse
from services import ai_service

router = APIRouter(tags=["Content Generation"])


@router.post("/generate-content", response_model=ContentOut, status_code=status.HTTP_201_CREATED)
def generate_content(
    payload: ContentGenerateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Builds the AI prompt, calls the AI provider, and stores the result."""
    try:
        prompt, generated_text = ai_service.generate_ai_content(
            content_type=payload.content_type.value,
            product_name=payload.product_name,
            tone=payload.tone,
            extra_details=payload.extra_details,
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    record = GeneratedContent(
        user_id=current_user.id,
        content_type=payload.content_type.value,
        prompt=prompt,
        generated_content=generated_text,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return record


@router.get("/history", response_model=HistoryListResponse)
def get_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Returns the current user's past generated content, most recent first."""
    base_query = db.query(GeneratedContent).filter(GeneratedContent.user_id == current_user.id)
    total = base_query.count()
    items = (
        base_query.order_by(GeneratedContent.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
    return HistoryListResponse(total=total, items=items)


@router.get("/history/{content_id}", response_model=ContentOut)
def get_history_item(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.id == content_id, GeneratedContent.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="History item not found")
    return record


@router.delete("/history/{content_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_history_item(
    content_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    record = (
        db.query(GeneratedContent)
        .filter(GeneratedContent.id == content_id, GeneratedContent.user_id == current_user.id)
        .first()
    )
    if not record:
        raise HTTPException(status_code=404, detail="History item not found")

    db.delete(record)
    db.commit()
    return None
