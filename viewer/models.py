from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Tuple

Point = Tuple[float, float]


@dataclass(frozen=True)
class ArtifactLabel:
    category: str
    points: Tuple[Point, ...]


@dataclass(frozen=True)
class ImageRecord:
    uid: str
    generator: str
    width: int
    height: int
    image: Any
    labels: Tuple[ArtifactLabel, ...]
