"""
Routes d'import et d'analyse d'images FilePond -> FastAPI.
"""
from __future__ import annotations

import io
import uuid
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from PIL import Image
from sqlalchemy.orm import Session, selectinload

from app.config import get_settings
from app.database import get_db
from app.models.analysis_image import AnalysisImage
from app.models.card import Card
from app.models.card_draft import CardDraft, CardDraftStatus
from app.models.user_card import CardCondition, UserCard
from app.schemas.imports import (
    CardDraftResponse,
    CardSelectionRequest,
    CardSelectionResponse,
    CardCandidate,
    ImageBatchResponse,
    UserCardResponse,
    UserMasterSetResponse,
)
from app.services.card_matching import CardMatchingService
from app.services.image_analysis import DetectedCardFeatures, ImageAnalyzer
from app.services.image_store import ImageStorageService
from app.services.master_set import MasterSetProgressService
from app.utils.dependencies import get_current_user
from app.models.user import User

router = APIRouter(
    prefix="/imports",
    tags=["imports"],
)


def _draft_to_response(draft: CardDraft) -> CardDraftResponse:
    metadata = draft.detected_metadata or {}
    candidate_objects = [
        CardCandidate(**candidate) for candidate in (draft.candidates or [])
    ]

    return CardDraftResponse(
        id=draft.id,
        batch_id=draft.batch_id,
        image_id=draft.image_id,
        image_url=f"/imports/images/{draft.image_id}",
        status=draft.status,
        candidates=candidate_objects,
        top_candidate_id=draft.top_candidate_id,
        top_candidate_score=draft.top_candidate_score,
        detected_metadata=metadata or None,
        created_at=draft.created_at,
    )


