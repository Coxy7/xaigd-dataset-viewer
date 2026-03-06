from __future__ import annotations

from typing import Any, Dict, Iterable, List, Optional

from viewer.constants import ALL_CATEGORIES_OPTION
from viewer.models import ArtifactLabel, ImageRecord


def normalize_label(raw_label: Dict[str, Any]) -> Optional[ArtifactLabel]:
    category = raw_label.get("label")
    raw_points = raw_label.get("points") or []
    if not isinstance(category, str):
        return None

    normalized_points = []
    for raw_point in raw_points:
        if not isinstance(raw_point, (list, tuple)) or len(raw_point) < 2:
            continue
        try:
            x_coord = float(raw_point[0])
            y_coord = float(raw_point[1])
        except (TypeError, ValueError):
            continue
        normalized_points.append((x_coord, y_coord))

    return ArtifactLabel(category=category, points=tuple(normalized_points))


def normalize_record(row: Dict[str, Any]) -> ImageRecord:
    image = row["image"]
    width = int(row.get("width") or image.size[0])
    height = int(row.get("height") or image.size[1])

    labels = []
    for raw_label in row.get("labels") or []:
        if not isinstance(raw_label, dict):
            continue
        normalized_label = normalize_label(raw_label)
        if normalized_label is not None:
            labels.append(normalized_label)

    return ImageRecord(
        uid=str(row.get("uid", "")),
        generator=str(row.get("generator", "")),
        width=width,
        height=height,
        image=image,
        labels=tuple(labels),
    )


def fetch_records(dataset_repo: str, split: str) -> List[ImageRecord]:
    from datasets import load_dataset

    if split not in {"labeled_train", "labeled_test"}:
        raise ValueError(f"Unsupported split: {split}")

    dataset = load_dataset(
        "parquet",
        data_files={split: f"hf://datasets/{dataset_repo}/data/{split}-*.parquet"},
        split=split,
    )
    return [normalize_record(row) for row in dataset]


def filter_labels(record: ImageRecord, category: str) -> List[ArtifactLabel]:
    if category == ALL_CATEGORIES_OPTION:
        return list(record.labels)
    return [label for label in record.labels if label.category == category]


def matching_indices(records: Iterable[ImageRecord], category: str) -> List[int]:
    if category == ALL_CATEGORIES_OPTION:
        return [index for index, _ in enumerate(records)]

    matches = []
    for index, record in enumerate(records):
        if any(label.category == category for label in record.labels):
            matches.append(index)
    return matches
