from __future__ import annotations

import unittest

from PIL import Image

from viewer.constants import ALL_CATEGORIES_OPTION
from viewer.data import filter_labels, matching_indices, normalize_record


class DataNormalizationTests(unittest.TestCase):
    def test_normalize_record_keeps_expected_fields(self) -> None:
        row = {
            "image": Image.new("RGB", (128, 96), "white"),
            "generator": "demo-gen",
            "uid": "sample-1",
            "width": 128,
            "height": 96,
            "labels": [
                {
                    "label": "low-level-edge_shape",
                    "points": [[1, 2], [20.5, 5], [9, 18]],
                },
                {
                    "label": "low-level-texture",
                    "points": [[4, 4], ["bad", 6], [7, 9]],
                },
            ],
        }

        record = normalize_record(row)

        self.assertEqual(record.uid, "sample-1")
        self.assertEqual(record.generator, "demo-gen")
        self.assertEqual((record.width, record.height), (128, 96))
        self.assertEqual(len(record.labels), 2)
        self.assertEqual(record.labels[0].points[1], (20.5, 5.0))
        self.assertEqual(record.labels[1].points, ((4.0, 4.0), (7.0, 9.0)))

    def test_normalize_record_allows_empty_labels(self) -> None:
        row = {
            "image": Image.new("RGB", (32, 32), "white"),
            "generator": "demo-gen",
            "uid": "sample-2",
            "labels": [],
        }

        record = normalize_record(row)

        self.assertEqual(record.labels, ())
        self.assertEqual((record.width, record.height), (32, 32))


class FilterTests(unittest.TestCase):
    def test_filter_labels_returns_all_when_unfiltered(self) -> None:
        record = normalize_record(
            {
                "image": Image.new("RGB", (32, 32), "white"),
                "generator": "demo-gen",
                "uid": "sample-3",
                "labels": [
                    {"label": "low-level-edge_shape", "points": [[1, 1], [2, 2], [3, 3]]},
                    {"label": "low-level-color", "points": [[4, 4], [5, 5], [6, 6]]},
                ],
            }
        )

        labels = filter_labels(record, ALL_CATEGORIES_OPTION)

        self.assertEqual(len(labels), 2)

    def test_matching_indices_only_returns_records_with_selected_category(self) -> None:
        records = [
            normalize_record(
                {
                    "image": Image.new("RGB", (16, 16), "white"),
                    "generator": "g1",
                    "uid": "1",
                    "labels": [{"label": "low-level-edge_shape", "points": [[1, 1], [2, 1], [2, 2]]}],
                }
            ),
            normalize_record(
                {
                    "image": Image.new("RGB", (16, 16), "white"),
                    "generator": "g2",
                    "uid": "2",
                    "labels": [{"label": "high-level-semantics", "points": [[1, 1], [2, 1], [2, 2]]}],
                }
            ),
            normalize_record(
                {
                    "image": Image.new("RGB", (16, 16), "white"),
                    "generator": "g3",
                    "uid": "3",
                    "labels": [],
                }
            ),
        ]

        labels = filter_labels(records[1], "high-level-semantics")
        matches = matching_indices(records, "high-level-semantics")

        self.assertEqual(len(labels), 1)
        self.assertEqual(matches, [1])


if __name__ == "__main__":
    unittest.main()
