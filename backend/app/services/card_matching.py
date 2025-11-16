"""
Service de matching entre les informations détectées et la base complète des cartes.
"""
from __future__ import annotations

import unicodedata
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Sequence

from rapidfuzz import fuzz  # type: ignore
from sqlalchemy.orm import Session, joinedload

from app.config import get_settings
from app.models.card import Card
from app.models.set import Set


@dataclass
class CardCandidate:
    card_id: str
    name: str
    set_id: str
    set_name: str
    local_id: str
    rarity: Optional[str]
    score: float

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["score"] = round(self.score, 4)
        return payload


class CardMatchingService:
    def __init__(self, db: Session):
        self.db = db
        self.settings = get_settings()

    def _normalize(self, value: Optional[str]) -> str:
        if not value:
            return ""
        normalized = unicodedata.normalize("NFKD", value)
        return normalized.lower().strip()

    def find_candidates(
        self,
        *,
        probable_name: Optional[str],
        local_number: Optional[str],
        set_hint: Optional[str],
        limit: Optional[int] = None,
    ) -> List[CardCandidate]:
        limit = limit or self.settings.analysis_max_candidates
        query = self.db.query(Card).options(joinedload(Card.set))

        if local_number:
            query = query.filter(Card.local_id == local_number)
        if set_hint:
            query = query.join(Set)
            query = query.filter(Set.id.ilike(f"{set_hint.lower()}%") | Set.name.ilike(f"%{set_hint}%"))

        cards: Sequence[Card] = query.limit(200).all() if query.column_descriptions else []
        if not cards:
            cards = self.db.query(Card).options(joinedload(Card.set)).limit(400).all()

        norm_name = self._normalize(probable_name)

        scored: List[CardCandidate] = []
        for card in cards:
            score_components: Dict[str, float] = {}

            if norm_name:
                score_components["name"] = fuzz.token_sort_ratio(norm_name, self._normalize(card.name)) / 100
            if local_number:
                score_components["number"] = 1.0 if card.local_id == local_number else 0.0
            if set_hint and card.set_id.lower().startswith(set_hint.lower()):
                score_components["set"] = 1.0

            base_score = (
                0.65 * score_components.get("name", 0.0)
                + 0.25 * score_components.get("number", 0.0)
                + 0.10 * score_components.get("set", 0.0)
            )

            if not score_components and not norm_name:
                base_score = 0.5  # Score neutre quand aucune info n'est disponible

            if base_score <= 0:
                continue

            scored.append(
                CardCandidate(
                    card_id=card.id,
                    name=card.name,
                    set_id=card.set_id,
                    set_name=card.set.name if card.set else "",
                    local_id=card.local_id,
                    rarity=card.rarity,
                    score=min(0.99, base_score),
                )
            )

        scored.sort(key=lambda c: c.score, reverse=True)
        return scored[:limit]
