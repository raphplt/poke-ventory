"""
Pipeline locale d'analyse d'image :
- détecte grossièrement les cartes présentes sur une image
- extrait des features textuelles (nom, numéro, set)
"""
from __future__ import annotations

import io
import re
import unicodedata
from dataclasses import dataclass, asdict
from typing import List, Optional, Tuple

from PIL import Image

try:
    import cv2  # type: ignore
    import numpy as np  # type: ignore
except Exception:  # pragma: no cover - OpenCV optionnel en local
    cv2 = None  # type: ignore
    np = None  # type: ignore

try:  # pragma: no cover - OCR optionnel
    import pytesseract  # type: ignore
except Exception:  # pragma: no cover
    pytesseract = None  # type: ignore


@dataclass
class DetectedCardFeatures:
    bounding_box: Tuple[int, int, int, int]
    raw_text: str
    probable_name: Optional[str]
    local_number: Optional[str]
    set_hint: Optional[str]

    def to_payload(self) -> dict:
        return asdict(self)


class ImageAnalyzer:
    """
    Détecte les cartes (rectangles) dans une image et extrait des informations.
    """

    def __init__(self) -> None:
        self.minimum_area = 7_500

    def analyze(self, image_bytes: bytes) -> List[DetectedCardFeatures]:
        image, fallback_box = self._load_image(image_bytes)
        if image is None:
            return []

        boxes = self._detect_boxes(image) or [fallback_box]
        detections: List[DetectedCardFeatures] = []
        for (x, y, w, h) in boxes[:4]:
            crop = image[y : y + h, x : x + w]
            text = self._extract_text(crop)
            parsed = self._parse_text(text)
            detections.append(
                DetectedCardFeatures(
                    bounding_box=(int(x), int(y), int(w), int(h)),
                    raw_text=text,
                    probable_name=parsed.get("probable_name"),
                    local_number=parsed.get("local_number"),
                    set_hint=parsed.get("set_hint"),
                )
            )
        return detections

    def _load_image(self, data: bytes) -> tuple[Optional["np.ndarray"], Tuple[int, int, int, int]]:
        if np is None or cv2 is None:
            # Fallback PIL -> numpy
            pil_image = Image.open(io.BytesIO(data)).convert("RGB")
            arr = np.array(pil_image) if np is not None else None  # type: ignore
            if arr is None:
                return None, (0, 0, 0, 0)
            h, w = arr.shape[:2]
            return arr, (0, 0, w, h)

        array = np.frombuffer(data, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_COLOR)
        if image is None:
            return None, (0, 0, 0, 0)
        h, w = image.shape[:2]
        return image, (0, 0, w, h)

    def _detect_boxes(self, image: "np.ndarray") -> List[Tuple[int, int, int, int]]:
        if cv2 is None:
            return []

        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        edged = cv2.Canny(blur, 20, 120)
        dilated = cv2.dilate(edged, None, iterations=2)
        contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        boxes: List[Tuple[int, int, int, int]] = []
        for contour in contours:
            area = cv2.contourArea(contour)
            if area < self.minimum_area:
                continue
            x, y, w, h = cv2.boundingRect(contour)
            aspect = h / float(w)
            if 1.2 <= aspect <= 1.75:  # ratio approximatif des cartes Pokémon
                boxes.append((x, y, w, h))

        boxes.sort(key=lambda b: b[0])
        return boxes

    def _extract_text(self, image: "np.ndarray") -> str:
        if pytesseract is None:
            return ""

        pil_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB)) if cv2 is not None else Image.fromarray(image)
        text = pytesseract.image_to_string(
            pil_image,
            lang="eng+fra",
            config="--psm 6",
        )
        return unicodedata.normalize("NFKD", text).strip()

    def _parse_text(self, text: str) -> dict:
        normalized = text.upper()
        local_number = None
        match = re.search(r"(\d{1,3})\s*/\s*(\d{1,3})", normalized)
        if match:
            local_number = match.group(1).zfill(3)

        probable_name = None
        for line in normalized.splitlines():
            line = line.strip()
            if not line or "HP" in line or "/" in line or len(line) < 3:
                continue
            if line.replace(" ", "").isalpha():
                probable_name = line.title()
                break

        set_hint = None
        hint_match = re.search(r"\b([A-Z]{2,4}\d{0,2})\b", normalized)
        if hint_match:
            set_hint = hint_match.group(1)

        return {
            "probable_name": probable_name,
            "local_number": local_number,
            "set_hint": set_hint,
        }