@router.post("/batches", response_model=ImageBatchResponse, status_code=status.HTTP_201_CREATED)
async def create_import_batch(
    files: List[UploadFile] = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if not files:
        raise HTTPException(status_code=400, detail="Aucun fichier fourni")

    storage = ImageStorageService()
    analyzer = ImageAnalyzer()
    matcher = CardMatchingService(db)
    settings = get_settings()

    batch_id = uuid.uuid4()
    created_drafts: List[CardDraft] = []

    for uploaded in files:
        content = await uploaded.read()
        if not content:
            continue

        image_uuid, redis_key = storage.save_image(content)
        pil_image = Image.open(io.BytesIO(content))
        width, height = pil_image.size

        image_record = AnalysisImage(
            id=uuid.UUID(image_uuid),
            user_id=current_user.id,
            redis_key=redis_key,
            filename=uploaded.filename or f"image-{image_uuid}.png",
            content_type=uploaded.content_type or "image/png",
            width=width,
            height=height,
            ttl_seconds=settings.image_ttl_seconds,
            expires_at=datetime.utcnow() + timedelta(seconds=settings.image_ttl_seconds),
            status="stored",
        )
        db.add(image_record)
        db.flush()

        detections = analyzer.analyze(content)
        if not detections:
            detections = [
                DetectedCardFeatures(
                    bounding_box=(0, 0, width, height),
                    raw_text="",
                    probable_name=None,
                    local_number=None,
                    set_hint=None,
                )
            ]

        for detection in detections[: settings.max_cards_per_image]:
            candidates = matcher.find_candidates(
                probable_name=detection.probable_name,
                local_number=detection.local_number,
                set_hint=detection.set_hint,
            )
            candidates_payload = [candidate.to_dict() for candidate in candidates]
            status_value = (
                CardDraftStatus.awaiting_validation.value
                if candidates_payload
                else CardDraftStatus.pending.value
            )
            top_candidate_id = candidates_payload[0]["card_id"] if candidates_payload else None
            top_candidate_score = candidates_payload[0]["score"] if candidates_payload else None

            draft = CardDraft(
                batch_id=batch_id,
                user_id=current_user.id,
                image_id=image_record.id,
                status=status_value,
                candidates=candidates_payload,
                top_candidate_id=top_candidate_id,
                top_candidate_score=top_candidate_score,
                detected_metadata=detection.to_payload(),
            )
            db.add(draft)
            created_drafts.append(draft)

        image_record.status = "analyzed"

    db.commit()
    for draft in created_drafts:
        db.refresh(draft)

    return ImageBatchResponse(
        batch_id=batch_id,
        drafts=[_draft_to_response(d) for d in created_drafts],
    )


@router.get("/batches/{batch_id}", response_model=ImageBatchResponse)
def get_batch(
    batch_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    drafts = (
        db.query(CardDraft)
        .filter(CardDraft.batch_id == batch_id, CardDraft.user_id == current_user.id)
        .order_by(CardDraft.created_at)
        .all()
    )
    if not drafts:
        raise HTTPException(status_code=404, detail="Batch introuvable")
    return ImageBatchResponse(
        batch_id=batch_id,
        drafts=[_draft_to_response(d) for d in drafts],
    )


@router.get("/drafts/{draft_id}", response_model=CardDraftResponse)
def get_draft(
    draft_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = (
        db.query(CardDraft)
        .options(selectinload(CardDraft.image))
        .filter(CardDraft.id == draft_id, CardDraft.user_id == current_user.id)
        .first()
    )
    if not draft:
        raise HTTPException(status_code=404, detail="Draft introuvable")
    return _draft_to_response(draft)


@router.get("/images/{image_id}")
def get_image(
    image_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    image = (
        db.query(AnalysisImage)
        .filter(AnalysisImage.id == image_id, AnalysisImage.user_id == current_user.id)
        .first()
    )
    if not image:
        raise HTTPException(status_code=404, detail="Image introuvable")

    storage = ImageStorageService()
    content = storage.fetch_image(image.redis_key)
    if not content:
        image.status = "expired"
        db.commit()
        raise HTTPException(status_code=404, detail="Image expirée")

    storage.touch(image.redis_key)
    image.refresh_ttl()
    db.commit()

    return StreamingResponse(
        io.BytesIO(content),
        media_type=image.content_type or "image/png",
    )


@router.post("/drafts/{draft_id}/select", response_model=CardSelectionResponse)
def select_card(
    draft_id: UUID,
    payload: CardSelectionRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    draft = (
        db.query(CardDraft)
        .options(selectinload(CardDraft.image))
        .filter(CardDraft.id == draft_id, CardDraft.user_id == current_user.id)
        .first()
    )
    if not draft:
        raise HTTPException(status_code=404, detail="Draft introuvable")
    if draft.status == CardDraftStatus.validated.value:
        raise HTTPException(status_code=400, detail="Draft déjà validé")

    card = db.query(Card).filter(Card.id == payload.card_id).first()
    if not card:
        raise HTTPException(status_code=404, detail="Carte introuvable")

    allowed_conditions = {c.value for c in CardCondition}
    condition_value = payload.condition or CardCondition.near_mint.value
    if condition_value not in allowed_conditions:
        raise HTTPException(status_code=400, detail="Condition invalide")

    price_value = Decimal(str(payload.price_paid)) if payload.price_paid is not None else None

    user_card = UserCard(
        user_id=current_user.id,
        card_id=card.id,
        draft_id=draft.id,
        quantity=payload.quantity,
        condition=condition_value,
        price_paid=price_value,
        acquired_at=payload.acquired_at,
        notes=payload.notes,
    )
    db.add(user_card)
    draft.mark_validated(card.id)

    master_set_service = MasterSetProgressService(db)
    master_set = master_set_service.sync_progress(current_user.id, card.set_id)

    db.commit()
    db.refresh(user_card)
    db.refresh(draft)

    return CardSelectionResponse(
        draft=_draft_to_response(draft),
        user_card=UserCardResponse.model_validate(user_card),
        master_set=UserMasterSetResponse.model_validate(master_set),
    )
