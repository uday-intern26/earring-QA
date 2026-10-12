"""Jewellery placement validators. Earrings are the implemented type."""

from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel

from app.cv.anchor_geometry import compare_reference, measure_placement
from app.cv.types import EarlobeAnchor, EarringAnchor, PlacementMeasurement, ReferenceComparison, ReferenceVector


class BodyAnchor(BaseModel):
    kind: str
    side: str | None = None
    x: float
    y: float
    confidence: float


class EarAnchor(BodyAnchor):
    kind: str = "ear"


class NeckAnchor(BodyAnchor):
    kind: str = "neck"


class WristAnchor(BodyAnchor):
    kind: str = "wrist"


class FingerAnchor(BodyAnchor):
    kind: str = "finger"


class JewelryPlacementValidator(ABC):
    jewelry_type: str

    @abstractmethod
    def validate(self, body_anchor, jewelry_anchor, *, config: dict) -> PlacementMeasurement:
        raise NotImplementedError


class EarringPlacementValidator(JewelryPlacementValidator):
    jewelry_type = "earring"

    def validate(self, body_anchor, jewelry_anchor, *, config: dict) -> PlacementMeasurement:
        earlobe = body_anchor if isinstance(body_anchor, EarlobeAnchor) else None
        earring = jewelry_anchor if isinstance(jewelry_anchor, EarringAnchor) else None
        return measure_placement(
            earlobe,
            earring,
            minimum_confidence=config["minimum_confidence"],
            pass_threshold=config["pass_threshold"],
            fail_threshold=config["fail_threshold"],
            zone_y_scale=config.get("zone_y_scale", 1.0),
        )

    def compare(self, reference: ReferenceVector | None, actual: PlacementMeasurement, config: dict) -> ReferenceComparison:
        return compare_reference(
            reference,
            actual,
            pass_threshold=config["pass_threshold"],
            fail_threshold=config["fail_threshold"],
        )


def validator_for(jewelry_type: str) -> JewelryPlacementValidator:
    if jewelry_type == "earring":
        return EarringPlacementValidator()
    raise ValueError(
        f"Jewellery type '{jewelry_type}' is not implemented. "
        "The validator interface is ready for necklace, bracelet, ring, and bangle checks."
    )
